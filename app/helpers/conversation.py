from typing import List
from uuid import uuid4
from api.external.gpt_clients.gpt_enums import GPTRole
from database.database_calls import postgres_database
from database.database_models.conversations_table_model import ConversationsTable
from redis_services.redis_methods import set_conversation_id


async def create_new_conversation(user_id: str) -> str:
    conversation_id = str(uuid4())

    await set_conversation_id(user_id, conversation_id)

    await postgres_database.insert_into_conversations_table(
        ConversationsTable(user_id=user_id, conversation_id=conversation_id)
    )

    return conversation_id


def filter_out_system_messages(messages: List[dict]) -> List[dict]:
    filtered_messages = [msg for msg in messages if msg.get("role") != GPTRole.SYSTEM]
    return filtered_messages
