from fastapi import HTTPException

from app.models.chat import Chat
from app.models.message import Message
from app.repositories.chat_repo import ChatRepository
from app.repositories.message_repo import MessageRepository


class ChatService:
    def __init__(self, session):
        self.chat_repo = ChatRepository(session)
        self.message_repo = MessageRepository(session)

    async def create_chat(self, owner_id, title: str) -> Chat:
        chat = Chat(owner_id=owner_id, title=title)
        return await self.chat_repo.create(chat)

    async def list_chats(self, owner_id):
        return await self.chat_repo.list_by_owner(owner_id)

    async def get_chat(self, chat_id, owner_id=None):
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        if owner_id and str(chat.owner_id) != str(owner_id):
            raise HTTPException(status_code=403, detail="Forbidden")
        return chat

    async def add_message(self, chat_id, role: str, content: str, sources: list | None = None) -> Message:
        message = Message(chat_id=chat_id, role=role, content=content, sources=sources or [])
        return await self.message_repo.create(message)

    async def list_messages(self, chat_id):
        return await self.message_repo.list_by_chat(chat_id)
