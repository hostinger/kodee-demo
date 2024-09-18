import json
from enum import StrEnum
from pydantic import BaseModel, field_validator
from typing import Any, Dict


class EventType(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL_CALL = "tool_call"
    FUNCTION_RESPONSE = "function_response"
    FUNCTION_ERROR = "function_error"
    FUNCTION_LOG = "function_log"
    CHATBOT_LABEL = "chatbot_label"


class EventsTable(BaseModel):
    conversation_id: str
    event_type: EventType
    payload: Dict
    message_part_id: str

    @field_validator("payload")
    def serialize_payload(cls, v: Any) -> str:
        return json.dumps(v, ensure_ascii=False)
