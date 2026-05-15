from __future__ import annotations

import asyncio
import os
import uuid

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.core.logging import get_logger
from app.models.chunk import Chunk
from app.models.document import Document
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.document_repo import DocumentRepository


logger = get_logger(__name__)


class DocumentService:
    def __init__(self, session):
        self.document_repo = DocumentRepository(session)
        self.chunk_repo = ChunkRepository(session)
        from app.services.chunking_service import ChunkingService
        from app.services.file_service import FileService

        self.file_service = FileService()
        self.chunking_service = ChunkingService()
        from app.services.embedding_service import EmbeddingService

        self.embedding_service = EmbeddingService()
        self._vector_store = None

    async def _get_vector_store(self):
        if self._vector_store is None:
            from app.services.vector_store_service import VectorStoreService

            self._vector_store = await asyncio.to_thread(lambda: VectorStoreService().store)
        return self._vector_store

    async def upload(self, owner_id, file: UploadFile) -> Document:
        logger.info(
            "upload received",
            owner_id=str(owner_id),
            filename=file.filename,
            content_type=file.content_type,
        )
        path, size, stored_name = await self.file_service.save_upload(file)
        logger.info("file saved", owner_id=str(owner_id), path=path, size=size)
        document = Document(
            owner_id=owner_id,
            filename=stored_name,
            content_type=file.content_type or "application/octet-stream",
            size=size,
            status="uploaded",
            meta={"original_name": file.filename, "path": path},
        )
        document = await self.document_repo.create(document)
        self._schedule_processing(document.id, owner_id)
        logger.info("upload success", document_id=str(document.id), owner_id=str(owner_id))
        return document

    def _schedule_processing(self, document_id, owner_id) -> None:
        task = asyncio.create_task(self.process_document(document_id, owner_id))

        def _log_task_result(completed_task: asyncio.Task) -> None:
            try:
                completed_task.result()
            except Exception:
                logger.exception(
                    "background document processing failed",
                    document_id=str(document_id),
                    owner_id=str(owner_id),
                )

        task.add_done_callback(_log_task_result)

    async def process_document(self, document_id, owner_id) -> None:
        if isinstance(document_id, str):
            document_id = uuid.UUID(document_id)
        if isinstance(owner_id, str):
            owner_id = uuid.UUID(owner_id)
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        if str(document.owner_id) != str(owner_id):
            raise HTTPException(status_code=403, detail="Forbidden")

        try:
            vector_store = await self._get_vector_store()
            logger.info("chunking started", document_id=str(document_id), owner_id=str(owner_id))
            await self.document_repo.update_status(document_id, "processing")
            file_path = document.meta.get("path") or os.path.join(settings.UPLOAD_DIR, document.filename)
            text = await self.file_service.extract_text(file_path)
            chunks = await asyncio.wait_for(
                asyncio.to_thread(self.chunking_service.split, text),
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
            )
            logger.info("chunking completed", document_id=str(document_id), chunk_count=len(chunks))
            if not chunks:
                await self.document_repo.update_status(document_id, "processed")
                logger.info("upload success", document_id=str(document_id), message="no chunks extracted")
                return

            logger.info("embedding started", document_id=str(document_id), chunk_count=len(chunks))
            embeddings = await asyncio.wait_for(
                self.embedding_service.embed_texts(chunks),
                timeout=settings.EMBEDDING_TIMEOUT_SECONDS,
            )
            logger.info("embedding completed", document_id=str(document_id), embedding_count=len(embeddings))

            chunk_models: list[Chunk] = []
            ids: list[str] = []
            metadatas: list[dict] = []

            for content, embedding in zip(chunks, embeddings):
                chunk_id = uuid.uuid4()
                metadata = {"document_id": str(document_id), "user_id": str(owner_id)}
                chunk_models.append(
                    Chunk(
                        id=chunk_id,
                        document_id=document_id,
                        content=content,
                        embedding_id=str(chunk_id),
                        meta=metadata,
                    )
                )
                ids.append(str(chunk_id))
                metadatas.append(metadata)

            logger.info("vector insertion started", document_id=str(document_id), chunk_count=len(chunk_models))
            await asyncio.wait_for(
                asyncio.to_thread(vector_store.upsert, ids, embeddings, chunks, metadatas),
                timeout=settings.VECTOR_STORE_TIMEOUT_SECONDS,
            )
            await self.chunk_repo.create_many(chunk_models)
            logger.info("vector insertion completed", document_id=str(document_id), chunk_count=len(chunk_models))
            await self.document_repo.update_status(document_id, "processed")
            logger.info("upload success", document_id=str(document_id), status="processed")
        except Exception:
            logger.exception("upload failure", document_id=str(document_id), owner_id=str(owner_id))
            await self.document_repo.update_status(document_id, "failed")
            raise

    async def list_documents(self, owner_id):
        return await self.document_repo.list_by_owner(owner_id)

    async def delete_document(self, document_id, owner_id):
        document = await self.document_repo.get_by_id(document_id)
        if not document or str(document.owner_id) != str(owner_id):
            raise HTTPException(status_code=404, detail="Document not found")
        vector_store = await self._get_vector_store()
        await asyncio.wait_for(
            asyncio.to_thread(vector_store.delete, None, {"document_id": str(document_id)}),
            timeout=settings.VECTOR_STORE_TIMEOUT_SECONDS,
        )
        await self.chunk_repo.delete_by_document(document_id)
        await self.document_repo.delete(document_id)
