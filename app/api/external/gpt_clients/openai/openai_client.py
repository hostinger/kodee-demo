from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from api.external.gpt_clients.cost_calculation_helpers import calculate_openai_cost
from api.external.gpt_clients.gpt_enums import (
    GPTResponseFormat,
    GPTChatbotNames,
    GPTTeamNames,
    GPTActionNames,
    GPTTemperature,
)
from api.external.gpt_clients.openai.openai_enums import OpenAIModel
from helpers.conversation import filter_out_system_messages
from helpers.gpt_helper import return_temperature_float_value
from helpers.tenacity_retry_strategies import openai_retry_strategy
from utils.logger.logger import Logger
from utils.env_constants import OPENAI_API_KEY
from time import time
import logging

TIMEOUT_SECONDS = 45
DEFAULT_MAX_TOKENS = 2048
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=TIMEOUT_SECONDS)

logger = Logger()


class OpenAIChat:
    @openai_retry_strategy
    async def get_response(
            self,
            messages: List[dict],
            model: OpenAIModel,
            action_name: GPTActionNames,
            team_name: GPTTeamNames,
            chatbot_name: Optional[GPTChatbotNames] = None,
            response_format: GPTResponseFormat = GPTResponseFormat.TEXT,
            temperature: GPTTemperature = GPTTemperature.POINT_FIVE,
            max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> ChatCompletion | None:
        try:
            start_time = time()

            response = await openai_client.chat.completions.create(
                messages=messages,
                model=model,
                response_format={"type": response_format},
                timeout=TIMEOUT_SECONDS,
                temperature=return_temperature_float_value(temperature),
                max_tokens=max_tokens,
            )

            process_time = time() - start_time
            total_cost = calculate_openai_cost(model, response.usage.prompt_tokens, response.usage.completion_tokens)

            logger.log(
                "OpenAI Token usage",
                team_name=team_name,
                action_name=action_name,
                chatbot_name=chatbot_name,
                model=model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                requests=self.get_response.retry.statistics["attempt_number"],
                response_time=process_time,
                cost=total_cost,
            )

            return response
        except Exception as e:
            logger.log(
                "GPT Exception occurred",
                level=logging.WARNING,
                service="OpenAI",
                payload=str(e),
                model_name=model,
                action_name=action_name,
                method_name="get_response",
                team_name=team_name,
                chatbot_name=chatbot_name,
                exception_type=type(e).__name__,
                conversation_messages=filter_out_system_messages(messages),
            )
            raise

    @openai_retry_strategy
    async def get_response_with_tools(
            self,
            messages: List[dict],
            action_name: GPTActionNames,
            team_name: GPTTeamNames,
            chatbot_name: GPTChatbotNames,
            tools: List[Dict[str, Any]],
            model: OpenAIModel,
            response_format: GPTResponseFormat = GPTResponseFormat.TEXT,
            temperature: GPTTemperature = GPTTemperature.POINT_FIVE,
            max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> ChatCompletion | None:
        try:
            start_time = time()

            response = await openai_client.chat.completions.create(
                messages=messages,
                model=model,
                tools=tools,
                tool_choice="auto",
                response_format={"type": response_format},
                temperature=return_temperature_float_value(temperature),
                max_tokens=max_tokens,
                timeout=TIMEOUT_SECONDS,
            )

            process_time = time() - start_time
            total_cost = calculate_openai_cost(model, response.usage.prompt_tokens, response.usage.completion_tokens)
            logger.log(
                "OpenAI With Tools Token usage",
                team_name=team_name,
                action_name=action_name,
                chatbot_name=chatbot_name,
                model=model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                requests=self.get_response_with_tools.retry.statistics.get("attempt_number"),
                response_time=process_time,
                cost=total_cost,
            )

            return response
        except Exception as e:
            logger.log(
                "GPT Exception occurred",
                level=logging.WARNING,
                service="OpenAI",
                payload=str(e),
                model_name=model,
                action_name=action_name,
                method_name="get_response_with_tools",
                team_name=team_name,
                chatbot_name=chatbot_name,
                exception_type=type(e).__name__,
                conversation_messages=filter_out_system_messages(messages),
            )
            raise
