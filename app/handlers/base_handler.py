from abc import ABC, abstractmethod
from typing import List, Dict
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from database.database_calls import postgres_database
from database.database_models.events_table_model import EventsTable, EventType
from api.external.gpt_clients.gpt_enums import GPTRole, GPTTeamNames, GPTActionNames, GPTChatbotNames, GPTTemperature
from helpers.gpt_helper import trim_to_earliest_user_message
from models.handler_config_model import HandlerConfigModel
from redis_services.redis_message_formatter import filter_history_messages
from models.gpt_function_param_model import DefaultGPTFunctionParams
from models.handler_response_model import HandlerResponse
from models.redis_messages_model import RedisMessages
from utils.logger.logger import Logger
from redis_services.redis_methods import (
    push_message_to_redis,
    get_assistant_part_id,
    fetch_latest_conversation_messages,
)
from models.chat.chat_message_input_model import ChatMessage
from utils.get_handler_functions import compile_function_metadata, compile_function_map
from api.external.gpt_clients.openai.openai_client import OpenAIChat
from api.external.gpt_clients.openai.openai_enums import OpenAIModel

logger = Logger()
openai_client = OpenAIChat()


class BaseChatHandler(ABC):
    functions_dir = None
    function_meta = None
    function_map = None

    def __init__(self, handler_config: HandlerConfigModel):
        self.user_id = handler_config.user_id
        self.conversation_id = handler_config.conversation_id

    @classmethod
    async def ensure_function_data_loaded(cls) -> None:
        if cls.function_meta is None:
            cls.function_meta = await compile_function_metadata(cls.functions_dir)
        if cls.function_map is None:
            cls.function_map = await compile_function_map(cls.functions_dir)

    @abstractmethod
    async def get_model(self) -> OpenAIModel:
        pass

    @abstractmethod
    def get_temperature(self) -> GPTTemperature:
        pass

    @abstractmethod
    async def get_system_description(self) -> str:
        pass

    @abstractmethod
    async def handle(self, message: ChatMessage) -> HandlerResponse:
        pass

    def log_message(self, message_content: str, **kwargs) -> None:
        log_fields = {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "handler": self.__class__.__name__,
            **kwargs,
        }
        logger.log(message_content, **log_fields)

    async def get_latest_conversation_messages_history(self) -> List[Dict]:
        conversation_messages = await filter_history_messages(
            await fetch_latest_conversation_messages(conversation_id=self.conversation_id)
        )

        return await trim_to_earliest_user_message(conversation_messages)

    async def format_chat_history_with_prompt(self) -> List[Dict]:
        return [
            {"role": GPTRole.SYSTEM, "content": await self.get_system_description()}
        ] + await self.get_latest_conversation_messages_history()

    async def push_function_response_to_redis(self, message: RedisMessages) -> None:
        return await push_message_to_redis(user_id=self.user_id, conversation_id=self.conversation_id, message=message)

    async def get_gpt_with_tools_response(
        self, action_name: GPTActionNames, team_name: GPTTeamNames, chatbot_name: GPTChatbotNames
    ) -> ChatCompletion:
        return await openai_client.get_response_with_tools(
            messages=await self.format_chat_history_with_prompt(),
            action_name=action_name,
            team_name=team_name,
            chatbot_name=chatbot_name,
            tools=self.function_meta,
            model=await self.get_model(),
            temperature=self.get_temperature(),
        )

    async def insert_tool_call_into_events_table(self, tool_calls: List[ChatCompletionMessageToolCall]) -> None:
        await postgres_database.insert_into_events_table(
            EventsTable(
                conversation_id=self.conversation_id,
                event_type=EventType.TOOL_CALL,
                payload={
                    "content": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {"arguments": tool_call.function.arguments, "name": tool_call.function.name},
                        }
                        for tool_call in tool_calls
                    ],
                },
                message_part_id=await get_assistant_part_id(self.user_id),
            )
        )

    async def get_default_gpt_function_params(self) -> DefaultGPTFunctionParams:
        return DefaultGPTFunctionParams(
            conversation_id=self.conversation_id,
            user_id=self.user_id,
        )

    async def is_gpt_generated_tools_valid(self, tool_calls: List[ChatCompletionMessageToolCall]) -> bool:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            if not self.function_map.get(function_name):
                self.log_message(f"GPT generated function {function_name} not found.")
                return False
        return True
