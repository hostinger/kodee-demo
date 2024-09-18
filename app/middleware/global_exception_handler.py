from fastapi import status, Request
from fastapi.responses import JSONResponse
from utils.logger.logger import Logger

logger = Logger()


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"},
    )
