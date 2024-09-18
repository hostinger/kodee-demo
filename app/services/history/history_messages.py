from typing import Dict
from fastapi import status
from fastapi.responses import JSONResponse
from database.database_calls import postgres_database
from models.history.messages_output_model import DatabaseHistoryTable
from models.history.history_response_model import HistoryAPIResponse, HistoryResponseStatusCode
from utils.logger.logger import Logger

logger = Logger()


async def history_messages_service(conversation_id: str) -> Dict | JSONResponse:
    try:
        history_messages = await postgres_database.get_history_by_conversation_id(conversation_id)
    except Exception as exception:
        logger.log("Failed fetching messages from database", conversation_id=conversation_id, payload=exception)
        return JSONResponse(
            content=HistoryAPIResponse(
                status=HistoryResponseStatusCode.ERROR, error_message="Failed fetching messages from database"
            ).convert_to_error_response(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not history_messages:
        return JSONResponse(
            content=HistoryAPIResponse(
                status=HistoryResponseStatusCode.ERROR, error_message="Conversation ID not found"
            ).convert_to_error_response(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    parsed_events = [DatabaseHistoryTable(**event) for event in history_messages]

    return HistoryAPIResponse(
        status=HistoryResponseStatusCode.SUCCESS, data=parsed_events
    ).convert_to_success_response()
