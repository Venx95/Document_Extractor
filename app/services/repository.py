from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.models.document import Document


class AbstractDocumentRepository(ABC):
    """Repository interface — Dependency Inversion Principle."""

    @abstractmethod
    async def save(self, document: Document) -> Document: ...

    @abstractmethod
    async def get_by_id(self, doc_id: UUID) -> Optional[Document]: ...

    @abstractmethod
    async def list_all(self, page: int, page_size: int) -> tuple[list[Document], int]: ...

    @abstractmethod
    async def update(self, document: Document) -> Document: ...

    @abstractmethod
    async def delete(self, doc_id: UUID) -> bool: ...


class InMemoryDocumentRepository(AbstractDocumentRepository):
    """
    Thread-safe-ish in-memory store for development / testing.
    Replace with SQLAlchemyDocumentRepository for production.
    """

    def __init__(self) -> None:
        self._store: dict[UUID, Document] = {}

    async def save(self, document: Document) -> Document:
        self._store[document.id] = document
        return document

    async def get_by_id(self, doc_id: UUID) -> Optional[Document]:
        return self._store.get(doc_id)

    async def list_all(self, page: int = 1, page_size: int = 20) -> tuple[list[Document], int]:
        all_docs = sorted(self._store.values(), key=lambda d: d.uploaded_at, reverse=True)
        total = len(all_docs)
        start = (page - 1) * page_size
        return all_docs[start : start + page_size], total

    async def update(self, document: Document) -> Document:
        self._store[document.id] = document
        return document

    async def delete(self, doc_id: UUID) -> bool:
        return self._store.pop(doc_id, None) is not None
