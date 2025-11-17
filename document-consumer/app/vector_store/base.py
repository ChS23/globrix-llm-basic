"""Base interface for vector stores."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.documents import Document


class VectorStoreInterface(ABC):
    """Abstract interface for vector store implementations."""

    @abstractmethod
    async def add_documents(
        self,
        documents: list[Document],
        **kwargs: Any,
    ) -> list[str]:
        """Add documents to the vector store.

        Args:
            documents: List of LangChain Document objects to add
            **kwargs: Additional parameters specific to the implementation

        Returns:
            List of document IDs that were added
        """
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> list[Document]:
        """Perform similarity search.

        Args:
            query: Query string
            k: Number of results to return
            filter: Metadata filters
            **kwargs: Additional parameters

        Returns:
            List of similar documents
        """
        pass

    @abstractmethod
    async def hybrid_search(
        self,
        query: str,
        k: int = 5,
        alpha: float = 0.5,
        filter: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> list[Document]:
        """Perform hybrid search (dense + sparse vectors).

        Args:
            query: Query string
            k: Number of results to return
            alpha: Weight for dense vs sparse (0=sparse only, 1=dense only)
            filter: Metadata filters
            **kwargs: Additional parameters

        Returns:
            List of similar documents
        """
        pass

    @abstractmethod
    async def delete_documents(
        self,
        ids: list[str],
        **kwargs: Any,
    ) -> bool:
        """Delete documents by IDs.

        Args:
            ids: List of document IDs to delete
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if vector store is healthy and accessible.

        Returns:
            True if healthy
        """
        pass
