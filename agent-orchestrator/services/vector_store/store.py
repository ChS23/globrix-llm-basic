"""
Vector Store для работы с Qdrant.

Использует LangChain для:
- Создания эмбеддингов через OpenRouter
- Поиска похожих документов (similarity search)
- Retriever для RAG pipeline
"""

import os
from functools import lru_cache
from typing import List, Optional

import structlog
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

logger = structlog.get_logger(__name__)

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class DocumentVectorStore:
    """
    Vector store для работы с Qdrant.

    Singleton pattern через lru_cache в get_vector_store().
    """

    def __init__(
        self,
        qdrant_url: str,
        collection_name: str,
        embedding_api_key: str,
        embedding_model: str = "text-embedding-3-small",
        embedding_dimensions: int = 1536,
    ):
        """
        Инициализация vector store.

        Args:
            qdrant_url: URL Qdrant сервера
            collection_name: Название коллекции
            embedding_api_key: API ключ OpenAI для эмбеддингов
            embedding_model: Модель для эмбеддингов
            embedding_dimensions: Размерность вектора
        """
        logger.info("Initializing vector store", qdrant_url=qdrant_url, collection=collection_name)

        self.collection_name = collection_name
        self.embedding_dimensions = embedding_dimensions

        # 1. Клиент Qdrant
        self.client = QdrantClient(url=qdrant_url)

        # 2. Embeddings через OpenRouter
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=embedding_api_key,
            openai_api_base=OPENROUTER_BASE_URL,
            check_embedding_ctx_length=False,  # OpenRouter не требует tiktoken
        )

        # 3. Создаём коллекцию если не существует
        self._ensure_collection_exists()

        # 4. LangChain vector store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings,
        )

        logger.info("Vector store initialized")

    def _ensure_collection_exists(self) -> None:
        """Создаёт коллекцию в Qdrant если не существует."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            logger.info("Creating collection", name=self.collection_name)

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimensions,
                    distance=Distance.COSINE,
                ),
            )

            logger.info("Collection created")

    async def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Добавляет документы в vector store.

        Args:
            documents: Список LangChain Document

        Returns:
            Список ID добавленных документов
        """
        logger.info("Adding documents", count=len(documents))

        ids = await self.vector_store.aadd_documents(documents)

        logger.info("Documents added", count=len(ids))
        return ids

    async def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[dict] = None,
    ) -> List[Document]:
        """
        Поиск похожих документов.

        Args:
            query: Текст запроса
            k: Количество результатов
            filter_metadata: Фильтр по метаданным (опционально)

        Returns:
            Список найденных документов
        """
        logger.info("Searching documents", query=query[:50], k=k)

        if filter_metadata:
            docs = await self.vector_store.asimilarity_search(
                query, k=k, filter=filter_metadata
            )
        else:
            docs = await self.vector_store.asimilarity_search(query, k=k)

        logger.info("Documents found", count=len(docs))
        return docs

    async def search_with_scores(
        self,
        query: str,
        k: int = 5,
    ) -> List[tuple[Document, float]]:
        """
        Поиск с возвратом scores (релевантность).

        Args:
            query: Текст запроса
            k: Количество результатов

        Returns:
            Список кортежей (Document, score)
        """
        results = await self.vector_store.asimilarity_search_with_score(query, k=k)
        return results

    def as_retriever(self, search_kwargs: Optional[dict] = None) -> BaseRetriever:
        """
        Возвращает LangChain Retriever для использования в RAG chains.

        Args:
            search_kwargs: Параметры поиска (k, filter, etc.)

        Returns:
            LangChain BaseRetriever
        """
        kwargs = search_kwargs or {"k": 5}
        return self.vector_store.as_retriever(search_kwargs=kwargs)


# === Dependency Injection ===


@lru_cache()
def get_vector_store() -> DocumentVectorStore:
    """
    Singleton factory для DocumentVectorStore.

    Читает конфигурацию из env переменных.
    Использует OpenRouter для эмбеддингов.
    """
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "documents")
    # Используем OPENROUTER_API_KEY для эмбеддингов
    embedding_api_key = os.getenv("OPENROUTER_API_KEY", "")
    # Модель в формате OpenRouter: openai/text-embedding-3-small
    embedding_model = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    embedding_dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

    if not embedding_api_key:
        logger.warning("OPENROUTER_API_KEY not set, vector store may not work")

    return DocumentVectorStore(
        qdrant_url=qdrant_url,
        collection_name=collection_name,
        embedding_api_key=embedding_api_key,
        embedding_model=embedding_model,
        embedding_dimensions=embedding_dimensions,
    )
