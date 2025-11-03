import hashlib
import re


INJECTION_PATTERNS = [
    r"ignore\s+previous",
    r"system\s+prompt",
    r"act\s+as",
    r"developer\s+message",
    r"jailbreak",
]


def is_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in INJECTION_PATTERNS)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
