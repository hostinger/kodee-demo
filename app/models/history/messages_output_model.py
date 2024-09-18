from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DatabaseHistoryTable(BaseModel):
    id: int
    conversation_id: str
    author_type: str
    message: str
    chatbot_label: Optional[str] = None
    message_part_id: Optional[str] = None
    created_at: datetime
