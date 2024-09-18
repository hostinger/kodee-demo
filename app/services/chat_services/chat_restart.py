from fastapi import HTTPException, status
from helpers.conversation import create_new_conversation
from utils.logger.logger import Logger
from models.chat.chat_initialization_output_model import ChatInitializationOutputModel
from redis_services.redis_methods import (
    get_conversation_id,
    delete_conversation,
    get_conversation_metadata,
    set_conversation_metadata,
)

logger = Logger()


async def restart_conversation_service(user_id: str) -> dict:
    current_conversation_id = await get_conversation_id(user_id)
    if not current_conversation_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer has no active conversations")

    current_conversation_metadata = await get_conversation_metadata(current_conversation_id, user_id)

    await delete_conversation(user_id, current_conversation_id)

    new_conversation_id = await create_new_conversation(user_id)
    await set_conversation_metadata(new_conversation_id, current_conversation_metadata)

    return ChatInitializationOutputModel(conversation_id=new_conversation_id, history=[]).model_dump(exclude_none=True)
