"""Global vector store manager with singleton pattern."""

from typing import Optional

import structlog

from app.config.settings import settings
from app.vector_store.base import VectorStoreInterface
from app.vector_store.qdrant_store import QdrantVectorStore

logger = structlog.get_logger()


class VectorStoreManager:
    """Singleton manager for vector store instances."""

    _instance: Optional["VectorStoreManager"] = None
    _vector_store: Optional[VectorStoreInterface] = None

    def __new__(cls) -> "VectorStoreManager":
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_vector_store(cls) -> VectorStoreInterface:
        """Get or create vector store instance.

        Returns:
            VectorStoreInterface implementation

        Raises:
            ValueError: If vector store type is not supported
        """
        if cls._vector_store is None:
            logger.info(
                "initializing_vector_store",
                type=settings.vector_store_type,
            )

            if settings.vector_store_type == "qdrant":
                cls._vector_store = QdrantVectorStore()
            else:
                raise ValueError(
                    f"Unsupported vector store type: {settings.vector_store_type}"
                )

            logger.info("vector_store_initialized", type=settings.vector_store_type)

        return cls._vector_store

    @classmethod
    async def health_check(cls) -> bool:
        """Check vector store health.

        Returns:
            True if healthy
        """
        try:
            store = cls.get_vector_store()
            return await store.health_check()
        except Exception as e:
            logger.error("vector_store_health_check_failed", error=str(e))
            return False

    @classmethod
    async def get_stats(cls) -> dict:
        """Get vector store statistics.

        Returns:
            Statistics dictionary
        """
        store = cls.get_vector_store()
        return await store.get_collection_stats()


# Global instance accessor
def get_vector_store() -> VectorStoreInterface:
    """Get global vector store instance.

    Returns:
        VectorStoreInterface implementation
    """
    return VectorStoreManager.get_vector_store()
