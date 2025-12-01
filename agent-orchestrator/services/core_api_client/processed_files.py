import logging
from typing import List, Optional

from .schemas import (
    FileDownloadLink,
    FilesListResponse,
    FileStatus,
    FileStatusUpdate,
    FileType,
    PaginationParams,
    ProcessedFileInfo,
)

logger = logging.getLogger(__name__)


class ProcessedFilesClient:
    """Клиент для работы с processed files через Core API.
    Использует Pydantic схемы для типизации данных.
    """

    def __init__(self, core_client):
        self.client = core_client

    async def get_by_id(self, file_id: str) -> ProcessedFileInfo:
        """Получение информации о файле по ID.

        Args:
            file_id: UUID файла

        Returns:
            ProcessedFileInfo: Типизированная информация о файле
        """
        logger.debug(f"Getting file info for file_id: {file_id}")
        response = await self.client._get(f"/api/processed-files/{file_id}")
        return ProcessedFileInfo.model_validate(response)

    async def get_download_link(self, file_id: str) -> str:
        """Получение ссылки для загрузки файла из Google Drive.

        Args:
            file_id: UUID файла

        Returns:
            str: URL для загрузки файла
        """
        logger.debug(f"Getting download link for file_id: {file_id}")
        response = await self.client._get(f"/api/processed-files/{file_id}/download-link")
        download_data = FileDownloadLink.model_validate(response)
        return download_data.download_link

    async def update_status(
        self,
        file_id: str,
        status: FileStatus,
        error_message: str | None = None,
        processed_at: str | None = None,
    ) -> ProcessedFileInfo:
        """Обновление статуса обработки файла.

        Args:
            file_id: UUID файла
            status: Новый статус
            error_message: Сообщение об ошибке (для status=FAILED)
            processed_at: Время завершения обработки (ISO format)

        Returns:
            ProcessedFileInfo: Обновленная информация о файле
        """
        logger.debug(f"Updating status for file_id: {file_id} to {status}")

        update_data = FileStatusUpdate(
            status=status, error_message=error_message, processed_at=processed_at
        )

        response = await self.client._patch(
            f"/api/processed-files/{file_id}/status",
            json_data=update_data.model_dump(exclude_none=True),
        )

        return ProcessedFileInfo.model_validate(response)

    async def list_by_project(
        self,
        project_id: str,
        status: FileStatus | None = None,
        file_type: FileType | None = None,
        pagination: PaginationParams | None = None,
    ) -> FilesListResponse:
        """Получение списка файлов по проекту.

        Args:
            project_id: UUID проекта
            status: Фильтр по статусу
            file_type: Фильтр по типу файла
            pagination: Параметры пагинации

        Returns:
            FilesListResponse: Типизированный список файлов
        """
        logger.debug(f"Getting files for project_id: {project_id}")

        params = {"project_id": project_id}
        if status:
            params["status"] = status.value
        if file_type:
            params["file_type"] = file_type.value
        if pagination:
            params.update(pagination.model_dump(exclude_none=True))

        response = await self.client._get("/api/processed-files", params=params)
        return FilesListResponse.model_validate(response)

    async def list_by_developer(
        self,
        developer_id: str,
        status: FileStatus | None = None,
        pagination: PaginationParams | None = None,
    ) -> FilesListResponse:
        """Получение списка файлов по разработчику.

        Args:
            developer_id: UUID разработчика
            status: Фильтр по статусу
            pagination: Параметры пагинации

        Returns:
            FilesListResponse: Типизированный список файлов
        """
        logger.debug(f"Getting files for developer_id: {developer_id}")

        params = {"developer_id": developer_id}
        if status:
            params["status"] = status.value
        if pagination:
            params.update(pagination.model_dump(exclude_none=True))

        response = await self.client._get("/api/processed-files", params=params)
        return FilesListResponse.model_validate(response)

    # Convenience методы с типизацией

    async def mark_as_processing(self, file_id: str) -> ProcessedFileInfo:
        """Помечает файл как обрабатываемый.

        Args:
            file_id: UUID файла

        Returns:
            ProcessedFileInfo: Обновленная информация о файле
        """
        return await self.update_status(file_id, FileStatus.PROCESSING)

    async def mark_as_completed(
        self, file_id: str, processed_at: str | None = None
    ) -> ProcessedFileInfo:
        """Помечает файл как успешно обработанный.

        Args:
            file_id: UUID файла
            processed_at: Время завершения обработки

        Returns:
            ProcessedFileInfo: Обновленная информация о файле
        """
        return await self.update_status(file_id, FileStatus.COMPLETED, processed_at=processed_at)

    async def mark_as_failed(
        self, file_id: str, error_message: str, processed_at: str | None = None
    ) -> ProcessedFileInfo:
        """Помечает файл как failed с сообщением об ошибке.

        Args:
            file_id: UUID файла
            error_message: Описание ошибки
            processed_at: Время обработки

        Returns:
            ProcessedFileInfo: Обновленная информация о файле
        """
        return await self.update_status(
            file_id, FileStatus.FAILED, error_message=error_message, processed_at=processed_at
        )
