import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.utils.text_utils import normalize_text


class ChunkingService:
    def __init__(self):
        chunk_size = max(300, min(settings.CHUNK_SIZE, 450))
        chunk_overlap = max(40, min(settings.CHUNK_OVERLAP, 80))
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "],
        )

    def split(self, text: str) -> list[str]:
        preserved_segments = [p.strip() for p in re.split(r"\r?\n+", text) if p.strip()]
        chunks: list[str] = []
        seen: set[str] = set()
        for segment in preserved_segments or [text]:
            cleaned_segment = normalize_text(segment)
            for chunk in self.splitter.split_text(cleaned_segment):
                normalized_chunk = normalize_text(chunk)
                if not normalized_chunk or normalized_chunk in seen:
                    continue
                seen.add(normalized_chunk)
                chunks.append(normalized_chunk)
        return chunks
