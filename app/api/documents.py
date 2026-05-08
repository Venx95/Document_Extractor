import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, File, Form, Query, UploadFile, status

from app.core.dependencies import DocumentServiceDep
from app.models.document import ExtractionType
from app.schemas.document import (
    DocumentDetail,
    DocumentSummary,
    PaginatedDocuments,
    UploadResponse,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document for extraction",
    description=(
        "Upload a document (PDF, image, Word, or plain text). "
        "The file is validated, stored, and queued for extraction."
    ),
)
async def upload_document(
    service: DocumentServiceDep,
    file: UploadFile = File(..., description="Document file to upload"),
    extraction_type: ExtractionType = Form(
        default=ExtractionType.TEXT,
        description="Type of extraction to perform",
    ),
) -> UploadResponse:
    content = await file.read()
    document = await service.upload_document(
        filename=file.filename or "unnamed",
        content=content,
        mime_type=file.content_type,
        extraction_type=extraction_type,
    )
    return UploadResponse(
        id=document.id,
        filename=document.filename,
        original_filename=document.original_filename,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        status=document.status,
        extraction_type=document.extraction_type,
        uploaded_at=document.uploaded_at,
    )


@router.get(
    "/",
    response_model=PaginatedDocuments,
    summary="List all documents",
)
async def list_documents(
    service: DocumentServiceDep,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedDocuments:
    documents, total = await service.list_documents(page=page, page_size=page_size)
    return PaginatedDocuments(
        items=[_to_summary(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentDetail,
    summary="Get document details",
)
async def get_document(
    document_id: UUID,
    service: DocumentServiceDep,
) -> DocumentDetail:
    document = await service.get_document(document_id)
    return DocumentDetail(
        id=document.id,
        original_filename=document.original_filename,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        status=document.status,
        extraction_type=document.extraction_type,
        uploaded_at=document.uploaded_at,
        processed_at=document.processed_at,
        extracted_data=document.extracted_data,
        error_message=document.error_message,
        metadata=document.metadata,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
)
async def delete_document(
    document_id: UUID,
    service: DocumentServiceDep,
) -> None:
    await service.delete_document(document_id)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_summary(d) -> DocumentSummary:
    return DocumentSummary(
        id=d.id,
        original_filename=d.original_filename,
        mime_type=d.mime_type,
        size_bytes=d.size_bytes,
        status=d.status,
        extraction_type=d.extraction_type,
        uploaded_at=d.uploaded_at,
        processed_at=d.processed_at,
    )
