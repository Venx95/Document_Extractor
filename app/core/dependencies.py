"""
Dependency Injection container.

FastAPI resolves these via `Depends(...)`.
Swap any concrete implementation here without touching route handlers.
"""
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.document_service import DocumentService
from app.services.repository import AbstractDocumentRepository, InMemoryDocumentRepository
from app.services.storage import AbstractStorageService, LocalStorageService


# ── Singletons ─────────────────────────────────────────────────────────────────

@lru_cache
def get_repository() -> AbstractDocumentRepository:
    """Single shared repository instance.  Replace with DB-backed repo in prod."""
    return InMemoryDocumentRepository()


@lru_cache
def get_storage(settings: Settings = Depends(get_settings)) -> AbstractStorageService:
    return LocalStorageService(base_dir=settings.UPLOAD_DIR)


# ── Composed service ───────────────────────────────────────────────────────────

def get_document_service(
    repository: AbstractDocumentRepository = Depends(get_repository),
    storage: AbstractStorageService = Depends(get_storage),
    settings: Settings = Depends(get_settings),
) -> DocumentService:
    return DocumentService(
        repository=repository,
        storage=storage,
        settings=settings,
    )


# ── Convenience type aliases (use in route signatures) ─────────────────────────

SettingsDep = Annotated[Settings, Depends(get_settings)]
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
