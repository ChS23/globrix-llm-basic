from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FileStatus(StrEnum):
    """Статусы обработки файлов"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileType(StrEnum):
    """Типы файлов"""

    DOCUMENT = "document"
    IMAGE = "image"
    FLOOR_PLAN = "floor_plan"
    PRESENTATION = "presentation"
    PRICE_LIST = "price_list"


# ============ Processed Files Schemas ============


class ProcessedFileInfo(BaseModel):
    """Информация о файле из Core API"""

    id: str
    google_drive_file_id: str = Field(alias="fileLinkId")
    file_name: str = Field(alias="fileName")
    file_type: FileType = Field(alias="fileType")
    mime_type: str = Field(alias="mimeType", default="application/pdf")
    file_size: int | None = Field(alias="fileSize", default=None)
    status: FileStatus
    project_id: str = Field(alias="projectId")
    developer_id: str = Field(alias="developerId")
    folder_path: str | None = Field(alias="folderPath", default=None)
    file_url: str | None = Field(alias="fileUrl", default=None)
    error_message: str | None = Field(alias="errorMessage", default=None)
    created_at: datetime | None = Field(alias="createdAt", default=None)
    processed_at: datetime | None = Field(alias="processedAt", default=None)

    model_config = {"populate_by_name": True}


class FileDownloadLink(BaseModel):
    """Ссылка для загрузки файла"""

    download_link: str


class FileStatusUpdate(BaseModel):
    """Запрос на обновление статуса файла"""

    status: FileStatus
    error_message: str | None = None
    processed_at: datetime | None = None


class FilesListResponse(BaseModel):
    """Ответ со списком файлов"""

    files: list[ProcessedFileInfo]
    total_count: int
    limit: int | None = None
    offset: int | None = None


# ============ Document Chunks Schemas ============


class DocumentChunk(BaseModel):
    """Chunk документа"""

    chunk_index: int
    text: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    char_start: int | None = None
    char_end: int | None = None
    page_number: int | None = None


class DocumentChunkCreate(BaseModel):
    """Создание chunk документа"""

    file_id: str
    chunks: list[DocumentChunk]


class DocumentChunkInfo(BaseModel):
    """Информация о chunk из БД"""

    id: str
    file_id: str
    chunk_index: int
    text: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


class DocumentChunksResponse(BaseModel):
    """Ответ со списком chunks"""

    chunks: list[DocumentChunkInfo]
    total_count: int


class SimilaritySearchRequest(BaseModel):
    """Запрос поиска похожих chunks"""

    embedding: list[float]
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class SimilaritySearchResponse(BaseModel):
    """Результат поиска похожих chunks"""

    chunks: list[DocumentChunkInfo]
    similarities: list[float]


# ============ System Schemas ============


class HealthCheckResponse(BaseModel):
    """Ответ health check"""

    status: str
    timestamp: datetime
    version: str | None = None
    uptime_seconds: int | None = None


class VersionInfo(BaseModel):
    """Информация о версии API"""

    version: str
    build_date: str | None = None
    git_commit: str | None = None


# ============ Management Schemas ============


class ProjectInfo(BaseModel):
    """Информация о проекте"""

    id: str
    name: str
    slug: str | None = None
    type: str = Field(alias="type")  # Core API возвращает "type", но мы будем маппить в project_type
    developer_id: str = Field(alias="developerId")  # Core API использует camelCase
    completion_date: str | None = Field(alias="completionDate", default=None)
    
    model_config = {"populate_by_name": True}
    
    @property
    def project_type(self) -> str:
        """Alias для совместимости с существующим кодом."""
        return self.type


class DeveloperInfo(BaseModel):
    """Информация о разработчике"""

    id: str
    name: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProcessingStats(BaseModel):
    """Статистика обработки файла"""

    chunks_count: int
    processing_time_seconds: float
    file_size_bytes: int | None = None
    extracted_text_length: int | None = None


class ProcessingCompleteNotification(BaseModel):
    """Уведомление о завершении обработки"""

    file_id: str
    processing_stats: ProcessingStats


# ============ Error Schemas ============


class ErrorResponse(BaseModel):
    """Стандартный ответ об ошибке"""

    error: str
    detail: str | None = None
    status_code: int


class ValidationErrorResponse(BaseModel):
    """Ответ с ошибками валидации"""

    error: str = "Validation error"
    validation_errors: list[dict[str, Any]]


# ============ Apartments Schemas ============


class ApartmentType(StrEnum):
    """Типы квартир"""
    STUDIO = "studio"
    ONE_BR = "1br"
    TWO_BR = "2br"
    THREE_BR = "3br"
    FOUR_BR = "4br"
    PENTHOUSE = "penthouse"
    DUPLEX = "duplex"
    LOFT = "loft"


class ApartmentView(StrEnum):
    """Виды из квартиры"""
    SEA_VIEW = "sea_view"
    PARTIAL_SEA_VIEW = "partial_sea_view"
    MOUNTAIN_VIEW = "mountain_view"
    POOL_VIEW = "pool_view"
    GARDEN_VIEW = "garden_view"
    CITY_VIEW = "city_view"
    COURTYARD_VIEW = "courtyard_view"
    NO_VIEW = "no_view"


class UnitStatus(StrEnum):
    """Статусы квартир"""
    AVAILABLE = "available"
    SOLD = "sold"
    RESERVED = "reserved"


class ApartmentInfo(BaseModel):
    """Информация о квартире из Core API"""

    id: str
    identifier: str
    type: ApartmentType
    area: str  # API возвращает как строку "84.00"
    area_living: str | None = Field(default=None, alias="areaLiving")
    area_balcony: str | None = Field(default=None, alias="areaBalcony")
    balcony_count: int | None = Field(default=None, alias="balconyCount")
    floor: int | None = None
    view: ApartmentView
    price_presale: str | None = Field(default=None, alias="pricePresale")
    price: str | None = None  # API возвращает как строку "17820000.00"
    price_diff_freehold: str | None = Field(default=None, alias="priceDiffFreehold")
    price_per_sqm: str | None = Field(default=None, alias="pricePerSqm")
    currency: str = "THB"
    status: UnitStatus
    building_id: str = Field(alias="buildingId")
    project_id: str = Field(alias="projectId")

    model_config = {"populate_by_name": True}


class ApartmentSearchParams(BaseModel):
    """Параметры поиска квартир согласно Core API"""

    ids: list[str] | None = None
    search_string: str | None = Field(default=None, alias="searchString")
    search_ignore_case: bool = Field(default=False, alias="searchIgnoreCase")
    order_by: str = Field(default="identifier", alias="orderBy")
    sort_order: str | None = Field(default="desc", alias="sortOrder")  # asc, desc
    project_id: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    model_config = {"populate_by_name": True}


class ApartmentsListResponse(BaseModel):
    """Ответ со списком квартир"""

    items: list[ApartmentInfo]
    total: int
    limit: int
    offset: int


class PriceRangeInfo(BaseModel):
    """Информация о диапазоне цен"""

    min_price: float | None = None
    max_price: float | None = None
    avg_price: float | None = None
    currency: str = "THB"
    total_units: int
    units_with_pricing: int
    min_area: float | None = None
    max_area: float | None = None
    avg_area: float | None = None
    min_price_per_sqm: float | None = None
    max_price_per_sqm: float | None = None
    avg_price_per_sqm: float | None = None


# ============ Generic Schemas ============


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    limit: int | None = Field(default=50, ge=1, le=1000)
    offset: int | None = Field(default=0, ge=0)


class FilterParams(BaseModel):
    """Общие параметры фильтрации"""

    status: FileStatus | None = None
    file_type: FileType | None = None
    project_id: str | None = None
    developer_id: str | None = None
