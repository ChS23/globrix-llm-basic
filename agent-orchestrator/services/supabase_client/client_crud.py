import structlog
from typing import Optional, List, Dict, Any

from .base_client import SupabaseClientService

logger = structlog.get_logger(__name__)


class ClientCRUD:
    """Асинхронные CRUD операции для таблицы client."""

    def __init__(self, supabase_service: SupabaseClientService):
        self.supabase = supabase_service
        self.table_name = "client"

    async def create(self) -> Dict[str, Any]:
        """Создание нового клиента.

        Returns:
            Dict с данными созданного клиента (id, created_at)

        Raises:
            Exception: При ошибке создания
        """
        try:
            client = await self.supabase.get_client()
            result = await client.table(self.table_name).insert({}).execute()
            logger.info(f"Created new client: {result.data[0]}")
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to create client: {e}")
            raise

    async def get_by_id(self, client_id: int) -> Optional[Dict[str, Any]]:
        """Получение клиента по ID.

        Args:
            client_id: ID клиента

        Returns:
            Dict с данными клиента или None если не найден
        """
        try:
            client = await self.supabase.get_client()
            result = await client.table(self.table_name).select("*").eq("id", client_id).execute()
            if result.data:
                logger.debug(f"Found client {client_id}")
                return result.data[0]
            logger.debug(f"Client {client_id} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to get client {client_id}: {e}")
            raise

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение всех клиентов с пагинацией.

        Args:
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            List клиентов
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
            logger.debug(f"Retrieved {len(result.data)} clients")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get clients: {e}")
            raise

    async def delete(self, client_id: int) -> bool:
        """Удаление клиента по ID.

        Args:
            client_id: ID клиента

        Returns:
            True если удален успешно

        Raises:
            Exception: При ошибке удаления
        """
        try:
            client = await self.supabase.get_client()
            result = await client.table(self.table_name).delete().eq("id", client_id).execute()
            logger.info(f"Deleted client {client_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete client {client_id}: {e}")
            raise

    async def count(self) -> int:
        """Получение количества клиентов.

        Returns:
            Количество записей в таблице
        """
        try:
            client = await self.supabase.get_client()
            result = await client.table(self.table_name).select("id", count="exact").execute()
            count = result.count if result.count is not None else 0
            logger.debug(f"Total clients count: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to count clients: {e}")
            raise
