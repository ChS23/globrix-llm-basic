"""
Модели данных для сообщений RabbitMQ.

Эти модели описывают структуру сообщений, которые приходят и уходят через RabbitMQ.
Pydantic автоматически валидирует типы данных.
"""
from pydantic import BaseModel, Field
from typing import Optional


class DocumentIngestEvent(BaseModel):
    """
    Событие о новом документе для обработки.

    Приходит из RabbitMQ в топик documents.ingest
    Содержит PDF документ в формате base64.
    """
    document_id: str = Field(
        description="Уникальный ID документа"
    )

    file_name: str = Field(
        description="Название файла (например, 'contract.pdf')"
    )

    file_content_base64: str = Field(
        description="Содержимое PDF файла в формате base64"
    )

    metadata: Optional[dict] = Field(
        default_factory=dict,
        description="Дополнительные метаданные (страна, категория и т.д.)"
    )


class DocumentProcessedEvent(BaseModel):
    """
    Событие о результате обработки документа.

    Отправляется обратно в RabbitMQ после обработки документа.
    Содержит информацию об успехе или ошибке.
    """
    document_id: str = Field(
        description="ID обработанного документа"
    )

    status: str = Field(
        description="Статус: 'success', 'failed' или 'duplicate'"
    )

    chunks_count: Optional[int] = Field(
        default=None,
        description="Сколько кусочков получилось из документа"
    )

    document_hash: Optional[str] = Field(
        default=None,
        description="SHA256 хеш документа для проверки дубликатов"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Сообщение об ошибке, если status='failed'"
    )
