from typing import Optional
from pydantic import BaseModel


class ChatbotMetadata(BaseModel):
    domain_name: Optional[str] = None


class ChatInitializationInputModel(BaseModel):
    user_id: str
    metadata: Optional[ChatbotMetadata] = None
