from __future__ import annotations

import os
import uuid
from fastapi import HTTPException, UploadFile
from redis import Redis
from redis.exceptions import RedisError
from rq import Queue

from app.core.config import settings, build_redis_url
from app.models.chunk import Chunk
from app.models.document import Document
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.document_repo import DocumentRepository


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

    def _get_vector_store(self):
        if self._vector_store is None:
            from app.services.vector_store_service import VectorStoreService

            self._vector_store = VectorStoreService().store
        return self._vector_store

    async def upload(self, owner_id, file: UploadFile) -> Document:
        path, size, stored_name = await self.file_service.save_upload(file)
        document = Document(
            owner_id=owner_id,
            filename=stored_name,
            content_type=file.content_type or "application/octet-stream",
            size=size,
            status="uploaded",
            meta={"original_name": file.filename, "path": path},
        )
        document = await self.document_repo.create(document)
        if settings.ASYNC_PROCESSING:
            try:
                self.enqueue_processing(document.id, owner_id)
            except RedisError:
                await self.process_document(document.id, owner_id)
        else:
            await self.process_document(document.id, owner_id)
        return document

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
            vector_store = self._get_vector_store()
            await self.document_repo.update_status(document_id, "processing")
            file_path = document.meta.get("path") or os.path.join(settings.UPLOAD_DIR, document.filename)
            text = await self.file_service.extract_text(file_path)
            chunks = self.chunking_service.split(text)
            if not chunks:
                await self.document_repo.update_status(document_id, "processed")
                return
            embeddings = await self.embedding_service.embed_texts(chunks)

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

            vector_store.upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
            await self.chunk_repo.create_many(chunk_models)
            await self.document_repo.update_status(document_id, "processed")
        except Exception:
            await self.document_repo.update_status(document_id, "failed")
            raise

    async def list_documents(self, owner_id):
        return await self.document_repo.list_by_owner(owner_id)

    async def delete_document(self, document_id, owner_id):
        document = await self.document_repo.get_by_id(document_id)
        if not document or str(document.owner_id) != str(owner_id):
            raise HTTPException(status_code=404, detail="Document not found")
        vector_store = self._get_vector_store()
        vector_store.delete(filters={"document_id": str(document_id)})
        await self.chunk_repo.delete_by_document(document_id)
        await self.document_repo.delete(document_id)

    def enqueue_processing(self, document_id, owner_id) -> None:
        redis_conn = Redis.from_url(build_redis_url())
        queue = Queue(settings.RQ_QUEUE_NAME, connection=redis_conn)
        queue.enqueue("app.workers.tasks.process_document_job", str(document_id), str(owner_id))
