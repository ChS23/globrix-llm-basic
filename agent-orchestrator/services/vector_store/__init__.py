"""Vector store service for RAG retrieval."""

from .store import DocumentVectorStore, get_vector_store

__all__ = ["DocumentVectorStore", "get_vector_store"]
