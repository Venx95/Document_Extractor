from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractionType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    FORM = "form"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CUSTOM = "custom"


class Document:
    """
    Core domain entity — framework-agnostic.
    Swap in a SQLAlchemy / Beanie model without touching business logic.
    """

    def __init__(
        self,
        filename: str,
        original_filename: str,
        mime_type: str,
        size_bytes: int,
        storage_path: str,
        extraction_type: ExtractionType = ExtractionType.TEXT,
        id: Optional[UUID] = None,
        status: DocumentStatus = DocumentStatus.PENDING,
        uploaded_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None,
        extracted_data: Optional[dict[str, Any]] = None,
        error_message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.id: UUID = id or uuid4()
        self.filename = filename
        self.original_filename = original_filename
        self.mime_type = mime_type
        self.size_bytes = size_bytes
        self.storage_path = storage_path
        self.extraction_type = extraction_type
        self.status = status
        self.uploaded_at = uploaded_at or datetime.utcnow()
        self.processed_at = processed_at
        self.extracted_data = extracted_data
        self.error_message = error_message
        self.metadata = metadata or {}

    def mark_processing(self) -> None:
        self.status = DocumentStatus.PROCESSING

    def mark_completed(self, extracted_data: dict[str, Any]) -> None:
        self.status = DocumentStatus.COMPLETED
        self.extracted_data = extracted_data
        self.processed_at = datetime.utcnow()

    def mark_failed(self, reason: str) -> None:
        self.status = DocumentStatus.FAILED
        self.error_message = reason
        self.processed_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Document id={self.id} status={self.status} file={self.original_filename}>"
