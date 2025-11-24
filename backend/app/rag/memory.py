from __future__ import annotations

from app.models.message import Message


def build_chat_history(messages: list[Message], max_messages: int = 4) -> str:
    history = []
    for message in messages[-max_messages:]:
        role = "User" if message.role == "user" else "Assistant"
        history.append(f"{role}: {message.content}")
    return "\n".join(history)
