import hashlib
import shutil
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import aiofiles

from app.core.exceptions import StorageError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AbstractStorageService(ABC):
    """Interface — swap local disk for S3/GCS without touching callers."""

    @abstractmethod
    async def save(self, data: bytes, filename: str, subfolder: str = "") -> str:
        """Persist bytes and return the storage path / key."""

    @abstractmethod
    async def load(self, storage_path: str) -> bytes:
        """Retrieve raw bytes from a storage path / key."""

    @abstractmethod
    async def delete(self, storage_path: str) -> None:
        """Remove a stored file."""

    @abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Check existence without loading content."""


class LocalStorageService(AbstractStorageService):
    """
    Stores files on the local filesystem.
    Production: replace with S3StorageService implementing the same interface.
    """

    def __init__(self, base_dir: Path) -> None:
        self._base = base_dir
        self._base.mkdir(parents=True, exist_ok=True)

    async def save(self, data: bytes, filename: str, subfolder: str = "") -> str:
        dest_dir = self._base / subfolder if subfolder else self._base
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Prevent collisions with a UUID prefix
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        dest_path = dest_dir / unique_name

        try:
            async with aiofiles.open(dest_path, "wb") as f:
                await f.write(data)
        except OSError as exc:
            logger.error("Failed to write file %s: %s", dest_path, exc)
            raise StorageError(f"Could not save file: {exc}") from exc

        relative = dest_path.relative_to(self._base)
        logger.debug("Saved file → %s", relative)
        return str(relative)

    async def load(self, storage_path: str) -> bytes:
        full = self._base / storage_path
        if not full.exists():
            raise StorageError(f"File not found in storage: {storage_path}")
        try:
            async with aiofiles.open(full, "rb") as f:
                return await f.read()
        except OSError as exc:
            raise StorageError(f"Could not read file: {exc}") from exc

    async def delete(self, storage_path: str) -> None:
        full = self._base / storage_path
        try:
            full.unlink(missing_ok=True)
        except OSError as exc:
            raise StorageError(f"Could not delete file: {exc}") from exc

    def exists(self, storage_path: str) -> bool:
        return (self._base / storage_path).exists()

    @staticmethod
    def compute_checksum(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
