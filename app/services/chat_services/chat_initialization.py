from typing import List, Dict
from helpers.conversation import create_new_conversation
from redis_services.redis_message_formatter import filter_history_messages
from models.chat.chat_initialization_input_model import ChatInitializationInputModel
from models.chat.chat_message_output_model import OutputRole
from models.chat.chat_initialization_output_model import ChatInitializationOutputModel
from redis_services.redis_methods import (
    get_conversation_id,
    refresh_conversation_expiration,
    set_conversation_metadata,
    fetch_entire_conversation_history,
    refresh_conversation_messages_expiration,
)


async def chat_initialization_service(user_id: str, request: ChatInitializationInputModel) -> dict:
    conversation_id = await handle_conversation_id(user_id)

    await set_conversation_metadata(conversation_id, request.metadata)

    history = await fetch_and_filter_history(conversation_id)

    return ChatInitializationOutputModel(conversation_id=conversation_id, history=history).model_dump(exclude_none=True)


async def handle_conversation_id(user_id: str) -> str:
    conversation_id = await get_conversation_id(user_id)

    if conversation_id:
        await refresh_conversation_expiration(user_id)
        await refresh_conversation_messages_expiration(conversation_id)
    else:
        conversation_id = await create_new_conversation(user_id)

    return conversation_id


async def fetch_and_filter_history(conversation_id: str) -> List[Dict]:
    return await filter_history_messages(
        await fetch_entire_conversation_history(conversation_id=conversation_id),
        exclude_fields=["tool_calls"],
        exclude_if_field_matches={"role": OutputRole.TOOL},
    )
