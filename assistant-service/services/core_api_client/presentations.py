"""Клиент для работы с презентациями в Core API."""

from __future__ import annotations

import structlog
from typing import Any, Optional, List, Dict
from uuid import UUID

from .base_client import CoreApiClient
from .exceptions import CoreApiException

logger = structlog.get_logger(__name__)


class PresentationsClient:
    """Клиент для работы с презентациями через Core API."""

    def __init__(self, api_client: CoreApiClient):
        """
        Initialize presentations client.
        
        Args:
            api_client: Base Core API client instance
        """
        self.api_client = api_client
        self.base_path = "/api/presentations"
        logger.info("Initialized PresentationsClient")

    async def list(self, limit: int = 10, offset: int = 0) -> dict[str, Any]:
        """
        Получить список презентаций.
        
        Args:
            limit: Количество записей
            offset: Смещение для пагинации
            
        Returns:
            Dict с презентациями и метаданными пагинации
        """
        # Core API возвращает пустой результат без параметров,
        # но работает с явными параметрами
        endpoint = f"{self.base_path}?limit={limit}&offset={offset}"
        return await self.api_client._get(endpoint)

    async def get(self, presentation_id: str | UUID) -> dict[str, Any]:
        """
        Получить презентацию по ID.
        
        Args:
            presentation_id: ID презентации
            
        Returns:
            Dict с данными презентации
        """
        endpoint = f"{self.base_path}/{presentation_id}"
        return await self.api_client._get(endpoint)

    async def get_by_project(self, project_id: str | UUID) -> dict[str, Any]:
        """
        Получить презентацию по ID проекта.
        
        Args:
            project_id: ID проекта
            
        Returns:
            Dict с данными презентации
        """
        endpoint = f"/api/projects/{project_id}/presentation"
        return await self.api_client._get(endpoint)

    async def create(
        self,
        project_id: str | UUID,
        template_name: Optional[str] = None,
        slide_sequence: Optional[list[str]] = None,
        slides_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Создать новую презентацию (JSON-only).
        
        Args:
            project_id: ID проекта
            template_name: Название шаблона (например, "serene")
            slide_sequence: Последовательность слайдов
            slides_data: JSON данные для слайдов
            
        Returns:
            Dict с созданной презентацией
        """
        import json
        
        data = {
            "projectId": str(project_id),
        }
        
        if template_name:
            data["templateName"] = template_name
            
        if slide_sequence:
            data["slideSequence"] = json.dumps(slide_sequence)
            
        if slides_data:
            data["slidesData"] = json.dumps(slides_data)
        
        return await self.api_client._post(self.base_path, data=data)

    async def update(
        self,
        presentation_id: str | UUID,
        template_name: Optional[str] = None,
        slide_sequence: Optional[list[str]] = None,
        slides_data: Optional[dict[str, Any]] = None,
        quality_assured: Optional[bool] = None,
        generation_attempts: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Обновить презентацию (JSON-only).
        
        Args:
            presentation_id: ID презентации
            template_name: Название шаблона
            slide_sequence: Последовательность слайдов
            slides_data: JSON данные для слайдов
            quality_assured: Флаг качества
            generation_attempts: Количество попыток генерации
            
        Returns:
            Dict с обновленной презентацией
        """
        import json
        
        data = {}
            
        if template_name is not None:
            data["templateName"] = template_name
            
        if slide_sequence is not None:
            data["slideSequence"] = json.dumps(slide_sequence)
            
        if slides_data is not None:
            data["slidesData"] = json.dumps(slides_data)
            
        if quality_assured is not None:
            data["qualityAssured"] = quality_assured
            
        if generation_attempts is not None:
            data["generationAttempts"] = generation_attempts
        
        endpoint = f"{self.base_path}/{presentation_id}"
        return await self.api_client._patch(endpoint, data=data)

    async def delete(self, presentation_id: str | UUID) -> dict[str, Any]:
        """
        Удалить презентацию.
        
        Args:
            presentation_id: ID презентации
            
        Returns:
            Dict с результатом удаления
        """
        endpoint = f"{self.base_path}/{presentation_id}"
        return await self.api_client._delete(endpoint)

    async def render(self, presentation_id: str | UUID) -> str:
        """
        Отрендерить презентацию.
        
        Args:
            presentation_id: ID презентации
            
        Returns:
            HTML контент отрендеренной презентации
        """
        endpoint = f"{self.base_path}/{presentation_id}/render"
        response = await self.api_client._get(endpoint)
        return response.get("html", "")

    async def save_generated_presentation(
        self,
        project_id: str | UUID,
        html_template: Optional[str],
        template_data: dict[str, Any],
        template_name: str = "serene",
        quality_assured: bool = False,
    ) -> dict[str, Any]:
        """
        Сохранить сгенерированную презентацию из workflow.
        
        Args:
            project_id: ID проекта
            html_template: HTML шаблон (может быть None для JSON-only mode)
            template_data: Данные для рендеринга (slides, metadata)
            template_name: Название использованного шаблона
            quality_assured: Прошла ли презентация QA
            
        Returns:
            Dict с сохраненной презентацией
        """
        # Извлекаем данные из template_data
        slides = template_data.get("slides", [])
        slide_sequence = [slide["type"] for slide in slides]
        
        # Создаем slides_data из slides
        slides_data = {
            "project": template_data.get("project", {}),
            "slides": slides,
            "metadata": template_data.get("metadata", {})
        }
        
        try:
            # Сначала пытаемся получить существующую презентацию
            existing = await self.get_by_project(project_id)
            
            # Если существует, обновляем
            logger.info(f"📝 Updating existing presentation {existing['id']} for project {project_id}")
            logger.info(f"📊 Update data: template_name={template_name}, slides_count={len(slides)}, quality={quality_assured}")
            
            if html_template:
                logger.info(f"📄 HTML size: {len(html_template)} chars")
            else:
                logger.info(f"📄 JSON-only mode: no HTML template")
            logger.info(f"📊 slides_data size: {len(str(slides_data))} chars")
            
            # Безопасно получаем generation_attempts
            current_attempts = existing.get("generationAttempts") or existing.get("generation_attempts") or 0
            
            result = await self.update(
                presentation_id=existing["id"],
                template_name=template_name,
                slide_sequence=slide_sequence,
                slides_data=slides_data,
                quality_assured=quality_assured,
                generation_attempts=current_attempts + 1,
            )
            logger.info(f"✅ Presentation updated successfully: {result.get('id')}")
            return result
            
        except CoreApiException:
            # Если не существует, создаем новую
            logger.info(f"📝 Creating new presentation for project {project_id}")
            if html_template:
                logger.info(f"📄 With HTML template ({len(html_template)} chars)")
            else:
                logger.info(f"📄 JSON-only mode")
                
            return await self.create(
                project_id=project_id,
                template_name=template_name,
                slide_sequence=slide_sequence,
                slides_data=slides_data,
            )