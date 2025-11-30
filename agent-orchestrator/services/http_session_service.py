import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp

from .singleton import SingletonMeta

logger = logging.getLogger(__name__)


class HttpSessionService(metaclass=SingletonMeta):
    """Базовый сервис для управления HTTP сессиями с aiohttp.
    Обеспечивает переиспользование соединений и оптимальную производительность.
    """

    def __init__(
        self,
        timeout: int = 300,  # Увеличиваем таймаут до 5 минут для генерации PDF
        connector_limit: int = 100,
        connector_limit_per_host: int = 30,
        headers: dict[str, str] | None = None,
    ):
        if hasattr(self, "_initialized"):
            return

        # Увеличиваем таймауты для долгих операций
        self._timeout = aiohttp.ClientTimeout(
            total=timeout,
            connect=10,
            sock_read=timeout
        )
        self._connector = aiohttp.TCPConnector(
            limit=connector_limit,
            limit_per_host=connector_limit_per_host,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        self._default_headers = headers or {}
        self._session: aiohttp.ClientSession | None = None
        self._lock = asyncio.Lock()
        self._initialized = True

        logger.info(
            f"Initialized HttpSessionService with timeout={timeout}s, connector_limit={connector_limit}"
        )

    @classmethod
    def get_instance(
        cls,
        timeout: int = 30,
        connector_limit: int = 100,
        connector_limit_per_host: int = 30,
        headers: dict[str, str] | None = None,
    ):
        return cls(
            timeout=timeout,
            connector_limit=connector_limit,
            connector_limit_per_host=connector_limit_per_host,
            headers=headers,
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии (thread-safe)"""
        if self._session is None or self._session.closed:
            async with self._lock:
                if self._session is None or self._session.closed:
                    self._session = aiohttp.ClientSession(
                        timeout=self._timeout,
                        connector=self._connector,
                        headers=self._default_headers,
                    )
                    logger.debug("Created new HTTP session")
        return self._session

    async def request(
        self, method: str, url: str, headers: dict[str, str] | None = None, **kwargs
    ) -> aiohttp.ClientResponse:
        """Выполнение HTTP запроса с автоматическим управлением сессией.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL для запроса
            headers: Дополнительные headers
            **kwargs: Дополнительные параметры для aiohttp

        Returns:
            aiohttp.ClientResponse
        """
        session = await self._get_session()

        # Объединяем headers
        request_headers = self._default_headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = await session.request(
                method=method, url=url, headers=request_headers, **kwargs
            )

            logger.debug(f"{method} {url} -> {response.status}")
            return response

        except Exception as e:
            logger.error(f"HTTP request failed: {method} {url} - {e}")
            raise

    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """GET запрос"""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """POST запрос"""
        return await self.request("POST", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """PATCH запрос"""
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """DELETE запрос"""
        return await self.request("DELETE", url, **kwargs)

    async def download_file(self, url: str, **kwargs) -> bytes:
        """Загрузка файла с автоматическим чтением содержимого.
        Оптимизировано для больших файлов.

        Args:
            url: URL файла для загрузки
            **kwargs: Дополнительные параметры для запроса

        Returns:
            bytes: Содержимое файла
        """
        async with await self.get(url, **kwargs) as response:
            response.raise_for_status()

            # Читаем содержимое по частям для экономии памяти
            content = b""
            async for chunk in response.content.iter_chunked(8192):
                content += chunk

            logger.debug(f"Downloaded file: {len(content)} bytes from {url}")
            return content

    async def json_request(
        self, method: str, url: str, json_data: dict[str, Any] | None = None, **kwargs
    ) -> dict[str, Any]:
        """JSON запрос с автоматическим парсингом ответа.

        Args:
            method: HTTP method
            url: URL для запроса
            json_data: JSON данные для отправки
            **kwargs: Дополнительные параметры

        Returns:
            Dict: Распарсенный JSON ответ
        """
        headers = kwargs.get("headers", {})
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers

        if json_data:
            kwargs["json"] = json_data

        async with await self.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    async def health_check(self, url: str) -> bool:
        """Проверка доступности сервиса.

        Args:
            url: URL для проверки

        Returns:
            bool: True если сервис доступен
        """
        try:
            async with await self.get(url) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Health check failed for {url}: {e}")
            return False

    async def close(self):
        """Закрытие HTTP сессии и освобождение ресурсов"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("HTTP session closed")

        if self._connector and not self._connector.closed:
            await self._connector.close()
            logger.debug("HTTP connector closed")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def get_session_stats(self) -> dict[str, Any]:
        """Получение статистики сессии для мониторинга"""
        if not self._session or self._session.closed:
            return {"status": "closed", "connections": 0}

        connector_info = {}
        if self._connector:
            connector_info = {
                "total_connections": len(self._connector._conns),
                "available_connections": self._connector._limit,
                "acquired_connections": self._connector._acquired_per_host,
            }

        return {
            "status": "active",
            "session_closed": self._session.closed,
            "connector_info": connector_info,
            "timeout": self._timeout.total,
        }
