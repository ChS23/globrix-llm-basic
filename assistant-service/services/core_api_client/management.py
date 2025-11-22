import logging
from typing import Any, Dict, List, Optional

from .schemas import DeveloperInfo, ProcessingCompleteNotification, ProcessingStats, ProjectInfo

logger = logging.getLogger(__name__)


class ManagementClient:
    """Клиент для управленческих операций Core API.
    Работа с проектами, разработчиками и уведомлениями.
    """

    def __init__(self, core_client):
        self.client = core_client

    # ============ Processing Notifications ============

    async def notify_processing_complete(
        self, file_id: str, processing_stats: ProcessingStats
    ) -> dict[str, Any]:
        """Уведомление о завершении обработки файла.

        Args:
            file_id: UUID файла
            processing_stats: Статистика обработки

        Returns:
            Dict[str, Any]: Результат уведомления
        """
        logger.debug(f"Notifying processing complete for file_id: {file_id}")

        notification = ProcessingCompleteNotification(
            file_id=file_id, processing_stats=processing_stats
        )

        return await self.client._post(
            "/api/v1/management/processing-completed", json_data=notification.model_dump()
        )

    async def notify_processing_started(self, file_id: str) -> dict[str, Any]:
        """Уведомление о начале обработки файла.

        Args:
            file_id: UUID файла

        Returns:
            Dict[str, Any]: Результат уведомления
        """
        logger.debug(f"Notifying processing started for file_id: {file_id}")

        return await self.client._post(
            "/api/v1/management/processing-started", json_data={"file_id": file_id}
        )

    async def notify_processing_failed(
        self, file_id: str, error_message: str, error_details: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Уведомление об ошибке обработки файла.

        Args:
            file_id: UUID файла
            error_message: Сообщение об ошибке
            error_details: Дополнительные детали ошибки

        Returns:
            Dict[str, Any]: Результат уведомления
        """
        logger.debug(f"Notifying processing failed for file_id: {file_id}")

        data = {"file_id": file_id, "error_message": error_message}
        if error_details:
            data["error_details"] = error_details

        return await self.client._post("/api/v1/management/processing-failed", json_data=data)

    # ============ Analytics ============

    async def get_processing_analytics(
        self, project_id: str | None = None, developer_id: str | None = None, days: int | None = 30
    ) -> dict[str, Any]:
        """Получение аналитики по обработке файлов.

        Args:
            project_id: Фильтр по проекту
            developer_id: Фильтр по разработчику
            days: Количество дней для анализа

        Returns:
            Dict[str, Any]: Аналитические данные
        """
        logger.debug("Getting processing analytics")

        params = {"days": days}
        if project_id:
            params["project_id"] = project_id
        if developer_id:
            params["developer_id"] = developer_id

        return await self.client._get("/api/v1/management/analytics", params=params)

    async def get_file_processing_history(self, file_id: str) -> list[dict[str, Any]]:
        """Получение истории обработки файла.

        Args:
            file_id: UUID файла

        Returns:
            List[Dict[str, Any]]: История обработки
        """
        logger.debug(f"Getting processing history for file_id: {file_id}")

        response = await self.client._get(f"/api/v1/management/files/{file_id}/history")
        return response.get("history", [])
