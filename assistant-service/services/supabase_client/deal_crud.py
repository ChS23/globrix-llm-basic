import structlog
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from .base_client import SupabaseClientService

logger = structlog.get_logger(__name__)


class DealCRUD:
    """Асинхронные CRUD операции для таблицы deal."""

    def __init__(self, supabase_service: SupabaseClientService):
        self.supabase = supabase_service
        self.table_name = "deal"

    async def create(
        self,
        client_id: Optional[int] = None,
        raw_request: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        ui_state: Optional[Dict[str, Any]] = None,
        deal_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Создание новой сделки.

        Args:
            client_id: ID клиента (FK к таблице client)
            raw_request: Сырой текст запроса
            request_params: Параметры запроса в формате JSON
            status: Статус сделки
            ui_state: Состояние UI в формате JSON
            deal_id: UUID сделки (если не указан, генерируется автоматически)

        Returns:
            Dict с данными созданной сделки

        Raises:
            Exception: При ошибке создания
        """
        try:
            data: Dict[str, Any] = {}

            if deal_id is not None:
                data["id"] = str(deal_id)
            else:
                data["id"] = str(uuid4())

            if client_id is not None:
                data["client_id"] = client_id
            if raw_request is not None:
                data["raw_request"] = raw_request
            if request_params is not None:
                data["request_params"] = request_params
            if status is not None:
                data["status"] = status
            if ui_state is not None:
                data["ui_state"] = ui_state

            client = await self.supabase.get_client()
            result = await client.table(self.table_name).insert(data).execute()
            logger.info(f"Created new deal: {result.data[0]['id']}")
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to create deal: {e}")
            raise

    async def get_by_id(self, deal_id: str | UUID) -> Optional[Dict[str, Any]]:
        """Получение сделки по ID.

        Args:
            deal_id: UUID сделки

        Returns:
            Dict с данными сделки или None если не найдена
        """
        try:
            deal_id_str = str(deal_id)
            client = await self.supabase.get_client()
            result = await client.table(self.table_name).select("*").eq("id", deal_id_str).execute()
            if result.data:
                logger.debug(f"Found deal {deal_id_str}")
                return result.data[0]
            logger.debug(f"Deal {deal_id_str} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to get deal {deal_id}: {e}")
            raise

    async def get_by_client_id(self, client_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение всех сделок для конкретного клиента.

        Args:
            client_id: ID клиента
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            List сделок клиента
        """
        try:
            client = await self.supabase.get_client()
            result = await (
                client.table(self.table_name)
                .select("*")
                .eq("client_id", client_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            logger.debug(f"Retrieved {len(result.data)} deals for client {client_id}")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get deals for client {client_id}: {e}")
            raise

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение всех сделок с пагинацией.

        Args:
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            List сделок
        """
        try:
            client = await self.supabase.get_client()
            result = await (
                client.table(self.table_name)
                .select("*")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            logger.debug(f"Retrieved {len(result.data)} deals")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get deals: {e}")
            raise

    async def update(
        self,
        deal_id: str | UUID,
        raw_request: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        ui_state: Optional[Dict[str, Any]] = None,
        client_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Обновление сделки.

        Args:
            deal_id: UUID сделки
            raw_request: Новый сырой текст запроса
            request_params: Новые параметры запроса
            status: Новый статус
            ui_state: Новое состояние UI
            client_id: Новый ID клиента

        Returns:
            Dict с обновленными данными сделки

        Raises:
            Exception: При ошибке обновления
        """
        try:
            data: Dict[str, Any] = {}

            if raw_request is not None:
                data["raw_request"] = raw_request
            if request_params is not None:
                data["request_params"] = request_params
            if status is not None:
                data["status"] = status
            if ui_state is not None:
                data["ui_state"] = ui_state
            if client_id is not None:
                data["client_id"] = client_id

            deal_id_str = str(deal_id)
            client = await self.supabase.get_client()
            result = await client.table(self.table_name).update(data).eq("id", deal_id_str).execute()
            logger.info(f"Updated deal {deal_id_str}")
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to update deal {deal_id}: {e}")
            raise

    async def delete(self, deal_id: str | UUID) -> bool:
        """Удаление сделки по ID.

        Args:
            deal_id: UUID сделки

        Returns:
            True если удалена успешно

        Raises:
            Exception: При ошибке удаления
        """
        try:
            deal_id_str = str(deal_id)
            client = await self.supabase.get_client()
            result = await client.table(self.table_name).delete().eq("id", deal_id_str).execute()
            logger.info(f"Deleted deal {deal_id_str}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete deal {deal_id}: {e}")
            raise

    async def count(self, client_id: Optional[int] = None) -> int:
        """Получение количества сделок.

        Args:
            client_id: Опционально - фильтр по ID клиента

        Returns:
            Количество записей в таблице
        """
        try:
            client = await self.supabase.get_client()
            query = client.table(self.table_name).select("id", count="exact")

            if client_id is not None:
                query = query.eq("client_id", client_id)

            result = await query.execute()
            count = result.count if result.count is not None else 0
            logger.debug(f"Total deals count: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to count deals: {e}")
            raise
