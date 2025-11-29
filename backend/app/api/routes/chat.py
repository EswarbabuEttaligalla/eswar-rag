import json
import time
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.chat import ChatCreate, ChatOut, MessageCreate, MessageOut
from app.schemas.retrieval import QueryRequest, QueryResponse
from app.services.analytics_service import AnalyticsService
from app.services.chat_service import ChatService
from app.services.rag_service import RagService
from app.rag.memory import build_chat_history

router = APIRouter()


@router.post("/", response_model=ChatOut)
async def create_chat(payload: ChatCreate, session: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    chat = await ChatService(session).create_chat(user.id, payload.title)
    return ChatOut(id=str(chat.id), title=chat.title, created_at=chat.created_at)


@router.get("/", response_model=list[ChatOut])
async def list_chats(session: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    chats = await ChatService(session).list_chats(user.id)
    return [ChatOut(id=str(chat.id), title=chat.title, created_at=chat.created_at) for chat in chats]


@router.get("/{chat_id}/messages", response_model=list[MessageOut])
async def list_messages(chat_id: str, session: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    chat_service = ChatService(session)
    await chat_service.get_chat(chat_id, owner_id=user.id)
    messages = await chat_service.list_messages(chat_id)
    return [
        MessageOut(
            id=str(message.id),
            role=message.role,
            content=message.content,
            sources=message.sources,
            created_at=message.created_at,
        )
        for message in messages
    ]


@router.post("/{chat_id}/messages", response_model=MessageOut)
async def add_message(
    chat_id: str,
    payload: MessageCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    chat_service = ChatService(session)
    await chat_service.get_chat(chat_id, owner_id=user.id)
    message = await chat_service.add_message(chat_id, "user", payload.content)
    return MessageOut(
        id=str(message.id),
        role=message.role,
        content=message.content,
        sources=message.sources,
        created_at=message.created_at,
    )


@router.post("/{chat_id}/ask", response_model=QueryResponse)
async def ask_chat(
    chat_id: str,
    payload: QueryRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    chat_service = ChatService(session)
    await chat_service.get_chat(chat_id, owner_id=user.id)
    rag_service = RagService()
    history = build_chat_history(await chat_service.list_messages(chat_id))
    await chat_service.add_message(chat_id, "user", payload.question)
    start = time.monotonic()
    response = await rag_service.answer(
        payload.question,
        user_id=str(user.id),
        top_k=payload.top_k,
        history=history,
    )
    latency_ms = (time.monotonic() - start) * 1000
    token_count = len(response.get("answer", "").split())
    await AnalyticsService(session).record_event(
        "query",
        user_id=user.id,
        payload={
            "latency_ms": round(latency_ms, 2),
            "model": "rag",
            "token_count": token_count,
        },
    )
    await chat_service.add_message(chat_id, "assistant", response["answer"], response["sources"])
    return response


@router.post("/{chat_id}/ask/stream")
async def stream_chat(
    chat_id: str,
    payload: QueryRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    chat_service = ChatService(session)
    await chat_service.get_chat(chat_id, owner_id=user.id)
    rag_service = RagService()
    history = build_chat_history(await chat_service.list_messages(chat_id))
    await chat_service.add_message(chat_id, "user", payload.question)
    start = time.monotonic()
    response = await rag_service.answer(
        payload.question,
        user_id=str(user.id),
        top_k=payload.top_k,
        history=history,
    )
    latency_ms = (time.monotonic() - start) * 1000
    token_count = len(response.get("answer", "").split())
    await AnalyticsService(session).record_event(
        "query",
        user_id=user.id,
        payload={
            "latency_ms": round(latency_ms, 2),
            "model": "rag",
            "token_count": token_count,
        },
    )
    answer = response["answer"]
    sources = response["sources"]

    async def event_stream():
        for i in range(0, len(answer), 20):
            chunk = answer[i : i + 20]
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        await chat_service.add_message(chat_id, "assistant", answer, sources)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
