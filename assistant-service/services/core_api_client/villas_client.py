"""Client для работы с villas API."""

import logging
from typing import Any

from .base_client import CoreApiClient

logger = logging.getLogger(__name__)


class VillasClient:
    """Client для работы с villas API."""

    def __init__(self, client: CoreApiClient):
        self.client = client
        
    async def list_villas(
        self,
        project_id: str | None = None,
        villa_type: str | None = None,
        status: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_area: float | None = None,
        max_area: float | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> dict[str, Any]:
        """Получить список вилл с фильтрацией.
        
        Args:
            project_id: UUID проекта для фильтрации
            villa_type: Тип виллы (pool_villa, beachfront_villa, hillside_villa, etc.)
            status: Статус виллы (available, sold, reserved, etc.)
            min_price: Минимальная цена
            max_price: Максимальная цена
            min_area: Минимальная площадь (кв.м)
            max_area: Максимальная площадь (кв.м)
            limit: Количество результатов (1-100)
            offset: Смещение для пагинации
            
        Returns:
            Dict с виллами и метаданными
        """
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        # Добавляем фильтры только если они заданы
        if project_id:
            params["project_id"] = project_id
        if villa_type:
            params["type"] = villa_type
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
            
        logger.info("Fetching villas with params", extra={"params": params})
        
        try:
            response = await self.client._get("/api/villas", params=params)
            logger.info("Successfully fetched villas", extra={
                "count": len(response.get('items', [])),
                "total": response.get('total', 0)
            })
            return response
        except Exception as e:
            logger.error("Error fetching villas", extra={"error": str(e)})
            raise
    
    async def get_villas_by_project(self, project_id: str) -> list[dict[str, Any]]:
        """Get all villas in a specific project.
        
        Args:
            project_id: UUID of the project
            
        Returns:
            List of villa dictionaries
        """
        result = await self.list_villas(project_id=project_id, limit=1000)
        return result.get("items", [])
    
    async def get_villa_types_by_project(self, project_id: str) -> list[str]:
        """Get unique villa types in a project.
        
        Args:
            project_id: UUID of the project
            
        Returns:
            List of villa type strings
        """
        villas = await self.get_villas_by_project(project_id)
        
        # Extract unique types
        villa_types = set()
        for villa in villas:
            if villa_type := villa.get("type"):
                villa_types.add(villa_type)
        
        return sorted(list(villa_types))
    
    async def get_price_range_by_project(
        self,
        project_id: str,
        villa_type: str | None = None
    ) -> dict[str, Any]:
        """Get price range statistics for villas in a project.
        
        Args:
            project_id: UUID of the project
            villa_type: Optional filter by villa type
            
        Returns:
            Dictionary with price statistics
        """
        # Get villas
        villas = await self.get_villas_by_project(project_id)
        
        # Filter by type if specified
        if villa_type:
            villas = [v for v in villas if v.get("type") == villa_type]
        
        # Calculate statistics
        prices = []
        areas = []
        price_per_sqm_list = []
        
        for villa in villas:
            if price := villa.get("price"):
                prices.append(float(price))
                
                if area := villa.get("area"):
                    areas.append(float(area))
                    price_per_sqm_list.append(float(price) / float(area))
        
        if not prices:
            return {
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "total_units": len(villas),
                "units_with_pricing": 0,
                "currency": "THB"
            }
        
        result = {
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "total_units": len(villas),
            "units_with_pricing": len(prices),
            "currency": villas[0].get("currency", "THB") if villas else "THB"
        }
        
        # Add area statistics if available
        if areas:
            result.update({
                "min_area": min(areas),
                "max_area": max(areas),
                "avg_area": sum(areas) / len(areas)
            })
        
        # Add price per sqm statistics
        if price_per_sqm_list:
            result.update({
                "min_price_per_sqm": min(price_per_sqm_list),
                "max_price_per_sqm": max(price_per_sqm_list),
                "avg_price_per_sqm": sum(price_per_sqm_list) / len(price_per_sqm_list)
            })
        
        return result
    
    async def get_villa(self, villa_id: str) -> dict[str, Any]:
        """Получить информацию о конкретной вилле.
        
        Args:
            villa_id: UUID виллы
            
        Returns:
            Dict с информацией о вилле
        """
        logger.info("Fetching villa", extra={"villa_id": villa_id})
        
        try:
            response = await self.client._get(f"/api/villas/{villa_id}")
            logger.info("Successfully fetched villa", extra={"villa_id": villa_id})
            return response
        except Exception as e:
            logger.error("Error fetching villa", extra={
                "villa_id": villa_id,
                "error": str(e)
            })
            raise
    
    async def create_villa(self, villa_data: dict[str, Any]) -> dict[str, Any]:
        """Создать новую виллу.
        
        Args:
            villa_data: Данные виллы
            
        Returns:
            Dict с созданной виллой
        """
        logger.info("Creating villa")
        
        try:
            response = await self.client._post("/api/villas", json=villa_data)
            logger.info("Successfully created villa", extra={"villa_id": response.get('id')})
            return response
        except Exception as e:
            logger.error("Error creating villa", extra={"error": str(e)})
            raise
    
    async def update_villa(self, villa_id: str, villa_data: dict[str, Any]) -> dict[str, Any]:
        """Обновить существующую виллу.
        
        Args:
            villa_id: UUID виллы
            villa_data: Обновленные данные
            
        Returns:
            Dict с обновленной виллой
        """
        logger.info("Updating villa", extra={"villa_id": villa_id})
        
        try:
            response = await self.client._patch(f"/api/villas/{villa_id}", json=villa_data)
            logger.info("Successfully updated villa", extra={"villa_id": villa_id})
            return response
        except Exception as e:
            logger.error("Error updating villa", extra={
                "villa_id": villa_id,
                "error": str(e)
            })
            raise
    
    async def delete_villa(self, villa_id: str) -> None:
        """Удалить виллу.
        
        Args:
            villa_id: UUID виллы
        """
        logger.info("Deleting villa", extra={"villa_id": villa_id})
        
        try:
            await self.client._delete(f"/api/villas/{villa_id}")
            logger.info("Successfully deleted villa", extra={"villa_id": villa_id})
        except Exception as e:
            logger.error("Error deleting villa", extra={
                "villa_id": villa_id,
                "error": str(e)
            })
            raise