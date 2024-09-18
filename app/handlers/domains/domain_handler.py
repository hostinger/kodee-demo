import asyncio
import logging
import os
import traceback
from typing import List, Union
from fastapi import HTTPException, status
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletion
from database.database_calls import postgres_database
from database.database_models.events_table_model import EventsTable, EventType
from handlers.base_handler import BaseChatHandler
from api.external.gpt_clients.gpt_enums import (
    GPTActionNames,
    GPTTeamNames,
    GPTChatbotNames,
    GPTTemperature,
)
from api.external.gpt_clients.openai.openai_enums import OpenAIModel
from helpers.tenacity_retry_strategies import openai_tools_calling_retry_strategy
from helpers.custom_exceptions import InvalidGPTResponseException
from models.handler_config_model import HandlerConfigModel
from models.chat.chat_message_input_model import ChatMessage
from models.chat.chat_message_output_model import OutputRole
from models.gpt_function_output_model import GPTFunctionOutput, OutputStatus
from helpers.gpt_helper import (
    decode_json_string,
    build_tool_call_info,
    get_mocked_failed_function_response,
)
from models.handler_response_model import (
    HandlerResponse,
    HandlerResponseStatus,
)
from models.redis_messages_model import RedisMessages
from redis_services.redis_methods import get_assistant_part_id, get_conversation_metadata

logger = logging.getLogger(__name__)

MAX_LOOP_COUNT = 4


class DomainChatHandler(BaseChatHandler):
    functions_dir = os.path.dirname(__file__)

    def __init__(self, handler_config: HandlerConfigModel):
        super().__init__(handler_config)
        self.handoff_support = False

    def get_temperature(self) -> GPTTemperature:
        return GPTTemperature.POINT_FIVE

    async def get_model(self) -> OpenAIModel:
        return OpenAIModel.GPT_4O_2024_08_06

    async def get_system_description(self) -> str:
        system_description = """You are a helpful and empathetic Hostinger AI assistant 
        named Kodee specialized in Domains issues. 
        Additional guidelines:
        Keep your responses short and simple, up to 3 sentences.
        Your answers must be in markdown format."""

        conversation_metadata = await get_conversation_metadata(self.conversation_id, self.user_id)

        if conversation_metadata and conversation_metadata.domain_name:
            system_description += (
                f"\nThe user has provided a domain name: {conversation_metadata.domain_name}. "
                f"Please verify if the user would like to discuss this domain."
            )

        return system_description

    async def handle(self, message: ChatMessage) -> HandlerResponse:
        if self.function_meta is None or self.function_map is None:
            await self.ensure_function_data_loaded()

        gpt_response_message = await self.process_gpt_response()

        if self.handoff_support:
            return HandlerResponse(
                status=HandlerResponseStatus.SUPPORT_HANDOFF,
                message=gpt_response_message,
            )

        return HandlerResponse(status=HandlerResponseStatus.SUCCESS, message=gpt_response_message)

    @openai_tools_calling_retry_strategy
    async def get_gpt_response(self) -> ChatCompletion:
        gpt_response = await self.get_gpt_with_tools_response(
            action_name=GPTActionNames.TOOLS_CALL_DOMAINS_ACTION_NAME,
            team_name=GPTTeamNames.AI,
            chatbot_name=GPTChatbotNames.DOMAIN,
        )

        if not gpt_response:
            self.log_message("GPT failed to generate a response")
            raise InvalidGPTResponseException()

        return gpt_response

    async def process_gpt_response(self) -> Union[str, None]:
        for _ in range(MAX_LOOP_COUNT):
            gpt_response = await self.get_gpt_response()
            gpt_message = gpt_response.choices[0].message

            if gpt_message.tool_calls:
                await self.process_tool_calls(gpt_message.tool_calls)

            if gpt_message.content and not gpt_message.tool_calls:
                return gpt_message.content

        self.log_message(f"GPT failed to provide a string response {MAX_LOOP_COUNT} times in a row")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"GPT Failed to respond {MAX_LOOP_COUNT} times"
        )

    async def process_tool_calls(self, tool_calls: List[ChatCompletionMessageToolCall]) -> None:
        await self.insert_tool_call_into_events_table(tool_calls)

        if not await self.is_gpt_generated_tools_valid(tool_calls):
            return

        tool_call_coroutines = [self.handle_tool_call(tool_call) for tool_call in tool_calls]
        function_results = await asyncio.gather(*tool_call_coroutines, return_exceptions=True)

        aggregated_tool_calls = []
        for tool_call in tool_calls:
            tool_call_info = await build_tool_call_info(tool_call)
            aggregated_tool_calls.append(tool_call_info)

        await self.push_function_response_to_redis(
            RedisMessages(
                role=OutputRole.ASSISTANT,
                tool_calls=aggregated_tool_calls,
            )
        )

        for result in function_results:
            await self.push_function_response_to_redis(result)

    async def handle_tool_call(self, tool_call) -> RedisMessages:
        gpt_function_name = tool_call.function.name
        gpt_arguments = decode_json_string(tool_call.function.arguments)
        default_function_arguments = await self.get_default_gpt_function_params()
        function_to_call = self.function_map.get(gpt_function_name)

        try:
            self.log_message(f"Calling {gpt_function_name} function with {gpt_arguments} arguments.")
            function_response: GPTFunctionOutput = await function_to_call(default_function_arguments, **gpt_arguments)

            self.log_message(f"Function {gpt_function_name} response: {function_response.to_dict()}")
            await postgres_database.insert_into_events_table(
                EventsTable(
                    conversation_id=self.conversation_id,
                    event_type=EventType.FUNCTION_RESPONSE,
                    payload={
                        "content": {
                            **tool_call.function.dict(),
                            **function_response.to_dict(),
                        }
                    },
                    message_part_id=await get_assistant_part_id(self.user_id),
                )
            )

            if function_response.status == OutputStatus.EXIT:
                self.handoff_support = True

            formatted_redis_message = RedisMessages(
                role=OutputRole.TOOL,
                tool_call_id=tool_call.id,
                content=function_response.message,
            )
            return formatted_redis_message
        except Exception as exception:
            tb_str = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            self.log_message(
                "Function call failed",
                function_name=gpt_function_name,
                arguments=gpt_arguments,
                payload=exception,
                traceback=tb_str,
                level=logging.ERROR,
            )
            await postgres_database.insert_into_events_table(
                EventsTable(
                    conversation_id=self.conversation_id,
                    event_type=EventType.FUNCTION_ERROR,
                    payload={
                        "content": {
                            **tool_call.function.dict(),
                            "error_message": str(exception),
                        }
                    },
                    message_part_id=await get_assistant_part_id(self.user_id),
                )
            )
            return await get_mocked_failed_function_response(tool_call.id)
