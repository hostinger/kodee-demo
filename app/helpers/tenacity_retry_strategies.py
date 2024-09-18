from tenacity import retry, stop_after_attempt, retry_if_exception_type
from helpers.custom_exceptions import InvalidGPTResponseException
from fastapi import HTTPException, status

from models.chat.chat_message_input_model import ChatbotLabel
from router.gpt_router_prompts import DEFAULT_HANDOFF_MESSAGE

TENACITY_RETRY_ATTEMPTS = 3
PART_ID_ERROR_INDICATOR = "ERROR_RETRIEVING_PART_ID"

redis_retry_strategy = retry(
    stop=stop_after_attempt(TENACITY_RETRY_ATTEMPTS),
    retry_error_callback=lambda retry_state: None,
)

redis_part_id_retry_strategy = retry(
    stop=stop_after_attempt(TENACITY_RETRY_ATTEMPTS),
    retry_error_callback=lambda retry_state: PART_ID_ERROR_INDICATOR,
)

openai_retry_strategy = retry(
    stop=stop_after_attempt(TENACITY_RETRY_ATTEMPTS),
    retry_error_callback=lambda retry_state: None,
)

openai_tools_calling_retry_strategy = retry(
    stop=stop_after_attempt(TENACITY_RETRY_ATTEMPTS),
    retry=retry_if_exception_type(InvalidGPTResponseException),
    retry_error_callback=lambda retry_state: raise_gpt_exception(),
)

handoff_retry_strategy = retry(
    stop=stop_after_attempt(TENACITY_RETRY_ATTEMPTS),
    retry_error_callback=lambda retry_state: True,
)

handoff_support_message_retry_strategy = retry(
    stop=stop_after_attempt(TENACITY_RETRY_ATTEMPTS),
    retry=retry_if_exception_type(InvalidGPTResponseException),
    retry_error_callback=lambda retry_state: DEFAULT_HANDOFF_MESSAGE,
)

postgresql_retry_strategy = retry(
    stop=stop_after_attempt(3),
    retry_error_callback=lambda retry_state: None,
)

chatbot_label_retry_strategy = retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(InvalidGPTResponseException),
    retry_error_callback=lambda retry_state: ChatbotLabel.OUT_OF_SCOPE,
)


def raise_gpt_exception():
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="GPT Failed to respond")
