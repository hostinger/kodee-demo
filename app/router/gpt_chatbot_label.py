from api.external.gpt_clients.gpt_enums import GPTResponseFormat, GPTActionNames, GPTTeamNames, GPTTemperature
from database.database_calls import postgres_database
from database.database_models.events_table_model import EventsTable, EventType
from helpers.tenacity_retry_strategies import chatbot_label_retry_strategy
from helpers.custom_exceptions import InvalidGPTResponseException
from redis_services.redis_methods import get_assistant_part_id
from utils.logger.logger import Logger
from helpers.gpt_helper import decode_json_string, get_conversation_history_with_system_prompt
from models.chat.chat_message_input_model import ChatbotLabel
from router.gpt_router_prompts import get_router_prompt
from api.external.gpt_clients.openai.openai_enums import OpenAIModel
from api.external.gpt_clients.openai.openai_client import OpenAIChat

openai_client = OpenAIChat()
logger = Logger()


async def is_chatbot_label_valid(chatbot_label: str) -> bool:
    return any(chatbot_label == label for label in ChatbotLabel)


@chatbot_label_retry_strategy
async def generate_chatbot_label(conversation_id: str, user_id: str) -> ChatbotLabel:
    system_description = get_router_prompt()
    messages = await get_conversation_history_with_system_prompt(system_description, conversation_id)

    gpt_response = await openai_client.get_response(
        messages=messages,
        model=OpenAIModel.GPT_4O_2024_08_06,
        response_format=GPTResponseFormat.JSON,
        temperature=GPTTemperature.ZERO,
        action_name=GPTActionNames.CHATBOT_LABEL_ACTION_NAME,
        team_name=GPTTeamNames.AI,
    )

    if not gpt_response:
        logger.log("GPT failed to generate a response.", conversation_id=conversation_id)
        raise InvalidGPTResponseException("GPT failed to generate a response.")

    decoded_chatbot_label = decode_json_string(gpt_response.choices[0].message.content)
    if not decoded_chatbot_label:
        logger.log("GPT response was not valid JSON.", conversation_id=conversation_id)
        raise InvalidGPTResponseException("GPT response was not valid JSON.")

    decoded_chatbot_label = decoded_chatbot_label.get("team_label", {})

    if not await is_chatbot_label_valid(decoded_chatbot_label):
        logger.log("GPT response was not a valid chatbot label.", conversation_id=conversation_id)
        raise InvalidGPTResponseException("GPT response was not a valid chatbot label.")

    await postgres_database.insert_into_events_table(
        EventsTable(
            conversation_id=conversation_id,
            event_type=EventType.CHATBOT_LABEL,
            payload={"content": {"message": "Setting active chatbot label for conversation",
                                 "label": decoded_chatbot_label}},
            message_part_id=await get_assistant_part_id(user_id),
        )
    )

    return decoded_chatbot_label
