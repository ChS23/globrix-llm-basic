import logging

from .schemas import (
    DocumentChunk,
    DocumentChunkCreate,
    DocumentChunkInfo,
    DocumentChunksResponse,
    SimilaritySearchRequest,
    SimilaritySearchResponse,
)

logger = logging.getLogger(__name__)


class DocumentChunksClient:
    """Клиент для работы с document chunks через Core API.
    Использует Pydantic схемы для типизации данных.
    """

    def __init__(self, core_client):
        self.client = core_client

    async def create_batch(
        self, file_id: str, chunks: list[DocumentChunk]
    ) -> DocumentChunksResponse:
        """Создание chunks документа в батче.

        Args:
            file_id: UUID файла
            chunks: Список chunks для создания

        Returns:
            DocumentChunksResponse: Созданные chunks с ID
        """
        logger.debug(f"Creating {len(chunks)} chunks for file_id: {file_id}")

        create_data = DocumentChunkCreate(file_id=file_id, chunks=chunks)

        response = await self.client._post(  # type: ignore
            "/api/document-chunks/batch", json_data=create_data.model_dump()
        )

        return DocumentChunksResponse.model_validate(response)

    async def get_by_file_id(self, file_id: str) -> DocumentChunksResponse:
        """Получение всех chunks файла.

        Args:
            file_id: UUID файла

        Returns:
            DocumentChunksResponse: Список chunks файла
        """
        logger.debug(f"Getting chunks for file_id: {file_id}")

        response = await self.client._get(f"/api/v1/document-chunks/file/{file_id}")
        return DocumentChunksResponse.model_validate(response)

    async def get_by_id(self, chunk_id: str) -> DocumentChunkInfo:
        """Получение конкретного chunk по ID.

        Args:
            chunk_id: UUID chunk

        Returns:
            DocumentChunkInfo: Информация о chunk
        """
        logger.debug(f"Getting chunk by id: {chunk_id}")

        response = await self.client._get(f"/api/v1/document-chunks/{chunk_id}")
        return DocumentChunkInfo.model_validate(response)

    async def search_similar(
        self, embedding: list[float], limit: int = 10, threshold: float | None = None
    ) -> SimilaritySearchResponse:
        """Поиск похожих chunks по вектору эмбеддинга.

        Args:
            embedding: Вектор эмбеддинга для поиска
            limit: Максимальное количество результатов
            threshold: Минимальный порог схожести

        Returns:
            SimilaritySearchResponse: Похожие chunks с оценками
        """
        logger.debug(f"Searching similar chunks, limit: {limit}")

        search_request = SimilaritySearchRequest(
            embedding=embedding, limit=limit, threshold=threshold
        )

        response = await self.client._post(
            "/api/v1/document-chunks/search", json_data=search_request.model_dump(exclude_none=True)
        )

        return SimilaritySearchResponse.model_validate(response)

    async def delete_by_file_id(self, file_id: str) -> dict:
        """Удаление всех chunks файла.

        Args:
            file_id: UUID файла

        Returns:
            dict: Результат операции удаления
        """
        logger.debug(f"Deleting chunks for file_id: {file_id}")

        return await self.client._delete(f"/api/v1/document-chunks/file/{file_id}")

    async def delete_by_id(self, chunk_id: str) -> dict:
        """Удаление конкретного chunk.

        Args:
            chunk_id: UUID chunk

        Returns:
            dict: Результат операции удаления
        """
        logger.debug(f"Deleting chunk by id: {chunk_id}")

        return await self.client._delete(f"/api/v1/document-chunks/{chunk_id}")

    async def update_embedding(self, chunk_id: str, embedding: list[float]) -> DocumentChunkInfo:
        """Обновление эмбеддинга для chunk.

        Args:
            chunk_id: UUID chunk
            embedding: Новый вектор эмбеддинга

        Returns:
            DocumentChunkInfo: Обновленная информация о chunk
        """
        logger.debug(f"Updating embedding for chunk_id: {chunk_id}")

        response = await self.client._patch(
            f"/api/v1/document-chunks/{chunk_id}/embedding", json_data={"embedding": embedding}
        )

        return DocumentChunkInfo.model_validate(response)

    async def search_by_text(
        self, query: str, file_id: str | None = None, project_id: str | None = None, limit: int = 10
    ) -> DocumentChunksResponse:
        """Текстовый поиск по chunks.

        Args:
            query: Поисковый запрос
            file_id: Ограничить поиск конкретным файлом
            project_id: Ограничить поиск конкретным проектом
            limit: Максимальное количество результатов

        Returns:
            DocumentChunksResponse: Найденные chunks
        """
        logger.debug(f"Text search for query: {query[:50]}...")

        params = {"query": query, "limit": limit}
        if file_id:
            params["file_id"] = file_id
        if project_id:
            params["project_id"] = project_id

        response = await self.client._get("/api/v1/document-chunks/search-text", params=params)

        return DocumentChunksResponse.model_validate(response)

    async def get_stats_by_file(self, file_id: str) -> dict:
        """Получение статистики по chunks файла.

        Args:
            file_id: UUID файла

        Returns:
            dict: Статистика chunks файла
        """
        logger.debug(f"Getting chunks stats for file_id: {file_id}")

        return await self.client._get(f"/api/v1/document-chunks/file/{file_id}/stats")
