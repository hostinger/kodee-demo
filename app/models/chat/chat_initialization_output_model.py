from typing import List
from pydantic import BaseModel


class ChatInitializationOutputModel(BaseModel):
    conversation_id: str
    history: List[dict]
