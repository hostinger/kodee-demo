from enum import StrEnum, IntEnum


class RedisPrefix(StrEnum):
    CONVERSATION_KEY_PREFIX = "user_conversation:"
    CONVERSATION_MESSAGES_KEY_PREFIX = "conversation_messages:"
    CONVERSATION_METADATA_KEY_PREFIX = "conversation_metadata:"
    CHATBOT_LABEL_KEY_PREFIX = "chatbot_label:"
    MUST_HANDOFF_CONVERSATION_KEY_PREFIX = "must_handoff_conversation:"
    MESSAGE_PART_ID_KEY_PREFIX = "message_part_ids:"


class RedisExpiration(IntEnum):
    FIVE_MINUTES = 300
    ONE_HOUR = 3600
    ONE_DAY = 86400
    ONE_WEEK = 604800
