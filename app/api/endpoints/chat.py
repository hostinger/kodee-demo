from fastapi import APIRouter
from models.chat.chat_initialization_input_model import ChatInitializationInputModel
from models.chat.chat_message_input_model import ChatMessage
from models.chat.chat_message_output_model import ConversationMessagesOutput
from models.chat.chat_restart_input_model import ChatRestartInputModel
from services.chat_services.chat_respond import chat_service
from services.chat_services.chat_initialization import chat_initialization_service
from services.chat_services.chat_restart import restart_conversation_service

chat_router = APIRouter()


@chat_router.post("/initialization")
async def chat_initialization(
    request: ChatInitializationInputModel,
):
    return await chat_initialization_service(request.user_id, request)


@chat_router.post("/respond")
async def chat_respond(
    request: ChatMessage,
) -> ConversationMessagesOutput:
    return await chat_service(request)


@chat_router.post("/restart")
async def chat_restart(
    request: ChatRestartInputModel,
):
    return await restart_conversation_service(request.user_id)
