import json
import redis.asyncio as redis
from enum import IntEnum
from typing import Any, Optional, List
from redis_services.redis_enums import RedisExpiration
from utils.env_constants import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from utils.logger.logger import Logger

REDIS_SOCKET_TIMEOUT = 10
REDIS_CONNECT_TIMEOUT = 5
logger = Logger()


class RedisClient:
    _instance: "RedisClient" = None

    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "client"):
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=REDIS_CONNECT_TIMEOUT,
            )

    async def close(self) -> None:
        await self.client.close()

    async def __aenter__(self) -> "RedisClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.client.get(key)
        except redis.RedisError as e:
            logger.log(f"Redis: Error getting key {key}", payload=str(e))
            return None

    async def setex(self, key: str, expiration_time: RedisExpiration, value: Any) -> bool:
        try:
            if isinstance(expiration_time, IntEnum):
                expiration_time = expiration_time.value
            await self.client.setex(key, expiration_time, value)
            return True
        except redis.RedisError as e:
            logger.log(
                f"Redis: Error setting key {key} with value {value} for {expiration_time} seconds", payload=str(e)
            )
            return False

    async def rpush(self, key: str, value: Any) -> bool:
        try:
            await self.client.rpush(key, json.dumps(value))
            return True
        except redis.RedisError as e:
            logger.log(f"Redis: Error pushing to list {key}", payload=str(e))
            return False

    async def lrange(self, key: str, start: int, stop: int) -> List[Any]:
        try:
            return await self.client.lrange(key, start, stop)
        except redis.RedisError as e:
            logger.log(f"Redis: Error retrieving range from list {key}", payload=str(e))
            return []

    async def delete(self, *keys: str) -> bool:
        try:
            await self.client.delete(*keys)
            return True
        except redis.RedisError as e:
            logger.log(f"Redis: Error deleting keys {keys}", payload=str(e))
            return False

    async def expire(self, key: str, expiration_time: RedisExpiration) -> bool:
        try:
            if isinstance(expiration_time, IntEnum):
                expiration_time = expiration_time.value
            await self.client.expire(key, expiration_time)
            return True
        except redis.RedisError as e:
            logger.log(f"Redis: Error setting expire for key {key}", payload=str(e))
            return False
