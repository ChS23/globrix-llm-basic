# agent/tools/apartments_search.py

from typing import List, Dict, Optional
from pydantic import BaseModel
from services.core_api_client.apartments import ApartmentsClient
from services.core_api_client.base_client import CoreApiClient
from services.core_api_client.schemas import ApartmentType, UnitStatus

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

async def apartments_search(filters: ApartmentSearchFilter) -> List[Dict]:
    """
    Вызывает API для поиска апартаментов по фильтрам.
    """
    # Подключение к API (нужно будет настроить URL и аутентификацию)
    client = CoreApiClient(
        base_url="http://core-api:8000",  # Замените на реальный URL
        api_key="your-api-key"            # Если нужен
    )
    apartments_client = ApartmentsClient(client=client)

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
        return response.get("items", [])
    except Exception as e:
        print(f"Ошибка при поиске апартаментов: {e}")
        return []