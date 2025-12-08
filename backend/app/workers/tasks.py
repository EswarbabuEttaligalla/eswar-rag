import asyncio

from app.db.session import AsyncSessionLocal
from app.services.document_service import DocumentService


def process_document_job(document_id: str, owner_id: str) -> None:
    async def _run():
        async with AsyncSessionLocal() as session:
            service = DocumentService(session)
            await service.process_document(document_id, owner_id)

    asyncio.run(_run())
