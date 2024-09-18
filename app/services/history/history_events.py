from typing import Dict
from fastapi import status
from fastapi.responses import JSONResponse
from database.database_calls import postgres_database
from models.history.events_output_model import DatabaseEventTable
from models.history.history_response_model import HistoryAPIResponse, HistoryResponseStatusCode
from utils.logger.logger import Logger

logger = Logger()


async def history_events_service(conversation_id: str) -> Dict | JSONResponse:
    try:
        history_events = await postgres_database.get_events_by_conversation_id(conversation_id)
    except Exception as exception:
        logger.log("Failed fetching events from database", conversation_id=conversation_id, payload=exception)
        return JSONResponse(
            content=HistoryAPIResponse(
                status=HistoryResponseStatusCode.ERROR, error_message="Failed fetching events from database"
            ).convert_to_error_response(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not history_events:
        return JSONResponse(
            content=HistoryAPIResponse(
                status=HistoryResponseStatusCode.ERROR, error_message="Conversation ID not found"
            ).convert_to_error_response(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    parsed_events = [DatabaseEventTable(**event) for event in history_events]

    return HistoryAPIResponse(
        status=HistoryResponseStatusCode.SUCCESS, data=parsed_events
    ).convert_to_success_response()
