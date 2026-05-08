from typing import Any, Optional


class IDEPException(Exception):
    """Base exception for all platform errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.details = details
        super().__init__(self.message)


# ── 4xx ───────────────────────────────────────────────────────────────────────

class ValidationError(IDEPException):
    status_code = 422
    error_code = "VALIDATION_ERROR"
    message = "Request validation failed."


class UnsupportedFileTypeError(IDEPException):
    status_code = 415
    error_code = "UNSUPPORTED_FILE_TYPE"
    message = "The uploaded file type is not supported."


class FileTooLargeError(IDEPException):
    status_code = 413
    error_code = "FILE_TOO_LARGE"
    message = "The uploaded file exceeds the maximum allowed size."


class DocumentNotFoundError(IDEPException):
    status_code = 404
    error_code = "DOCUMENT_NOT_FOUND"
    message = "The requested document was not found."


# ── 5xx ───────────────────────────────────────────────────────────────────────

class ExtractionError(IDEPException):
    status_code = 500
    error_code = "EXTRACTION_FAILED"
    message = "Document extraction failed."


class StorageError(IDEPException):
    status_code = 500
    error_code = "STORAGE_ERROR"
    message = "A storage operation failed."
