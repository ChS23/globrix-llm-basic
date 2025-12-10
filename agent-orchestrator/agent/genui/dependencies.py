"""Dependency Injection для GenUI Agent.

Используется FastAPI DI для управления зависимостями вместо глобальных переменных.
"""

import os
import httpx
import structlog
from functools import lru_cache
from typing import Dict, Any, Optional

from services.supabase_client.base_client import SupabaseClientService
from services.supabase_client.deal_crud import DealCRUD

logger = structlog.get_logger(__name__)


# === Component Schema Service ===


class ComponentSchemaService:
    """Service for fetching and caching UI component schemas from frontend."""

    def __init__(self, frontend_url: str):
        self.frontend_url = frontend_url
        self._cache: Optional[Dict[str, Any]] = None

    async def get_schemas(self) -> Dict[str, Any]:
        """Fetch UI component schemas from frontend API.

        Кэширует схемы для последующих вызовов.

        Returns:
            Dict со схемами всех компонентов

        Raises:
            Exception: При ошибке запроса к API
        """
        if self._cache is not None:
            return self._cache

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.frontend_url}/api/ui-components")
                response.raise_for_status()
                data = response.json()

                self._cache = data.get("schemas", {})
                logger.info(
                    f"Fetched {len(self._cache)} component schemas from frontend"
                )

                return self._cache

        except Exception as e:
            logger.error(f"Failed to fetch component schemas: {e}")
            raise


@lru_cache()
def get_supabase_service() -> SupabaseClientService:
    """Get singleton instance of Supabase service.

    Кэшируется через lru_cache для переиспользования.
    """
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")

    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

    return SupabaseClientService.get_instance(
        url=supabase_url,
        key=supabase_key
    )


def get_deal_crud() -> DealCRUD:
    """Get DealCRUD instance.

    Dependency для FastAPI endpoints и внутренних функций.
    """
    supabase_service = get_supabase_service()
    return DealCRUD(supabase_service)


@lru_cache()
def get_component_schema_service() -> ComponentSchemaService:
    """Get singleton instance of ComponentSchemaService.

    Кэширует схемы компонентов для переиспользования.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
    return ComponentSchemaService(frontend_url=frontend_url)
