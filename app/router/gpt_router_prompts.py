from models.chat.chat_message_input_model import ChatbotLabel

# This message is used, if GPT failed to generate a handoff message
DEFAULT_HANDOFF_MESSAGE = (
    "I’m now redirecting you to our Customer Success Team for further assistance. "
    "A specialist will join our conversation shortly. They’ll have access to our chat history, "
    "so there's no need for you to repeat anything previously mentioned, unless you'd like to "
    "provide additional details."
)

# This message is used, if GPT failed to generate a handoff clarify message
DEFAULT_HANDOFF_CLARIFY_MESSAGE = "Could you please provide more details about the issue you're facing?"

CHATBOT_DESCRIPTIONS = {
    ChatbotLabel.DOMAIN: """
Domain purchase/registration: domain pricing, TLDs, domain extensions, free domain, registration requirements, domain 
activation/validation; domain management: DNS settings, nameservers, propagation, domain setup, domain contact details, 
suspended domain, wrong domain, misspelled domain, domain renewal, 
domain expiration; domain functionality: domain pointing, connect domain, redirects, domain parking, adding a 
domain to hosting plan, park domain, preview domain, cancel/delete domain; 
subdomains; transfer from another provider, transfer out, domain lock; moving a domain to a different user account. 
""",
    ChatbotLabel.OUT_OF_SCOPE: """
Any questions/issue that do not relate to the above topics, conversational elements, chit chat.
""",
}


def get_router_prompt() -> str:
    prompt_lines = [
        """You need to select 1 team based on conversation messages, focusing on the user's latest message.,
        This team will further assist the customer, and they are specializing only in 1 topic,
        Below are possible team names, and explanations, in what they are specializing:""",
    ]

    for chatbot_label, description in CHATBOT_DESCRIPTIONS.items():
        prompt_lines.append(f'"{chatbot_label}": {description.strip()}')

    prompt_lines.append(
        """Respond in JSON format with team_label field, select the most capable team to help the user based
        on the conversation history. You MUST respond as in this example: {"team_label": "team_name"}"""
    )

    return "\n".join(prompt_lines)


def get_is_handoff_needed_prompt() -> str:
    return """Based on the received customer conversation, you need to decide if the customer is explicitly asking to contact
    a real human, agent or specialist. A simple mention of "support" or descriptions of problems/issues, such as "website doesn't work",
    does not necessarily mean that the user is seeking assistance from an agent.
    Only return True if the customer clearly indicates that they want to talk to a human or a live agent. Examples include:
    "I want live chat", "I want to talk to a human", "I need human assistance", or similar phrases.
    Additionally, if the customer is using swear words, cursing, or inappropriate language, this should also be interpreted
    as seeking human assistance, and you should return True. In other cases, return False.
    Respond in JSON format with the field is_seeking_human_assistance. You can only return True or False.
    Output example:
    {"is_seeking_human_assistance": False}"""


def get_handoff_message_prompt() -> str:
    return """Below between triple dashes is the message that needs to be rephrased and translated to user language language:
    
    ---
    I’m now redirecting you to our Customer Success Team for further assistance.
    A specialist will join our conversation shortly. They’ll have access to our chat history,
    so there's no need for you to repeat anything previously mentioned, unless you'd like to
    provide additional details.
    ---
    
    You must follow rules:
    1. Do not change the context of the message. Don't add extra details to the message.
    3. You must respond only with this sentence.
    """


def get_handoff_clarify_prompt() -> str:
    return """You are a Hostinger AI Assistant. Your task is to ask the user to provide more details about their issue.
    Request additional specifics about the problem they're facing.
    You must follow 2 rules:
    1. Do not assist the user in any way. Just respond with a message asking for more details about the problem they are facing.
    2. Respond in the same language as user used in the conversation.
    User will be automatically redirected to a specific Customer Success Team after they provide more information.
    """
