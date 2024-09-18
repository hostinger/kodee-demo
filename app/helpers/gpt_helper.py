import json
from typing import Dict, Any, List, Union
from openai.types.chat import ChatCompletionMessageToolCall
from api.external.gpt_clients.gpt_enums import GPTRole, GPTTemperature
from models.chat.chat_message_input_model import InputRole
from models.redis_messages_model import RedisMessages
from redis_services.redis_message_formatter import filter_history_messages
from models.chat.chat_message_output_model import OutputRole
from utils.logger.logger import Logger
from redis_services.redis_methods import fetch_entire_conversation_history

logger = Logger()


def decode_json_string(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.log("Error decoding JSON string", payload=e)
        return None


async def get_conversation_history_with_system_prompt(system_description: str, conversation_id: str) -> list[dict]:
    historical_messages = await filter_history_messages(
        await fetch_entire_conversation_history(conversation_id=conversation_id),
        exclude_fields=["tool_calls"],
        exclude_if_field_matches={"role": OutputRole.TOOL},
    )
    return [{"role": GPTRole.SYSTEM, "content": system_description}] + historical_messages


async def trim_to_earliest_user_message(history_data: List[Dict]) -> List[Dict]:
    relevant_start_index = 0
    for i in range(len(history_data)):
        if history_data[i].get("role") == InputRole.USER:
            relevant_start_index = i
            break

    trimmed_history_data = history_data[relevant_start_index:]

    return trimmed_history_data


async def build_tool_call_info(tool_call: ChatCompletionMessageToolCall) -> Dict[str, Any]:
    return {
        "id": tool_call.id,
        "type": "function",
        "function": tool_call.function.model_dump(),
    }


async def get_mocked_failed_function_response(tool_call_id) -> RedisMessages:
    return RedisMessages(
        role=OutputRole.TOOL,
        tool_call_id=tool_call_id,
        content="Function has faced an error. Do not use this function at the moment.",
    )


def return_temperature_float_value(temperature: Union[GPTTemperature, float]) -> float:
    if isinstance(temperature, GPTTemperature):
        return temperature.value
    elif isinstance(temperature, float):
        return temperature
    else:
        raise ValueError("GPT Temperature must be a GPTTemperature enum member or a float.")
