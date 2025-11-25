import structlog
import asyncio
from supabase import acreate_client, AsyncClient
from typing import Optional

from ..singleton import SingletonMeta

logger = structlog.get_logger(__name__)


class SupabaseClientService(metaclass=SingletonMeta):
    """Singleton сервис для работы с Supabase.

    Использует паттерн Singleton для переиспользования подключения.
    Асинхронный клиент для работы с async/await и Realtime.
    """

    def __init__(self, url: str, key: str):
        if hasattr(self, "_initialized"):
            return

        self.url = url
        self.key = key
        self._client: Optional[AsyncClient] = None
        self._client_lock = asyncio.Lock()
        self._initialized = True

        logger.info(f"Initialized SupabaseClientService for {url}")

    async def get_client(self) -> AsyncClient:
        """Async lazy initialization и получение клиента Supabase.

        Thread-safe благодаря использованию asyncio.Lock.
        """
        if self._client is None:
            async with self._client_lock:
                # Double-check после получения lock
                if self._client is None:
                    self._client = await acreate_client(self.url, self.key)
                    logger.info("Supabase async client created")
        return self._client

    @classmethod
    def get_instance(cls, url: str, key: str) -> "SupabaseClientService":
        """Получение singleton instance."""
        return cls(url=url, key=key)

    async def health_check(self) -> bool:
        """Проверка доступности Supabase."""
        try:
            # Простой запрос для проверки соединения
            client = await self.get_client()
            await client.table("client").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.warning(f"Supabase health check failed: {e}")
            return False

    async def close(self) -> None:
        """Закрытие соединения и очистка ресурсов."""
        if self._client is not None:
            try:
                # Попытка закрыть auth сессию
                await self._client.auth.sign_out()
                logger.info("Supabase client closed")
            except Exception as e:
                logger.warning(f"Error closing Supabase client: {e}")
            finally:
                self._client = None

    async def __aenter__(self) -> "SupabaseClientService":
        """Async context manager entry."""
        await self.get_client()
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
