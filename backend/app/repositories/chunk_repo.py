from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, chunks: list[Chunk]):
        self.session.add_all(chunks)
        await self.session.commit()

    async def list_by_document(self, document_id):
        result = await self.session.execute(select(Chunk).where(Chunk.document_id == document_id))
        return list(result.scalars().all())

    async def delete_by_document(self, document_id):
        await self.session.execute(delete(Chunk).where(Chunk.document_id == document_id))
        await self.session.commit()
