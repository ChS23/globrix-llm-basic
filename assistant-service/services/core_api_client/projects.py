"""Projects client для Core API."""

import logging
from typing import Dict, Any, List, Optional

from .schemas import ProjectInfo

logger = logging.getLogger(__name__)


class ProjectsClient:
    """Клиент для работы с проектами."""

    def __init__(self, core_client):
        """Инициализация клиента с Core API client."""
        self.client = core_client

    # ============ Projects ============

    async def get_project_info(self, project_id: str) -> ProjectInfo:
        """Получение информации о проекте.

        Args:
            project_id: UUID проекта

        Returns:
            ProjectInfo: Информация о проекте
        """
        logger.debug(f"Getting project info for project_id: {project_id}")

        response = await self.client._get(f"/api/projects/{project_id}")
        return ProjectInfo.model_validate(response)

    async def list_projects(
        self,
        developer_id: str | None = None,
        project_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> List[ProjectInfo]:
        """Получение списка проектов.

        Args:
            developer_id: Фильтр по разработчику
            project_type: Фильтр по типу проекта
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            List[ProjectInfo]: Список проектов
        """
        logger.debug("Getting projects list")

        params = {}
        if developer_id:
            params["developer_id"] = developer_id
        if project_type:
            params["project_type"] = project_type
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        params["is_published"] = "True"

        response = await self.client._get("/api/projects", params=params)
        # OpenAPI схема показывает что проекты в response["items"]
        return [ProjectInfo.model_validate(project) for project in response.get("items", [])]