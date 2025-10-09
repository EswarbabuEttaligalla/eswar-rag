from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message: Message):
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def list_by_chat(self, chat_id):
        result = await self.session.execute(
            select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
        )
        return list(result.scalars().all())
