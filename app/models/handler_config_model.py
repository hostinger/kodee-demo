from pydantic import BaseModel


class HandlerConfigModel(BaseModel):
    user_id: str
    conversation_id: str
