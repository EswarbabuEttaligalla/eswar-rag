from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.utils.time import utcnow


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document: Document):
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_by_id(self, document_id):
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id):
        result = await self.session.execute(
            select(Document).where(Document.owner_id == owner_id).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(self, document_id, status: str):
        await self.session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(status=status, updated_at=utcnow())
        )
        await self.session.commit()

    async def delete(self, document_id):
        await self.session.execute(delete(Document).where(Document.id == document_id))
        await self.session.commit()
