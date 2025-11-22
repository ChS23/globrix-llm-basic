"""
Developers client for Core API.
"""

from typing import TYPE_CHECKING, Any

import structlog

from .schemas import DeveloperInfo

if TYPE_CHECKING:
    from . import CoreApiClient

logger = structlog.get_logger(__name__)


class DevelopersClient:
    """Client for developers domain operations."""

    def __init__(self, core_client: "CoreApiClient"):
        self.client = core_client

    async def get_developer_info(self, developer_id: str) -> DeveloperInfo:
        """Получение информации о разработчике.

        Args:
            developer_id: UUID разработчика

        Returns:
            DeveloperInfo: Информация о разработчике
        """
        logger.debug(f"Getting developer info for developer_id: {developer_id}")

        response = await self.client._get(f"/api/developers/{developer_id}")
        return DeveloperInfo.model_validate(response)

    async def list_developers(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[DeveloperInfo]:
        """Получение списка разработчиков.

        Args:
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            List[DeveloperInfo]: Список разработчиков
        """
        logger.debug("Getting developers list")

        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        response = await self.client._get("/api/developers", params=params)
        return [DeveloperInfo.model_validate(dev) for dev in response.get("items", [])]

    async def get_developer_stats(self, developer_id: str) -> dict[str, Any]:
        """Получение статистики по разработчику.

        Args:
            developer_id: UUID разработчика

        Returns:
            Dict[str, Any]: Статистика разработчика
        """
        logger.debug(f"Getting developer stats for developer_id: {developer_id}")

        return await self.client._get(f"/api/developers/{developer_id}/stats")

    async def get_developer_by_project(self, project_id: str) -> DeveloperInfo | None:
        """Получение информации о разработчике по ID проекта.

        Args:
            project_id: UUID проекта

        Returns:
            DeveloperInfo: Информация о разработчике или None
        """
        try:
            # Сначала получаем информацию о проекте
            from .projects import ProjectsClient
            projects_client = ProjectsClient(self.client)
            project_info = await projects_client.get_project_info(project_id)

            if project_info.developer_id:
                return await self.get_developer_info(project_info.developer_id)

            return None
        except Exception as e:
            logger.error(f"Error getting developer by project: {e}")
            return None
