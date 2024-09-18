from pydantic import BaseModel


class ChatRestartInputModel(BaseModel):
    user_id: str
