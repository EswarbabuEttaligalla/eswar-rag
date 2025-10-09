from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, chat: Chat):
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def get_by_id(self, chat_id):
        result = await self.session.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id):
        result = await self.session.execute(select(Chat).where(Chat.owner_id == owner_id))
        return list(result.scalars().all())

    async def delete(self, chat_id):
        await self.session.execute(delete(Chat).where(Chat.id == chat_id))
        await self.session.commit()
