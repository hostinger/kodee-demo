from enum import StrEnum, Enum


class GPTTemperature(float, Enum):
    ZERO = 0
    POINT_ONE = 0.1
    POINT_TWO = 0.2
    POINT_THREE = 0.3
    POINT_FOUR = 0.4
    POINT_FIVE = 0.5
    POINT_SIX = 0.6
    POINT_SEVEN = 0.7
    POINT_EIGHT = 0.8
    POINT_NINE = 0.9
    ONE = 1


class GPTRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class GPTResponseFormat(StrEnum):
    JSON = "json_object"
    TEXT = "text"


class GPTActionNames(StrEnum):
    HANDOFF_DECIDER_ACTION = "handoff_decider_action"
    HANDOFF_MESSAGE_ACTION = "handoff_message_action"
    CHATBOT_LABEL_ACTION_NAME = "chatbot_label_action"
    TOOLS_CALL_DOMAINS_ACTION_NAME = "tools_call_domains_action"
    TOOLS_CALL_OOS_ACTION_NAME = "tools_call_oos_action"


class GPTTeamNames(StrEnum):
    AI = "ai"


class GPTChatbotNames(StrEnum):
    DOMAIN = "domain"
    OUT_OF_SCOPE = "out_of_scope"
