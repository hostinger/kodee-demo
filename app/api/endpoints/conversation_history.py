from fastapi import APIRouter, Query
from services.history.history_events import history_events_service
from services.history.history_messages import history_messages_service

history_router = APIRouter()


@history_router.get("/events")
async def retrieve_events_by_conversation_id(
    conversation_id: str = Query(..., description="The conversation ID to retrieve events for"),
):
    return await history_events_service(conversation_id)


@history_router.get("/messages")
async def retrieve_messages_by_conversation_id(
    conversation_id: str = Query(..., description="The conversation ID to retrieve messages for"),
):
    return await history_messages_service(conversation_id)
