import logging
import asyncpg
from asyncpg import UniqueViolationError, ForeignKeyViolationError, PostgresError
from database.database_models.conversations_table_model import ConversationsTable
from database.database_models.history_table_model import HistoryTable
from database.database_models.events_table_model import EventsTable
from helpers.tenacity_retry_strategies import postgresql_retry_strategy
from utils.logger.logger import Logger
from utils.env_constants import DB_NAME, DB_PASSWORD, DB_USERNAME, DB_HOST

MIN_POOL_SIZE = 1
MAX_POOL_SIZE = 10
COMMAND_MAX_EXECUTION_TIMEOUT = 5
ACQUIRE_A_CONNECTION_MAX_TIMEOUT = 5

logger = Logger()


class AsyncPostgreSQLDatabase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db_uri = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        self.pool = None

    async def connect(self, connection_timeout=ACQUIRE_A_CONNECTION_MAX_TIMEOUT) -> None:
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.db_uri, min_size=MIN_POOL_SIZE, max_size=MAX_POOL_SIZE, command_timeout=connection_timeout
            )

    async def close_pool(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None

    @postgresql_retry_strategy
    async def _fetch_query(self, query, *args, command_timeout=COMMAND_MAX_EXECUTION_TIMEOUT):
        try:
            async with self.pool.acquire(timeout=command_timeout) as connection:
                async with connection.transaction():
                    return await connection.fetch(query, *args, timeout=command_timeout)
        except TimeoutError as e:
            logger.log(
                "TimeoutError occurred while fetching data",
                level=logging.ERROR,
                query=query,
                arguments=args,
                payload=e,
            )
            raise
        except PostgresError as e:
            logger.log("PostgresError occurred:", level=logging.ERROR, query=query, arguments=args, payload=e)
            raise
        except Exception as e:
            logger.log(
                "Unexpected error occurred during database operation:",
                level=logging.ERROR,
                query=query,
                arguments=args,
                payload=e,
            )
            raise

    @postgresql_retry_strategy
    async def _insert_query(self, query, *args, command_timeout=COMMAND_MAX_EXECUTION_TIMEOUT) -> None:
        try:
            async with self.pool.acquire(timeout=command_timeout) as connection:
                async with connection.transaction():
                    return await connection.execute(query, *args, timeout=command_timeout)
        except TimeoutError as e:
            logger.log(
                "TimeoutError occurred while executing query",
                level=logging.ERROR,
                query=query,
                arguments=args,
                payload=e,
            )
            raise
        except (UniqueViolationError, ForeignKeyViolationError) as e:
            logger.log("Constraint violation occurred:", level=logging.ERROR, query=query, arguments=args, payload=e)
            raise
        except PostgresError as e:
            logger.log("PostgresError occurred:", level=logging.ERROR, query=query, arguments=args, payload=e)
            raise
        except Exception as e:
            logger.log(
                "Unexpected error occurred during database operation:",
                level=logging.ERROR,
                query=query,
                arguments=args,
                payload=e,
            )
            raise

    async def insert_into_conversations_table(self, data: ConversationsTable) -> None:
        query = "INSERT INTO conversations (user_id, conversation_id) VALUES ($1, $2)"
        await self._insert_query(query, data.user_id, data.conversation_id)

    async def insert_into_events_table(self, data: EventsTable) -> None:
        query = "INSERT INTO events (conversation_id, event_type, payload, message_part_id) VALUES ($1, $2, $3, $4)"
        await self._insert_query(query, data.conversation_id, data.event_type, data.payload, data.message_part_id)

    async def insert_into_history_table(self, data: HistoryTable) -> None:
        query = "INSERT INTO history (conversation_id, author_type, message, chatbot_label, message_part_id) VALUES ($1, $2, $3, $4, $5)"
        await self._insert_query(
            query, data.conversation_id, data.author_type, data.message, data.chatbot_label, data.message_part_id
        )

    async def get_events_by_conversation_id(self, conversation_id: str):
        query = """
            SELECT id, conversation_id, event_type, payload, message_part_id, created_at
            FROM events
            WHERE conversation_id = $1
            ORDER BY created_at ASC;
        """
        return await self._fetch_query(query, conversation_id)

    async def get_history_by_conversation_id(self, conversation_id: str):
        query = """
            SELECT id, conversation_id, author_type, message, chatbot_label, message_part_id, created_at
            FROM history
            WHERE conversation_id = $1
            ORDER BY created_at ASC;
        """
        return await self._fetch_query(query, conversation_id)


postgres_database = AsyncPostgreSQLDatabase()
