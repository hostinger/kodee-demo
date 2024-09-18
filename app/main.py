from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from api.endpoints.chat import chat_router
from api.endpoints.conversation_history import history_router
from database.database_calls import AsyncPostgreSQLDatabase
from redis_services.redis_client import RedisClient
from middleware.global_exception_handler import global_exception_handler

postgres_database = AsyncPostgreSQLDatabase()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    await postgres_database.connect()
    yield
    redis_client = RedisClient()
    await redis_client.close()
    await postgres_database.close_pool()


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(history_router, prefix="/api/history", tags=["Database History"])
