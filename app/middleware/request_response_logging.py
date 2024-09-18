import logging
import traceback
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from time import time
from utils.logger.logger import Logger

logger = Logger()


def format_detailed_traceback(exc: Exception) -> str:
    tb_list = traceback.format_exception(type(exc), exc, exc.__traceback__)
    exception_message = tb_list[-1].strip()
    location_info = tb_list[-2].strip() if len(tb_list) > 1 else "Location info not available"
    detailed_traceback = f"{location_info}\n{exception_message}"

    return detailed_traceback


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body_bytes = await request.body()
        request.state.body = body_bytes.decode("utf-8")

        start_time = time()
        try:
            response = await call_next(request)
            process_time = time() - start_time
            logger.log(
                "Endpoint response processing",
                endpoint=request.url.path,
                response_time=process_time,
                status_code=response.status_code,
            )
        except Exception as exc:
            logger.log(
                "Unhandled exception occurred during request processing",
                level=logging.ERROR,
                request_path=request.url.path,
                request_body=getattr(request.state, "body", "Request body not available"),
                exception=str(exc),
                traceback=format_detailed_traceback(exc),
            )
            raise exc from None

        return response
