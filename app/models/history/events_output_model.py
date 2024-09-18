import json
from typing import Dict
from pydantic import BaseModel, field_validator
from datetime import datetime


class DatabaseEventTable(BaseModel):
    id: int
    conversation_id: str
    event_type: str
    payload: str | Dict
    message_part_id: str
    created_at: datetime

    @field_validator("payload")
    def parse_json_to_dict(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(f"Unable to parse 'payload' as JSON: {e}")
        return v
