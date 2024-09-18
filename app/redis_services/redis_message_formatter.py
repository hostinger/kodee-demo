from typing import List, Optional, Dict
from models.redis_messages_model import RedisMessages


async def filter_history_messages(
    history_data: List[RedisMessages],
    exclude_fields: Optional[List[str]] = None,
    exclude_if_field_matches: Optional[Dict[str, str]] = None,
) -> List[Dict]:
    """
    Filters out messages from history_data based on the following criteria:
    - Removes dictionaries where any specified field is not None (if exclude_fields is provided).
    - Removes entire dictionary if a specified field value matches a given value (if exclude_if_field_matches is provided).
    - Removes None fields from the dictionaries.
    """
    filtered_messages = []
    for message in history_data:
        if exclude_fields and any(message.get(field) is not None for field in exclude_fields):
            continue

        if exclude_if_field_matches and any(
            message.get(field) == value for field, value in exclude_if_field_matches.items()
        ):
            continue

        filtered_msg = {key: value for key, value in message.items() if value is not None}

        if filtered_msg:
            filtered_messages.append(filtered_msg)

    return filtered_messages
