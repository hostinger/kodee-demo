from api.external.gpt_clients.gpt_enums import GPTTeamNames, GPTTemperature, GPTRole
from api.external.gpt_clients.gpt_enums import GPTResponseFormat, GPTActionNames
from helpers.tenacity_retry_strategies import handoff_retry_strategy, handoff_support_message_retry_strategy
from helpers.custom_exceptions import InvalidGPTResponseException
from utils.logger.logger import Logger
from helpers.gpt_helper import decode_json_string, get_conversation_history_with_system_prompt
from router.gpt_router_prompts import get_is_handoff_needed_prompt, get_handoff_message_prompt
import logging
from api.external.gpt_clients.openai.openai_client import OpenAIChat
from api.external.gpt_clients.openai.openai_enums import OpenAIModel


openai_client = OpenAIChat()
logger = Logger()


@handoff_retry_strategy
async def is_seeking_human_assistance(conversation_id: str, user_id: str) -> bool:
    messages = await get_conversation_history_with_system_prompt(get_is_handoff_needed_prompt(), conversation_id)
    gpt_response = await openai_client.get_response(
        messages=messages,
        action_name=GPTActionNames.HANDOFF_DECIDER_ACTION,
        team_name=GPTTeamNames.AI,
        model=OpenAIModel.GPT_4O_2024_08_06,
        response_format=GPTResponseFormat.JSON,
        temperature=GPTTemperature.ZERO,
    )

    if not gpt_response:
        logger.log(
            "is_seeking_human_assistance: GPT failed to generate a response.",
            conversation_id=conversation_id,
            user_id=user_id,
            level=logging.WARNING,
        )
        raise InvalidGPTResponseException("GPT failed to generate a response.")

    decoded_handoff_boolean = decode_json_string(gpt_response.choices[0].message.content)
    if not decoded_handoff_boolean:
        logger.log(
            "is_seeking_human_assistance: GPT response was not valid JSON.",
            conversation_id=conversation_id,
            user_id=user_id,
            level=logging.WARNING,
            payload=gpt_response.choices[0].message.content,
        )
        raise InvalidGPTResponseException("GPT response was not valid JSON.")

    decoded_handoff_boolean = decoded_handoff_boolean.get("is_seeking_human_assistance", {})

    if isinstance(decoded_handoff_boolean, int):
        decoded_handoff_boolean = bool(decoded_handoff_boolean)
    elif isinstance(decoded_handoff_boolean, str):
        if decoded_handoff_boolean.lower() in ["true", "false"]:
            decoded_handoff_boolean = decoded_handoff_boolean.lower() == "true"

    if not isinstance(decoded_handoff_boolean, bool):
        logger.log(
            "is_seeking_human_assistance: GPT response was not a boolean",
            conversation_id=conversation_id,
            user_id=user_id,
            level=logging.WARNING,
            payload=decoded_handoff_boolean,
        )
        raise InvalidGPTResponseException("GPT response was not a boolean")

    return decoded_handoff_boolean


@handoff_support_message_retry_strategy
async def get_handoff_response_message(conversation_id: str, user_id: str) -> str:
    gpt_response = await openai_client.get_response(
        messages=[{"role": GPTRole.SYSTEM, "content": get_handoff_message_prompt()}],
        action_name=GPTActionNames.HANDOFF_MESSAGE_ACTION,
        team_name=GPTTeamNames.AI,
        model=OpenAIModel.GPT_4O_2024_08_06,
        temperature=GPTTemperature.ZERO,
    )

    if not gpt_response:
        logger.log(
            "get_handoff_response_message: GPT failed to generate a response.",
            conversation_id=conversation_id,
            user_id=user_id,
            level=logging.WARNING,
        )
        raise InvalidGPTResponseException("GPT failed to generate a response.")

    return gpt_response.choices[0].message.content
