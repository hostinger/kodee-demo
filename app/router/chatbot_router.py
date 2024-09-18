from handlers.domains.domain_handler import DomainChatHandler
from handlers.out_of_scope.out_of_scope_handler import OutOfScopeChatHandler
from models.chat.chat_message_input_model import ChatMessage, ChatbotLabel
from models.chat.chat_message_output_model import OutputChatbotLabel
from models.handler_config_model import HandlerConfigModel
from router.gpt_chatbot_label import generate_chatbot_label
from utils.logger.logger import Logger
from models.handler_response_model import HandlerResponse, HandlerResponseStatus
from router.support_handoff_decider import is_seeking_human_assistance, get_handoff_response_message

logger = Logger()
MAXIMUM_OUT_OF_SCOPE_ATTEMPTS = 3


class ChatbotRouter:
    def __init__(self):
        self.handler_classes = {
            ChatbotLabel.DOMAIN: DomainChatHandler,
            ChatbotLabel.OUT_OF_SCOPE: OutOfScopeChatHandler,
        }

        self.chatbot_label_mapping = {
            ChatbotLabel.DOMAIN: OutputChatbotLabel.DOMAIN_BOT,
            ChatbotLabel.OUT_OF_SCOPE: OutputChatbotLabel.OUT_OF_SCOPE_BOT,
        }

    async def route(self, message: ChatMessage, handler_config: HandlerConfigModel) -> HandlerResponse:
        if await is_seeking_human_assistance(handler_config.conversation_id, handler_config.user_id):
            return HandlerResponse(
                status=HandlerResponseStatus.SUPPORT_HANDOFF,
                message=await get_handoff_response_message(handler_config.conversation_id, handler_config.user_id),
                chatbot_label=OutputChatbotLabel.SUPPORT_HANDOFF_BOT,
            )

        message.chatbot_label = await generate_chatbot_label(handler_config.conversation_id, handler_config.user_id)

        handler_class = self.handler_classes.get(message.chatbot_label)
        response = await handler_class(handler_config).handle(message)
        response.chatbot_label = self.chatbot_label_mapping.get(message.chatbot_label)
        return response
