import asyncio
import structlog
from typing import Any

from aiohttp import ClientConnectorError, ClientResponseError

from services.http_session_service import HttpSessionService
from ..singleton import SingletonMeta
from .exceptions import (
    CoreApiConnectionError,
    CoreApiForbidden,
    CoreApiHttpException,
    CoreApiNotFound,
    CoreApiServerError,
    CoreApiTimeout,
    CoreApiUnauthorized,
)

logger = structlog.get_logger(__name__)


class CoreApiClient(metaclass=SingletonMeta):
    """Базовый клиент для взаимодействия с Core API.
    Использует HttpSessionService для оптимальной производительности.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        http_session_service: HttpSessionService | None = None,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ):
        if hasattr(self, "_initialized"):
            return

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.http_session = http_session_service
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

        # Headers для аутентификации
        self.auth_headers = {}
        if api_key:
            self.auth_headers["Authorization"] = f"Bearer {api_key}"  # type: ignore
            self.auth_headers["X-Authentication-Key"] = f"{api_key}"  # type: ignore

        # Инициализация domain-клиентов будет в дочерних классах
        self._initialized = True

        logger.info(f"Initialized CoreApiClient for {base_url}")

    @classmethod
    def get_instance(
        cls,
        base_url: str,
        api_key: str | None = None,
        http_session_service: HttpSessionService | None = None,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ):
        return cls(
            base_url=base_url,
            api_key=api_key,
            http_session_service=http_session_service,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
        )

    def _get_full_url(self, endpoint: str) -> str:
        """Построение полного URL из endpoint"""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    def _handle_http_error(self, error: Exception, url: str) -> None:
        """Обработка HTTP ошибок и преобразование в custom exceptions"""
        if isinstance(error, ClientResponseError):
            status_code = error.status
            message = f"HTTP {status_code} error for {url}: {error.message}"

            if status_code == 404:
                raise CoreApiNotFound(message, status_code)
            if status_code == 401:
                raise CoreApiUnauthorized(message, status_code)
            if status_code == 403:
                raise CoreApiForbidden(message, status_code)
            if 500 <= status_code < 600:
                raise CoreApiServerError(message, status_code)
            raise CoreApiHttpException(message, status_code)

        if isinstance(error, ClientConnectorError):
            raise CoreApiConnectionError(f"Connection error for {url}: {error}")
        if isinstance(error, asyncio.TimeoutError):
            raise CoreApiTimeout(f"Request timeout for {url}")
        # Для всех остальных ошибок
        raise CoreApiHttpException(f"Request failed for {url}: {error}")

    async def _request_with_retry(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:  # type: ignore
        """HTTP запрос с retry механизмом и обработкой ошибок.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (без base_url)
            **kwargs: Дополнительные параметры для запроса

        Returns:
            Dict: Parsed JSON response

        Raises:
            CoreApiException: При ошибках запроса
        """
        if not self.http_session:
            raise CoreApiConnectionError("HttpSessionService not initialized")

        url = self._get_full_url(endpoint)

        # Объединяем auth headers с переданными
        headers = kwargs.get("headers", {})  # type: ignore
        headers.update(self.auth_headers)  # type: ignore
        kwargs["headers"] = headers

        last_exception = None

        for attempt in range(self.retry_attempts):
            try:
                logger.warning(f"HTTP REQUEST: {method} {url}")  # Force visibility
                logger.warning(f"Request headers: {kwargs.get('headers', {})}")
                logger.warning(f"Request data: {kwargs.get('data', {})}")

                # Извлекаем data для передачи как json_data, если есть
                json_data = kwargs.pop('data', None)

                # Передаем json_data только если он есть
                if json_data is not None:
                    response_data = await self.http_session.json_request(  # type: ignore
                        method=method, url=url, json_data=json_data, **kwargs  # type: ignore
                    )
                else:
                    response_data = await self.http_session.json_request(  # type: ignore
                        method=method, url=url, **kwargs  # type: ignore
                    )

                logger.debug(f"Successful request: {method} {url}")
                return response_data

            except Exception as e:
                last_exception = e
                logger.warning(f"Request attempt {attempt + 1} failed: {method} {url} - {e}")

                # Не делаем retry для клиентских ошибок (4xx)
                if isinstance(e, ClientResponseError) and 400 <= e.status < 500:
                    break

                # Если это не последняя попытка, ждем перед повтором
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (2**attempt))  # Exponential backoff

        # Обрабатываем последнюю ошибку
        self._handle_http_error(last_exception, url)  # type: ignore

    async def _get(self, endpoint: str, **kwargs) -> dict[str, Any]:  # type: ignore
        """GET запрос"""
        return await self._request_with_retry("GET", endpoint, **kwargs)  # type: ignore

    async def _post(self, endpoint: str, **kwargs) -> dict[str, Any]:  # type: ignore
        """POST запрос"""
        return await self._request_with_retry("POST", endpoint, **kwargs)  # type: ignore

    async def _patch(self, endpoint: str, **kwargs) -> dict[str, Any]:  # type: ignore
        """PATCH запрос"""
        return await self._request_with_retry("PATCH", endpoint, **kwargs)  # type: ignore

    async def _delete(self, endpoint: str, **kwargs) -> dict[str, Any]:  # type: ignore
        """DELETE запрос"""
        return await self._request_with_retry("DELETE", endpoint, **kwargs)  # type: ignore

    async def health_check(self) -> bool:
        """Проверка доступности Core API.

        Returns:
            bool: True если API доступен
        """
        try:
            await self._get("/api/system/health")  # type: ignore
            return True
        except Exception as e:
            logger.warning(f"Core API health check failed: {e}")
            return False

    def get_client_info(self) -> dict[str, Any]:
        """Получение информации о клиенте для мониторинга"""
        return {
            "base_url": self.base_url,
            "has_auth": bool(self.api_key),
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "http_session_active": self.http_session is not None,
        }
