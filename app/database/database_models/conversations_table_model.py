from pydantic import BaseModel


class ConversationsTable(BaseModel):
    user_id: str
    conversation_id: str
