"""Client для работы с apartments API."""

import logging
from typing import Any

from .base_client import CoreApiClient

logger = logging.getLogger(__name__)


class ApartmentsClient:
    """Client для работы с apartments API."""

    def __init__(self, client: CoreApiClient):
        self.client = client

    async def list_apartments(
        self,
        project_id: str | None = None,
        apartment_type: str | None = None,
        status: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_area: float | None = None,
        max_area: float | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Получить список квартир с фильтрацией.

        Args:
            project_id: UUID проекта для фильтрации
            apartment_type: Тип квартиры (studio, 1br, 2br, 3br, 4br, penthouse, duplex, loft)
            status: Статус квартиры (available, sold, reserved, etc.)
            min_price: Минимальная цена
            max_price: Максимальная цена
            min_area: Минимальная площадь (кв.м)
            max_area: Максимальная площадь (кв.м)
            limit: Количество результатов (1-100)
            offset: Смещение для пагинации

        Returns:
            Dict с квартирами и метаданными
        """
        params = {
            "limit": limit,
            "offset": offset
        }

        # Добавляем фильтры только если они заданы
        if project_id:
            params["project_id"] = project_id
        if apartment_type:
            params["type"] = apartment_type
        if status:
            params["status"] = status
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if min_area is not None:
            params["min_area"] = min_area
        if max_area is not None:
            params["max_area"] = max_area

        logger.info("Fetching apartments with params", extra={"params": params})

        try:
            response = await self.client._get("/api/apartments", params=params)
            logger.info("Successfully fetched apartments", extra={
                "count": len(response.get('items', [])),
                "total": response.get('total', 0)
            })
            return response
        except Exception as e:
            logger.error("Error fetching apartments", extra={"error": str(e)})
            raise

    async def get_apartment(self, apartment_id: str) -> dict[str, Any]:
        """Получить информацию о конкретной квартире.

        Args:
            apartment_id: UUID квартиры

        Returns:
            Dict с информацией о квартире
        """
        logger.info("Fetching apartment", extra={"apartment_id": apartment_id})

        try:
            response = await self.client._get(f"/api/apartments/{apartment_id}")
            logger.info("Successfully fetched apartment", extra={"apartment_id": apartment_id})
            return response
        except Exception as e:
            logger.error("Error fetching apartment", extra={
                "apartment_id": apartment_id,
                "error": str(e)
            })
            raise

    async def get_apartments_by_project(
        self,
        project_id: str,
        apartment_type: str | None = None,
        status: str | None = None,
        limit: int = 1000
    ) -> list[dict[str, Any]]:
        """Получить все квартиры в проекте.

        Convenience method для получения всех квартир в проекте
        с опциональной фильтрацией по типу и статусу.

        Args:
            project_id: UUID проекта
            apartment_type: Тип квартиры для фильтрации
            status: Статус для фильтрации
            limit: Максимальное количество результатов

        Returns:
            List квартир в проекте
        """
        response = await self.list_apartments(
            project_id=project_id,
            apartment_type=apartment_type,
            status=status,
            limit=limit,
            offset=0
        )
        return response.get("items", [])

    async def get_apartment_types_by_project(self, project_id: str) -> list[str]:
        """Получить доступные типы квартир в проекте.

        Args:
            project_id: UUID проекта

        Returns:
            List доступных типов квартир
        """
        apartments = await self.get_apartments_by_project(project_id)
        
        apartment_types = set()
        for apt in apartments:
            apt_type = apt.get("type")
            if apt_type:
                apartment_types.add(apt_type)
        
        return sorted(list(apartment_types))

    async def get_price_range_by_project(
        self,
        project_id: str,
        apartment_type: str | None = None
    ) -> dict[str, Any]:
        """Получить диапазон цен в проекте.

        Args:
            project_id: UUID проекта
            apartment_type: Тип квартиры для фильтрации

        Returns:
            Dict с минимальной, максимальной и средней ценой
        """
        apartments = await self.get_apartments_by_project(
            project_id=project_id,
            apartment_type=apartment_type
        )
        
        prices = []
        areas = []
        currency = "THB"
        
        for apt in apartments:
            price = apt.get("price")
            if price and price != "null" and float(price) > 0:
                prices.append(float(price))
                
            area = apt.get("area")
            if area and area != "null" and float(area) > 0:
                areas.append(float(area))
                
            # Получаем валюту из первой квартиры
            if currency == "THB":
                apt_currency = apt.get("currency")
                if apt_currency:
                    currency = apt_currency

        if not prices:
            return {
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "currency": currency,
                "total_units": len(apartments),
                "units_with_pricing": 0
            }

        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)

        result = {
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "currency": currency,
            "total_units": len(apartments),
            "units_with_pricing": len(prices)
        }

        # Добавляем статистику по площади если доступна
        if areas:
            min_area = min(areas)
            max_area = max(areas)
            avg_area = sum(areas) / len(areas)
            
            result.update({
                "min_area": min_area,
                "max_area": max_area,
                "avg_area": avg_area,
                "min_price_per_sqm": min_price / max_area,
                "max_price_per_sqm": max_price / min_area,
                "avg_price_per_sqm": avg_price / avg_area
            })

        return result