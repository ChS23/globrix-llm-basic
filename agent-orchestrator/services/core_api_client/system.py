import logging
from typing import Any, Dict

from .schemas import HealthCheckResponse, VersionInfo

logger = logging.getLogger(__name__)


class SystemClient:
    """Клиент для системных операций Core API.
    Использует Pydantic схемы для типизации данных.
    """

    def __init__(self, core_client):
        self.client = core_client

    async def health_check(self) -> HealthCheckResponse:
        """Проверка состояния системы.

        Returns:
            HealthCheckResponse: Статус здоровья системы
        """
        logger.debug("Performing health check")

        response = await self.client._get("/api/v1/system/health")
        return HealthCheckResponse.model_validate(response)

    async def get_version(self) -> VersionInfo:
        """Получение информации о версии API.

        Returns:
            VersionInfo: Информация о версии
        """
        logger.debug("Getting version info")

        response = await self.client._get("/api/v1/system/version")
        return VersionInfo.model_validate(response)

    async def get_metrics(self) -> dict[str, Any]:
        """Получение метрик системы.

        Returns:
            Dict[str, Any]: Системные метрики
        """
        logger.debug("Getting system metrics")

        return await self.client._get("/api/v1/system/metrics")

    async def get_database_status(self) -> dict[str, Any]:
        """Проверка состояния базы данных.

        Returns:
            Dict[str, Any]: Статус БД
        """
        logger.debug("Checking database status")

        return await self.client._get("/api/v1/system/database/status")

    async def get_queue_status(self) -> dict[str, Any]:
        """Проверка состояния очередей RabbitMQ.

        Returns:
            Dict[str, Any]: Статус очередей
        """
        logger.debug("Checking queue status")

        return await self.client._get("/api/v1/system/queues/status")

    async def get_storage_status(self) -> dict[str, Any]:
        """Проверка состояния хранилища (Google Drive).

        Returns:
            Dict[str, Any]: Статус хранилища
        """
        logger.debug("Checking storage status")

        return await self.client._get("/api/v1/system/storage/status")

    async def ping(self) -> dict[str, str]:
        """Простая проверка доступности API.

        Returns:
            Dict[str, str]: Ответ пинга
        """
        logger.debug("Pinging API")

        return await self.client._get("/api/v1/system/ping")

    async def get_dependencies_status(self) -> dict[str, Any]:
        """Проверка состояния всех зависимостей.

        Returns:
            Dict[str, Any]: Статус всех зависимостей
        """
        logger.debug("Checking dependencies status")

        return await self.client._get("/api/v1/system/dependencies")
