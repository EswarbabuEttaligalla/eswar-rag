from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.utils.text_utils import normalize_text


class ChunkingService:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    def split(self, text: str) -> list[str]:
        normalized = normalize_text(text)
        paragraphs = [p.strip() for p in normalized.split("\n\n") if p.strip()]
        chunks: list[str] = []
        for paragraph in paragraphs:
            chunks.extend(self.splitter.split_text(paragraph))
        return chunks
