from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import IDEPException
from app.core.logging import get_logger

logger = get_logger(__name__)


def _error_body(error_code: str, message: str, details=None) -> dict:
    body = {"error": {"code": error_code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(IDEPException)
    async def idep_exception_handler(request: Request, exc: IDEPException):
        logger.warning(
            "IDEPException: %s — %s",
            exc.error_code,
            exc.message,
            extra={"path": request.url.path},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.error_code, exc.message, exc.details),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content=_error_body("INTERNAL_ERROR", "An unexpected error occurred."),
        )
