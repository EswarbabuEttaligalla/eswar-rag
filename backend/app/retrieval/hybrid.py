import re


def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z0-9]+", text.lower())
    return set(tokens)


def lexical_score(query: str, text: str) -> float:
    q_tokens = tokenize(query)
    t_tokens = tokenize(text)
    if not q_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)
