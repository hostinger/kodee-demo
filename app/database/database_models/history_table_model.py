from enum import StrEnum
from pydantic import BaseModel


class AuthorType(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class HistoryTable(BaseModel):
    conversation_id: str
    author_type: AuthorType
    message: str
    chatbot_label: str
    message_part_id: str
