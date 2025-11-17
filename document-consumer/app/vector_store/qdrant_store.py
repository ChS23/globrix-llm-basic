"""Qdrant vector store implementation."""

import uuid
from typing import Any, Optional

import structlog
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config.settings import settings
from app.vector_store.base import VectorStoreInterface

logger = structlog.get_logger()


class QdrantVectorStore(VectorStoreInterface):
    """Qdrant implementation of VectorStoreInterface using LangChain."""

    def __init__(self) -> None:
        """Initialize Qdrant vector store."""
        logger.info(
            "initializing_qdrant_store",
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection=settings.qdrant_collection_name,
        )

        # Initialize Qdrant client
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )

        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": settings.embedding_device},
            encode_kwargs={"batch_size": settings.embedding_batch_size},
        )

        # Get embedding dimension
        self.embedding_dim = len(self.embeddings.embed_query("test"))

        # Create collection if it doesn't exist
        self._ensure_collection()

        # Initialize LangChain Qdrant wrapper
        self.vectorstore = Qdrant(
            client=self.client,
            collection_name=settings.qdrant_collection_name,
            embeddings=self.embeddings,
        )

        logger.info(
            "qdrant_store_initialized",
            embedding_dim=self.embedding_dim,
            model=settings.embedding_model,
        )

    def _ensure_collection(self) -> None:
        """Ensure collection exists, create if not."""
        try:
            self.client.get_collection(settings.qdrant_collection_name)
            logger.info("collection_exists", collection=settings.qdrant_collection_name)
        except Exception:
            logger.info(
                "creating_collection",
                collection=settings.qdrant_collection_name,
                dim=self.embedding_dim,
            )
            self.client.create_collection(
                collection_name=settings.qdrant_collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )

    async def add_documents(
        self,
        documents: list[Document],
        **kwargs: Any,
    ) -> list[str]:
        """Add documents to Qdrant.

        Args:
            documents: List of LangChain Document objects
            **kwargs: Additional parameters

        Returns:
            List of document IDs
        """
        logger.info("adding_documents", count=len(documents))

        # Generate IDs if not present
        ids = [
            doc.metadata.get("id", str(uuid.uuid4()))
            for doc in documents
        ]

        # Add documents using LangChain wrapper
        self.vectorstore.add_documents(documents=documents, ids=ids)

        logger.info("documents_added", count=len(ids))
        return ids

    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> list[Document]:
        """Perform similarity search using dense vectors.

        Args:
            query: Query string
            k: Number of results
            filter: Metadata filters
            **kwargs: Additional parameters

        Returns:
            List of similar documents
        """
        logger.debug("similarity_search", query=query[:50], k=k, filter=filter)

        results = self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter,
            **kwargs,
        )

        logger.debug("similarity_search_complete", results_count=len(results))
        return results

    async def hybrid_search(
        self,
        query: str,
        k: int = 5,
        alpha: float = 0.5,
        filter: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> list[Document]:
        """Perform hybrid search (dense + sparse).

        Note: Basic implementation uses only dense vectors.
        For true hybrid search, Qdrant sparse vectors need to be configured.

        Args:
            query: Query string
            k: Number of results
            alpha: Weight (currently not used in basic implementation)
            filter: Metadata filters
            **kwargs: Additional parameters

        Returns:
            List of similar documents
        """
        logger.debug(
            "hybrid_search",
            query=query[:50],
            k=k,
            alpha=alpha,
            filter=filter,
        )

        # TODO: Implement true hybrid search with sparse vectors
        # For now, fall back to similarity search
        results = await self.similarity_search(
            query=query,
            k=k,
            filter=filter,
            **kwargs,
        )

        logger.debug("hybrid_search_complete", results_count=len(results))
        return results

    async def delete_documents(
        self,
        ids: list[str],
        **kwargs: Any,
    ) -> bool:
        """Delete documents by IDs.

        Args:
            ids: List of document IDs
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        logger.info("deleting_documents", count=len(ids))

        try:
            self.client.delete(
                collection_name=settings.qdrant_collection_name,
                points_selector=ids,
            )
            logger.info("documents_deleted", count=len(ids))
            return True
        except Exception as e:
            logger.error("delete_failed", error=str(e), exc_info=True)
            return False

    async def get_collection_stats(self) -> dict[str, Any]:
        """Get collection statistics.

        Returns:
            Dictionary with stats
        """
        collection_info = self.client.get_collection(settings.qdrant_collection_name)

        return {
            "collection_name": settings.qdrant_collection_name,
            "vectors_count": collection_info.vectors_count,
            "points_count": collection_info.points_count,
            "status": collection_info.status,
        }

    async def health_check(self) -> bool:
        """Check if Qdrant is healthy.

        Returns:
            True if healthy
        """
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            logger.error("health_check_failed", error=str(e))
            return False
