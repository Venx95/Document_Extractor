import mimetypes
from pathlib import Path
from typing import Optional
from uuid import UUID

from app.core.config import Settings
from app.core.exceptions import (
    DocumentNotFoundError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from app.core.logging import get_logger
from app.models.document import Document, DocumentStatus, ExtractionType
from app.services.repository import AbstractDocumentRepository
from app.services.storage import AbstractStorageService

logger = get_logger(__name__)


class DocumentService:
    """
    Orchestrates the document lifecycle: upload → validate → store → persist.
    All I/O dependencies are injected — fully testable without filesystem or DB.
    """

    def __init__(
        self,
        repository: AbstractDocumentRepository,
        storage: AbstractStorageService,
        settings: Settings,
    ) -> None:
        self._repo = repository
        self._storage = storage
        self._settings = settings

    # ── Public API ─────────────────────────────────────────────────────────────

    async def upload_document(
        self,
        filename: str,
        content: bytes,
        mime_type: Optional[str],
        extraction_type: ExtractionType = ExtractionType.TEXT,
    ) -> Document:
        """Validate, store, and register a new document."""
        resolved_mime = mime_type or self._guess_mime(filename)
        self._validate_file(filename, resolved_mime, len(content))

        storage_path = await self._storage.save(
            data=content,
            filename=filename,
            subfolder="uploads",
        )

        safe_name = Path(filename).name
        document = Document(
            filename=safe_name,
            original_filename=safe_name,
            mime_type=resolved_mime,
            size_bytes=len(content),
            storage_path=storage_path,
            extraction_type=extraction_type,
        )
        await self._repo.save(document)
        logger.info("Document uploaded: id=%s file=%s", document.id, document.filename)
        return document

    async def get_document(self, doc_id: UUID) -> Document:
        document = await self._repo.get_by_id(doc_id)
        if not document:
            raise DocumentNotFoundError(f"Document {doc_id} not found.")
        return document

    async def list_documents(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Document], int]:
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        return await self._repo.list_all(page=page, page_size=page_size)

    async def delete_document(self, doc_id: UUID) -> None:
        document = await self.get_document(doc_id)
        await self._storage.delete(document.storage_path)
        await self._repo.delete(doc_id)
        logger.info("Document deleted: id=%s", doc_id)

    # ── Internals ──────────────────────────────────────────────────────────────

    def _validate_file(self, filename: str, mime_type: str, size: int) -> None:
        if size > self._settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileTooLargeError(
                f"File size {size / (1024**2):.1f} MB exceeds limit "
                f"of {self._settings.MAX_UPLOAD_SIZE_MB} MB."
            )

        ext = Path(filename).suffix.lower()
        if (
            mime_type not in self._settings.ALLOWED_MIME_TYPES
            and ext not in self._settings.ALLOWED_EXTENSIONS
        ):
            raise UnsupportedFileTypeError(
                f"File type '{mime_type}' ({ext}) is not supported. "
                f"Allowed: {', '.join(self._settings.ALLOWED_EXTENSIONS)}"
            )

    @staticmethod
    def _guess_mime(filename: str) -> str:
        guessed, _ = mimetypes.guess_type(filename)
        return guessed or "application/octet-stream"
