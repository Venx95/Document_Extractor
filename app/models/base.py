"""
Extractor abstractions — Open/Closed Principle.
Add a new extractor by subclassing BaseExtractor; no existing code changes.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.models.document import ExtractionType


@dataclass
class ExtractionResult:
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    extraction_type: ExtractionType = ExtractionType.TEXT


class BaseExtractor(ABC):
    """
    Interface for all extractors.
    Implementations: PDFExtractor, ImageOCRExtractor, DocxExtractor, etc.
    """

    @property
    @abstractmethod
    def supported_mime_types(self) -> list[str]:
        """MIME types this extractor handles."""

    @abstractmethod
    async def extract(self, content: bytes, filename: str) -> ExtractionResult:
        """Run extraction and return structured result."""

    def can_handle(self, mime_type: str) -> bool:
        return mime_type in self.supported_mime_types


class PlainTextExtractor(BaseExtractor):
    """Trivial extractor for plain-text files — serves as a working example."""

    @property
    def supported_mime_types(self) -> list[str]:
        return ["text/plain"]

    async def extract(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            text = content.decode("utf-8", errors="replace")
            return ExtractionResult(
                success=True,
                data={
                    "text": text,
                    "char_count": len(text),
                    "line_count": text.count("\n") + 1,
                },
                extraction_type=ExtractionType.TEXT,
            )
        except Exception as exc:
            return ExtractionResult(success=False, error=str(exc))


class ExtractorRegistry:
    """
    Resolves the correct extractor for a given MIME type.
    Register extractors at startup; open for extension, closed for modification.
    """

    def __init__(self) -> None:
        self._extractors: list[BaseExtractor] = []

    def register(self, extractor: BaseExtractor) -> None:
        self._extractors.append(extractor)

    def resolve(self, mime_type: str) -> BaseExtractor | None:
        for extractor in self._extractors:
            if extractor.can_handle(mime_type):
                return extractor
        return None
