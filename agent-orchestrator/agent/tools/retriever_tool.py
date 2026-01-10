"""
Retriever Tool - поиск по векторному хранилищу документов.

Используется для RAG (Retrieval-Augmented Generation):
- Поиск релевантных документов по запросу
- Контекстное обогащение ответов агента
"""

from typing import List

import structlog
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.tools import tool


def _force_all_required(schema: dict) -> None:
    """Force all properties into required array for Azure/o3 compatibility."""
    if "properties" in schema:
        schema["required"] = list(schema["properties"].keys())


from langchain_core.documents import Document

from services.vector_store import get_vector_store, DocumentVectorStore

logger = structlog.get_logger(__name__)


class RetrieverToolInput(BaseModel):
    """Схема аргументов для retriever_tool."""

    model_config = ConfigDict(json_schema_extra=_force_all_required)

    query: str = Field(
        description="Поисковый запрос — формулируй конкретно и развёрнуто для лучших результатов"
    )
    k: int = Field(
        default=5,
        description="Количество документов для возврата (по умолчанию 5, максимум 20)"
    )
    collection: str | None = Field(
        default=None,
        description="Коллекция для поиска (опционально, по умолчанию — основная)"
    )


@tool(args_schema=RetrieverToolInput)
async def retriever_tool(
    query: str,
    k: int = 5,
    collection: str | None = None,
) -> str:
    """Поиск информации в базе знаний по семантическому сходству.

    Используй этот инструмент для получения информации о:
    - Проектах и застройщиках (описания, характеристики, условия)
    - Районах и локациях (инфраструктура, преимущества, особенности)
    - Правилах покупки недвижимости для иностранцев
    - Налогах и сборах при покупке/владении
    - Визовых программах для инвесторов
    - Рынке недвижимости в целом

    Args:
        query: Поисковый запрос — формулируй конкретно и развёрнуто для лучших результатов.
               Примеры хороших запросов:
               - "инфраструктура и удобства района Dubai Marina"
               - "налоги при покупке недвижимости в Таиланде для иностранцев"
               - "условия рассрочки от застройщика Emaar"
        k: Количество документов для возврата (по умолчанию 5, максимум 20)
        collection: Коллекция для поиска (опционально, по умолчанию — основная)

    Returns:
        Форматированный текст с найденными документами и их содержимым.

    Когда использовать:
        ✓ Клиент спрашивает о конкретном проекте или застройщике
        ✓ Вопросы о районах, инфраструктуре, локациях
        ✓ Вопросы о налогах, визах, правилах покупки
        ✓ Общие вопросы о рынке недвижимости

    Когда НЕ использовать:
        ✗ Поиск конкретных апартаментов по параметрам → используй search_apartments
    """
    logger.info(f"Retriever tool called", query=query[:100], k=k)

    try:
        # Get vector store
        vector_store = get_vector_store()

        # Search documents
        k = min(k, 20)  # Limit max results
        docs = await vector_store.search(query=query, k=k)

        if not docs:
            return "No relevant documents found for your query."

        # Format results
        result = _format_documents(docs)

        logger.info(f"Retriever tool found {len(docs)} documents")
        return result

    except Exception as e:
        logger.error(f"Retriever tool error: {e}")
        return f"Error searching documents: {str(e)}"


@tool
async def retriever_with_scores_tool(
    query: str,
    k: int = 5,
    min_score: float = 0.5,
) -> str:
    """Search documents with relevance scores.

    Similar to retriever_tool but also returns similarity scores.
    Useful when you need to filter by relevance threshold.

    Args:
        query: Search query
        k: Number of documents to return
        min_score: Minimum similarity score (0.0 to 1.0).
                  Documents below this threshold are filtered out.

    Returns:
        Formatted string with documents, scores, and metadata.
    """
    logger.info(f"Retriever with scores called", query=query[:100], k=k, min_score=min_score)

    try:
        vector_store = get_vector_store()

        results = await vector_store.search_with_scores(query=query, k=k)

        # Filter by min_score
        filtered = [(doc, score) for doc, score in results if score >= min_score]

        if not filtered:
            return f"No documents found with similarity score >= {min_score}"

        # Format with scores
        result = _format_documents_with_scores(filtered)

        logger.info(f"Found {len(filtered)} documents above threshold")
        return result

    except Exception as e:
        logger.error(f"Retriever with scores error: {e}")
        return f"Error searching documents: {str(e)}"


def _format_documents(docs: List[Document]) -> str:
    """Format documents for LLM consumption."""
    if not docs:
        return "No documents found."

    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        project = doc.metadata.get("project_id", "")

        header = f"[Document {i}]"
        if project:
            header += f" (Project: {project})"

        formatted.append(f"{header}\nSource: {source}\n{doc.page_content}\n")

    return "\n---\n".join(formatted)


def _format_documents_with_scores(results: List[tuple[Document, float]]) -> str:
    """Format documents with similarity scores."""
    if not results:
        return "No documents found."

    formatted = []
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "Unknown")
        project = doc.metadata.get("project_id", "")

        header = f"[Document {i}] Score: {score:.3f}"
        if project:
            header += f" | Project: {project}"

        formatted.append(f"{header}\nSource: {source}\n{doc.page_content}\n")

    return "\n---\n".join(formatted)


# === Convenience Functions ===


async def search_documents(
    query: str,
    k: int = 5,
    vector_store: DocumentVectorStore | None = None,
) -> List[Document]:
    """
    Direct function for searching documents (not as tool).

    Args:
        query: Search query
        k: Number of results
        vector_store: Optional vector store instance (DI)

    Returns:
        List of Document objects
    """
    if vector_store is None:
        vector_store = get_vector_store()

    return await vector_store.search(query=query, k=k)


def get_retriever(search_kwargs: dict | None = None):
    """
    Get LangChain Retriever for use in chains.

    Args:
        search_kwargs: Search parameters (k, filter, etc.)

    Returns:
        LangChain BaseRetriever
    """
    vector_store = get_vector_store()
    return vector_store.as_retriever(search_kwargs=search_kwargs)
