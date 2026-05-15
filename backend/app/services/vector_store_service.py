from __future__ import annotations

import logging
import os

import chromadb

from app.core.config import settings


logger = logging.getLogger(__name__)


class BaseVectorStore:
    def upsert(self, ids: list[str], embeddings: list[list[float]], documents: list[str], metadatas: list[dict]):
        raise NotImplementedError

    def query(self, embedding: list[float], top_k: int, filters: dict | None):
        raise NotImplementedError

    def delete(self, ids: list[str] | None = None, filters: dict | None = None):
        raise NotImplementedError


class ChromaVectorStore(BaseVectorStore):
    def __init__(self):
        self.collection = self._init_collection()

    def _create_collection(self, client):
        return client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def _init_collection(self):
        try:
            client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
            collection = self._create_collection(client)
            logger.info("Using remote Chroma vector store at %s:%s", settings.CHROMA_HOST, settings.CHROMA_PORT)
            return collection
        except Exception as exc:
            fallback_dir = os.path.join(settings.VECTOR_DIR, "chroma")
            os.makedirs(fallback_dir, exist_ok=True)
            logger.warning("Falling back to persistent Chroma store at %s: %s", fallback_dir, exc)
            client = chromadb.PersistentClient(path=fallback_dir)
            return self._create_collection(client)

    def upsert(self, ids: list[str], embeddings: list[list[float]], documents: list[str], metadatas: list[dict]):
        self.collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    def query(self, embedding: list[float], top_k: int, filters: dict | None):
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=filters,
            include=["documents", "metadatas", "distances", "embeddings"],
        )
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        embeddings = result.get("embeddings", [[]])[0]
        ids = result.get("ids", [[]])[0]
        items = []
        for doc, meta, dist, item_id, emb in zip(docs, metas, distances, ids, embeddings):
            score = 1.0 / (1.0 + dist) if dist is not None else 0.0
            items.append({"id": item_id, "text": doc, "metadata": meta, "score": score, "embedding": emb})
        return items

    def delete(self, ids: list[str] | None = None, filters: dict | None = None):
        self.collection.delete(ids=ids, where=filters)


class FAISSVectorStore(BaseVectorStore):
    def __init__(self):
        raise NotImplementedError("FAISS store requires implementation")


class PineconeVectorStore(BaseVectorStore):
    def __init__(self):
        raise NotImplementedError("Pinecone store requires implementation")


class VectorStoreService:
    def __init__(self):
        self.store = self._init_store()

    def _init_store(self) -> BaseVectorStore:
        if settings.VECTOR_STORE == "chroma":
            return ChromaVectorStore()
        if settings.VECTOR_STORE == "faiss":
            return FAISSVectorStore()
        if settings.VECTOR_STORE == "pinecone":
            return PineconeVectorStore()
        raise ValueError("Unsupported vector store")
