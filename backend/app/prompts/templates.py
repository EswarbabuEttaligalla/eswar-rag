SYSTEM_PROMPT = """You are a private enterprise knowledge assistant. Follow the rules:
- Answer using only the provided context.
- If the answer is not in the context, say you do not have enough information.
- Give a direct answer in 1 to 3 short sentences.
- Do not dump retrieved text, repeat the question, or add unrelated details.
- Prefer the most specific grounded answer over completeness.
- Use the supplied context only as evidence; do not quote large passages.
"""


def build_prompt(context: str, question: str, history: str | None = None) -> str:
    history_block = f"\n\nConversation history:\n{history}\n" if history else ""
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n"
        f"{history_block}\n"
        f"Question: {question}\n"
        f"Answer concisely and grounded in the context."
    )
