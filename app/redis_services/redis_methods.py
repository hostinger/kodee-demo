import json
import logging
import uuid
from typing import List, Optional
from redis import RedisError
from helpers.tenacity_retry_strategies import (
    redis_retry_strategy,
    redis_part_id_retry_strategy,
    PART_ID_ERROR_INDICATOR,
)
from models.chat.chat_initialization_input_model import ChatbotMetadata
from utils.logger.logger import Logger
from models.redis_messages_model import RedisMessages
from redis_services.redis_client import RedisClient
from redis_services.redis_enums import RedisPrefix, RedisExpiration

logger = Logger()
redis_client = RedisClient()


@redis_retry_strategy
async def get_conversation_id(user_id: str) -> Optional[str]:
    try:
        conversation_id = await redis_client.get(f"{RedisPrefix.CONVERSATION_KEY_PREFIX}{user_id}")
        return conversation_id
    except RedisError as e:
        logger.log("Redis: Error retrieving conversation data", level=logging.WARNING, user_id=user_id, payload=e)
        raise


@redis_retry_strategy
async def set_conversation_id(user_id: str, conversation_id: str) -> None:
    try:
        await redis_client.setex(
            f"{RedisPrefix.CONVERSATION_KEY_PREFIX}{user_id}",
            RedisExpiration.ONE_HOUR,
            conversation_id,
        )
    except RedisError as e:
        logger.log(
            "Redis: Error setting conversation_id",
            level=logging.WARNING,
            conversation_id=conversation_id,
            user_id=user_id,
            payload=e,
        )
        raise


@redis_retry_strategy
async def push_message_to_redis(user_id: str, conversation_id: str, message: RedisMessages) -> None:
    try:
        await redis_client.rpush(
            f"{RedisPrefix.CONVERSATION_MESSAGES_KEY_PREFIX}{conversation_id}", message.model_dump()
        )
        await refresh_conversation_expiration(user_id)
        await refresh_conversation_messages_expiration(conversation_id)
        await refresh_metadata_expiration(conversation_id)
    except RedisError as e:
        logger.log(
            "Redis: Error pushing message",
            level=logging.WARNING,
            conversation_id=conversation_id,
            user_id=user_id,
            payload=e,
        )
        raise


@redis_retry_strategy
async def refresh_metadata_expiration(conversation_id: str) -> None:
    try:
        await redis_client.expire(
            f"{RedisPrefix.CONVERSATION_METADATA_KEY_PREFIX}{conversation_id}",
            RedisExpiration.ONE_HOUR,
        )
    except RedisError as e:
        logger.log(
            "Redis: Error refreshing metadata expiration",
            level=logging.WARNING,
            conversation_id=conversation_id,
            payload=e,
        )
        raise


@redis_retry_strategy
async def refresh_conversation_expiration(user_id: str) -> None:
    try:
        await redis_client.expire(f"{RedisPrefix.CONVERSATION_KEY_PREFIX}{user_id}", RedisExpiration.ONE_HOUR)
    except RedisError as e:
        logger.log("Redis: Error refreshing conversation expiration", level=logging.WARNING, user_id=user_id, payload=e)
        raise


@redis_retry_strategy
async def refresh_conversation_messages_expiration(conversation_id: str) -> None:
    try:
        await redis_client.expire(
            f"{RedisPrefix.CONVERSATION_MESSAGES_KEY_PREFIX}{conversation_id}",
            RedisExpiration.ONE_HOUR,
        )
    except RedisError as e:
        logger.log(
            "Redis: Error refreshing conversation messages expiration",
            level=logging.WARNING,
            conversation_id=conversation_id,
            payload=e,
        )
        raise


@redis_retry_strategy
async def fetch_entire_conversation_history(conversation_id: str) -> List[RedisMessages]:
    try:
        history_data = await redis_client.lrange(
            f"{RedisPrefix.CONVERSATION_MESSAGES_KEY_PREFIX}{conversation_id}", 0, -1
        )
        return [RedisMessages(**json.loads(msg)).to_dict() for msg in history_data]
    except RedisError as e:
        logger.log(
            "Redis: Error fetching conversation messages",
            level=logging.WARNING,
            conversation_id=conversation_id,
            payload=e,
        )
        raise


@redis_retry_strategy
async def fetch_latest_conversation_messages(
    conversation_id: str, event_message_count: int = 20
) -> List[RedisMessages]:
    try:
        history_data = await redis_client.lrange(
            f"{RedisPrefix.CONVERSATION_MESSAGES_KEY_PREFIX}{conversation_id}", -event_message_count, -1
        )
        return [RedisMessages(**json.loads(msg)).to_dict() for msg in history_data]
    except RedisError as e:
        logger.log(
            "Redis: Error fetching latest conversation messages",
            level=logging.WARNING,
            conversation_id=conversation_id,
            payload=e,
        )
        raise


@redis_retry_strategy
async def delete_conversation(user_id: str, conversation_id: str) -> None:
    try:
        keys_to_delete = [
            f"{RedisPrefix.CHATBOT_LABEL_KEY_PREFIX}{conversation_id}",
            f"{RedisPrefix.CONVERSATION_MESSAGES_KEY_PREFIX}{conversation_id}",
            f"{RedisPrefix.CONVERSATION_KEY_PREFIX}{user_id}",
            f"{RedisPrefix.CONVERSATION_METADATA_KEY_PREFIX}{conversation_id}",
            f"{RedisPrefix.MUST_HANDOFF_CONVERSATION_KEY_PREFIX}{conversation_id}",
        ]
        await redis_client.delete(*keys_to_delete)
    except RedisError as e:
        logger.log(
            "Redis: Error deleting conversation",
            level=logging.WARNING,
            conversation_id=conversation_id,
            user_id=user_id,
            payload=e,
        )
        raise


@redis_retry_strategy
async def set_conversation_metadata(conversation_id: str, metadata: ChatbotMetadata) -> None:
    try:
        await redis_client.setex(
            f"{RedisPrefix.CONVERSATION_METADATA_KEY_PREFIX}{conversation_id}",
            RedisExpiration.ONE_HOUR,
            json.dumps(metadata.model_dump()),
        )
    except RedisError as e:
        logger.log(
            "Redis: Error setting conversation metadata",
            level=logging.WARNING,
            conversation_id=conversation_id,
            payload=e,
        )
        raise


@redis_retry_strategy
async def get_conversation_metadata(conversation_id: str, user_id: str) -> Optional[ChatbotMetadata]:
    try:
        conversation_metadata = await redis_client.get(
            f"{RedisPrefix.CONVERSATION_METADATA_KEY_PREFIX}{conversation_id}"
        )
        return ChatbotMetadata.model_validate_json(conversation_metadata)
    except RedisError as e:
        logger.log("Redis: Error retrieving conversation metadata", level=logging.WARNING, user_id=user_id, payload=e)
        raise


@redis_retry_strategy
async def generate_new_part_ids(user_id: str) -> None:
    try:
        key = f"{RedisPrefix.MESSAGE_PART_ID_KEY_PREFIX}{user_id}"
        new_part_ids = json.dumps(
            {"user_part_id": f"{user_id}-{str(uuid.uuid4())}", "assistant_part_id": f"{user_id}-{str(uuid.uuid4())}"}
        )
        await redis_client.setex(key, RedisExpiration.FIVE_MINUTES, new_part_ids)
    except RedisError as e:
        logger.log("Redis: Error generating part_ids", level=logging.WARNING, user_id=user_id, payload=e)
        raise


@redis_part_id_retry_strategy
async def get_assistant_part_id(user_id: str) -> Optional[str]:
    try:
        key = f"{RedisPrefix.MESSAGE_PART_ID_KEY_PREFIX}{user_id}"
        part_ids_str = await redis_client.get(key)
        if part_ids_str:
            part_ids = json.loads(part_ids_str)
            return part_ids.get("assistant_part_id", PART_ID_ERROR_INDICATOR)
        return PART_ID_ERROR_INDICATOR
    except RedisError as e:
        logger.log("Redis: Error retrieving assistant_part_id", level=logging.WARNING, user_id=user_id, payload=e)
        return PART_ID_ERROR_INDICATOR


@redis_part_id_retry_strategy
async def get_user_part_id(user_id: str) -> Optional[str]:
    try:
        key = f"{RedisPrefix.MESSAGE_PART_ID_KEY_PREFIX}{user_id}"
        part_ids_str = await redis_client.get(key)
        if part_ids_str:
            part_ids = json.loads(part_ids_str)
            return part_ids.get("user_part_id", PART_ID_ERROR_INDICATOR)
        return PART_ID_ERROR_INDICATOR
    except RedisError as e:
        logger.log("Redis: Error retrieving user_part_id", level=logging.WARNING, user_id=user_id, payload=e)
        return PART_ID_ERROR_INDICATOR
