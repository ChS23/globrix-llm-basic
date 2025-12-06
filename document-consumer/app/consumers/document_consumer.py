"""
Обработчик документов из RabbitMQ.
"""
import structlog
from faststream.rabbit import RabbitRouter

from app.config.settings import settings
from app.models.events import DocumentIngestEvent, DocumentProcessedEvent
from app.services.document_ingestion import DocumentIngestionService

logger = structlog.get_logger()

# Создаем роутер для обработки сообщений
router = RabbitRouter()


@router.subscriber(settings.topic_documents_ingest)
async def process_document(
    event: DocumentIngestEvent,
) -> DocumentProcessedEvent:
    """
    Обрабатывает документ из RabbitMQ.

    Это тонкий обработчик - он только:
    1. Получает сообщение из RabbitMQ
    2. Передаёт его в сервис
    3. Возвращает результат

    Вся бизнес-логика находится в DocumentIngestionService.

    Аргументы:
        event: Событие с документом из RabbitMQ

    Возвращает:
        Результат обработки документа
    """
    logger.info(
        "received_document_event",
        document_id=event.document_id,
        file_name=event.file_name,
    )

    # Создаём сервис и обрабатываем документ
    service = DocumentIngestionService()
    result = await service.ingest_document(event)

    logger.info(
        "document_event_processed",
        document_id=event.document_id,
        status=result.status,
    )

    return result
