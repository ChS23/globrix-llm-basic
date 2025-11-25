"""Модульный клиент для Core API с типизированными схемами."""

from .apartments import ApartmentsClient
from .base_client import CoreApiClient
from .developers import DevelopersClient
from .document_chunks import DocumentChunksClient
from .exceptions import *
from .management import ManagementClient
from .presentations import PresentationsClient
from .processed_files import ProcessedFilesClient
from .projects import ProjectsClient
from .schemas import *
from .system import SystemClient
from .unit_media import UnitMediaClient, UnitMediaInfo, UnitMediaUpdate
from .agent_portal_client import AgentPortalClient
from .villas_client import VillasClient


class FullCoreApiClient(CoreApiClient):
    """Полный клиент Core API с инициализированными domain-клиентами."""

    def __init__(self, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)  # type: ignore

        if not hasattr(self, "_domain_clients_initialized"):
            # Инициализируем domain-специфичные клиенты
            self.processed_files = ProcessedFilesClient(self)
            self.document_chunks = DocumentChunksClient(self)
            self.system = SystemClient(self)
            self.management = ManagementClient(self)
            self.unit_media = UnitMediaClient(self)
            self.apartments = ApartmentsClient(self)
            self.projects = ProjectsClient(self)
            self.developers = DevelopersClient(self)
            self.presentations = PresentationsClient(self)
            self.agent_portal = AgentPortalClient(self)
            self.villas = VillasClient(self)

            self._domain_clients_initialized = True


# Экспортируем основной клиент
__all__ = [
    # Основной клиент
    "FullCoreApiClient",
    "CoreApiClient",
    "ProcessedFilesClient",
    "DocumentChunksClient",
    "SystemClient",
    "ManagementClient",
    "UnitMediaClient",
    "ApartmentsClient",
    "ProjectsClient",
    "PresentationsClient",
    "AgentPortalClient",
    "VillasClient",
    # Схемы
    "ProcessedFileInfo",
    "DocumentChunk",
    "DocumentChunkInfo",
    "ProjectInfo",
    "DeveloperInfo",
    "HealthCheckResponse",
    "FileStatus",
    "FileType",
    "UnitMediaInfo",
    "UnitMediaUpdate",
    "ApartmentInfo",
    "ApartmentSearchParams", 
    "ApartmentsListResponse",
    "PriceRangeInfo",
    "ApartmentType",
    "ApartmentView", 
    "UnitStatus",
    # Исключения
    "CoreApiException",
    "CoreApiHttpException",
    "CoreApiNotFound",
    "CoreApiUnauthorized",
    "CoreApiForbidden",
    "CoreApiServerError",
    "CoreApiConnectionError",
    "CoreApiTimeout",
    "CoreApiValidationError",
]
