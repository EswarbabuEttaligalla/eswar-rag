SYSTEM_PROMPT = """You are a private enterprise knowledge assistant. Follow the rules:
- Answer using only the provided context.
- If the answer is not in the context, say you do not have enough information.
- Provide concise responses with citations.
"""


def build_prompt(context: str, question: str, history: str | None = None) -> str:
    history_block = f"\n\nConversation history:\n{history}\n" if history else ""
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n"
        f"{history_block}\n"
        f"Question: {question}\n"
        f"Answer with citations."
    )
