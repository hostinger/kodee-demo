from database.database_calls import postgres_database
from database.database_models.history_table_model import HistoryTable, AuthorType
from database.database_models.events_table_model import EventsTable, EventType
from models.chat.chat_message_input_model import ChatMessage
from models.gpt_function_param_model import DefaultGPTFunctionParams
from models.handler_response_model import HandlerResponse
from redis_services.redis_methods import get_assistant_part_id, get_user_part_id


async def log_user_message_interaction(user_id: str, conversation_id: str, message: ChatMessage) -> None:
    user_part_id = await get_user_part_id(user_id)

    await postgres_database.insert_into_events_table(
        EventsTable(
            conversation_id=conversation_id,
            event_type=EventType.USER,
            payload={"content": message.to_dict()},
            message_part_id=user_part_id,
        )
    )

    await postgres_database.insert_into_history_table(
        HistoryTable(
            conversation_id=conversation_id,
            author_type=AuthorType.USER,
            message=message.content,
            chatbot_label=message.chatbot_label,
            message_part_id=user_part_id,
        )
    )


async def log_chatbot_response_interaction(
    user_id: str, conversation_id: str, chatbot_response: HandlerResponse
) -> None:
    assistant_part_id = await get_assistant_part_id(user_id)

    await postgres_database.insert_into_events_table(
        EventsTable(
            conversation_id=conversation_id,
            event_type=EventType.ASSISTANT,
            payload={"content": chatbot_response.to_dict()},
            message_part_id=assistant_part_id,
        )
    )

    await postgres_database.insert_into_history_table(
        HistoryTable(
            conversation_id=conversation_id,
            author_type=AuthorType.ASSISTANT,
            message=chatbot_response.message,
            chatbot_label=chatbot_response.chatbot_label,
            message_part_id=assistant_part_id,
        )
    )


async def insert_function_log(data: DefaultGPTFunctionParams, message_payload: dict):
    await postgres_database.insert_into_events_table(
        EventsTable(
            conversation_id=data.conversation_id,
            event_type=EventType.FUNCTION_LOG,
            message_part_id=await get_assistant_part_id(data.user_id),
            payload={"content": message_payload},
        )
    )
