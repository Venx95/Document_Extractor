from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus, ExtractionType


# ── Shared ─────────────────────────────────────────────────────────────────────

class _Base(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Upload ─────────────────────────────────────────────────────────────────────

class UploadResponse(_Base):
    """Returned immediately after a successful file upload."""

    id: UUID
    filename: str
    original_filename: str
    mime_type: str
    size_bytes: int
    status: DocumentStatus
    extraction_type: ExtractionType
    uploaded_at: datetime
    message: str = "File uploaded successfully. Extraction queued."


# ── Document ───────────────────────────────────────────────────────────────────

class DocumentSummary(_Base):
    id: UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    status: DocumentStatus
    extraction_type: ExtractionType
    uploaded_at: datetime
    processed_at: Optional[datetime] = None


class DocumentDetail(DocumentSummary):
    extracted_data: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


# ── Paginated list ─────────────────────────────────────────────────────────────

class PaginatedDocuments(_Base):
    items: list[DocumentSummary]
    total: int
    page: int
    page_size: int
    pages: int


# ── Health ─────────────────────────────────────────────────────────────────────

class HealthResponse(_Base):
    status: str
    version: str
    environment: str
