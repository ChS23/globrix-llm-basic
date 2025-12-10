# agent/tools/apartments_search.py

import os
from functools import lru_cache
from typing import List, Dict, Optional

import structlog
from pydantic import BaseModel

from services.core_api_client.apartments import ApartmentsClient
from services.core_api_client.base_client import CoreApiClient
from services.http_session_service import HttpSessionService

logger = structlog.get_logger(__name__)


class ApartmentSearchFilter(BaseModel):
    project_id: Optional[str] = None
    apartment_type: Optional[str] = None  # studio, 1br, 2br, 3br, 4br, penthouse, duplex, loft
    status: Optional[str] = None         # available, sold, reserved
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    limit: int = 20
    offset: int = 0


# === Dependency Injection ===

@lru_cache()
def get_http_session_service() -> HttpSessionService:
    """Get singleton HttpSessionService."""
    return HttpSessionService()


@lru_cache()
def get_core_api_client() -> CoreApiClient:
    """Get singleton CoreApiClient with config from env."""
    base_url = os.getenv("CORE_API_BASE_URL", "https://api.globrix.pro")
    api_key = os.getenv("CORE_API_KEY", "")

    if not api_key:
        logger.warning("CORE_API_KEY not set, API calls may fail")

    http_session = get_http_session_service()

    return CoreApiClient(
        base_url=base_url,
        api_key=api_key,
        http_session_service=http_session,
    )


def get_apartments_client() -> ApartmentsClient:
    """Get ApartmentsClient instance."""
    core_client = get_core_api_client()
    return ApartmentsClient(client=core_client)


# === Tool Function ===

async def apartments_search(
    filters: ApartmentSearchFilter,
    apartments_client: ApartmentsClient | None = None,
) -> List[Dict]:
    """
    Вызывает API для поиска апартаментов по фильтрам.

    Args:
        filters: Фильтры для поиска
        apartments_client: ApartmentsClient instance (DI, optional)

    Returns:
        List апартаментов
    """
    if apartments_client is None:
        apartments_client = get_apartments_client()

    try:
        response = await apartments_client.list_apartments(
            project_id=filters.project_id,
            apartment_type=filters.apartment_type,
            status=filters.status,
            min_price=filters.min_price,
            max_price=filters.max_price,
            min_area=filters.min_area,
            max_area=filters.max_area,
            limit=filters.limit,
            offset=filters.offset
        )

        items = response.get("items", [])
        logger.info(f"Found {len(items)} apartments", extra={
            "total": response.get("total", 0),
            "filters": filters.model_dump(exclude_none=True)
        })

        return items

    except Exception as e:
        logger.error(f"Error searching apartments: {e}")
        return []