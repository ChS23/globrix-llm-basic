"""
Обработчик документов из RabbitMQ.

Пока это пустой роутер, чтобы приложение могло запуститься.
Полную реализацию добавим на Этапе 2.
"""
import structlog
from faststream.rabbit import RabbitRouter

from app.config.settings import settings

logger = structlog.get_logger()

# Создаем роутер для обработки сообщений
# Роутер - это набор обработчиков для разных топиков RabbitMQ
router = RabbitRouter()


# TODO: На Этапе 2 здесь добавим обработчик для документов
# @router.subscriber(settings.topic_documents_ingest)
# async def process_document(event: DocumentIngestEvent):
#     pass
