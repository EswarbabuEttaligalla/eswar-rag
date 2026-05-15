import logging

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.document import DocumentOut, DocumentProcessResponse, DocumentUploadResponse
from app.services.analytics_service import AnalyticsService
from app.services.document_service import DocumentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        service = DocumentService(session)
        document = await service.upload(user.id, file)
        try:
            await AnalyticsService(session).record_event(
                "upload",
                user_id=user.id,
                payload={"document_id": str(document.id), "size": document.size},
            )
        except Exception as exc:
            logger.warning("Upload analytics recording failed for document %s: %s", document.id, exc)
        return DocumentUploadResponse(
            document=DocumentOut(
                id=str(document.id),
                filename=document.filename,
                content_type=document.content_type,
                size=document.size,
                status=document.status,
                metadata=document.meta,
                created_at=document.created_at,
            )
        )
    except Exception as exc:
        logger.exception("upload failed")
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@router.get("/", response_model=list[DocumentOut])
async def list_documents(session: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    service = DocumentService(session)
    documents = await service.list_documents(user.id)
    return [
        DocumentOut(
            id=str(document.id),
            filename=document.filename,
            content_type=document.content_type,
            size=document.size,
            status=document.status,
            metadata=document.meta,
            created_at=document.created_at,
        )
        for document in documents
    ]


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document(document_id: str, session: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    service = DocumentService(session)
    await service.process_document(document_id, user.id)
    return DocumentProcessResponse(document_id=document_id, status="processing")


@router.delete("/{document_id}")
async def delete_document(document_id: str, session: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    service = DocumentService(session)
    await service.delete_document(document_id, user.id)
    return {"status": "deleted"}
