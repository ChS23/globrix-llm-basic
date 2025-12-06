"""
Tool для загрузки документов в систему через document consumer.

Этот инструмент позволяет агенту загружать PDF документы
в векторную базу знаний для последующего использования в RAG.
"""
import base64
import uuid
from typing import Optional, Dict
from pydantic import BaseModel, Field
import aio_pika
import json
import structlog

logger = structlog.get_logger()


class DocumentIngestionInput(BaseModel):
    """Входные параметры для загрузки документа."""

    file_path: str = Field(
        description="Путь к PDF файлу для загрузки"
    )

    file_name: Optional[str] = Field(
        default=None,
        description="Имя файла (если не указано - берется из пути)"
    )

    metadata: Optional[Dict] = Field(
        default_factory=dict,
        description="Дополнительные метаданные (регион, категория и т.д.)"
    )


class DocumentIngestionClient:
    """
    Клиент для отправки документов в RabbitMQ.

    Публикует события DocumentIngestEvent в топик documents.ingest,
    которые затем обрабатываются document-consumer сервисом.
    """

    def __init__(
        self,
        rabbitmq_url: str = "amqp://guest:guest@localhost:5672/",
        exchange_name: str = "documents",
        routing_key: str = "documents.ingest"
    ):
        """
        Инициализация клиента RabbitMQ.

        Args:
            rabbitmq_url: URL для подключения к RabbitMQ
            exchange_name: Имя exchange для публикации сообщений
            routing_key: Routing key для топика загрузки документов
        """
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self._connection = None
        self._channel = None

    async def connect(self):
        """Устанавливает соединение с RabbitMQ."""
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self._channel = await self._connection.channel()
            logger.info("rabbitmq_connected", url=self.rabbitmq_url)

    async def close(self):
        """Закрывает соединение с RabbitMQ."""
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()
        logger.info("rabbitmq_disconnected")

    async def send_document(
        self,
        file_path: str,
        file_name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Отправляет документ на обработку.

        Args:
            file_path: Путь к PDF файлу
            file_name: Имя файла (если None - берется из пути)
            metadata: Дополнительные метаданные

        Returns:
            document_id: ID созданного документа

        Raises:
            FileNotFoundError: Если файл не найден
            Exception: При ошибках чтения или отправки
        """
        await self.connect()

        # Читаем файл
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
        except FileNotFoundError:
            logger.error("file_not_found", path=file_path)
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        # Кодируем в base64
        file_content_base64 = base64.b64encode(file_content).decode('utf-8')

        # Генерируем ID и имя файла
        document_id = str(uuid.uuid4())
        if file_name is None:
            file_name = file_path.split('/')[-1]

        # Формируем событие
        event = {
            "document_id": document_id,
            "file_name": file_name,
            "file_content_base64": file_content_base64,
            "metadata": metadata or {}
        }

        # Отправляем в RabbitMQ
        try:
            exchange = await self._channel.get_exchange(self.exchange_name)

            message = aio_pika.Message(
                body=json.dumps(event).encode('utf-8'),
                content_type='application/json',
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await exchange.publish(
                message,
                routing_key=self.routing_key
            )

            logger.info(
                "document_sent",
                document_id=document_id,
                file_name=file_name,
                size_bytes=len(file_content)
            )

            return document_id

        except Exception as e:
            logger.error(
                "document_send_failed",
                error=str(e),
                exc_info=True
            )
            raise


# Глобальный клиент (можно переиспользовать)
_client = None


async def document_ingestion_tool(
    file_path: str,
    file_name: Optional[str] = None,
    metadata: Optional[Dict] = None,
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
) -> str:
    """
    Загружает PDF документ в систему для обработки.

    Этот инструмент отправляет документ в очередь RabbitMQ,
    где document-consumer сервис:
    1. Извлечет текст из PDF
    2. Разобьет на chunks
    3. Создаст embeddings
    4. Сохранит в векторную БД Qdrant

    После успешной загрузки документ будет доступен для поиска через RAG.

    Args:
        file_path: Путь к PDF файлу для загрузки
        file_name: Имя файла (опционально, по умолчанию из пути)
        metadata: Дополнительные метаданные для документа (регион, категория и т.д.)
        rabbitmq_url: URL RabbitMQ (опционально, по умолчанию localhost)

    Returns:
        Сообщение об успешной загрузке с ID документа

    Examples:
        >>> await document_ingestion_tool("/path/to/contract.pdf")
        "Документ успешно отправлен на обработку. ID: abc-123-def"

        >>> await document_ingestion_tool(
        ...     "/path/to/rules.pdf",
        ...     metadata={"region": "Ростов", "category": "Правила"}
        ... )
        "Документ успешно отправлен на обработку. ID: xyz-456-uvw"
    """
    global _client

    try:
        # Создаем клиента если еще не создан
        if _client is None:
            _client = DocumentIngestionClient(rabbitmq_url=rabbitmq_url)

        # Отправляем документ
        document_id = await _client.send_document(
            file_path=file_path,
            file_name=file_name,
            metadata=metadata
        )

        return (
            f"✅ Документ успешно отправлен на обработку.\n"
            f"ID документа: {document_id}\n"
            f"Файл: {file_name or file_path.split('/')[-1]}\n"
            f"Документ будет обработан и добавлен в базу знаний в течение нескольких секунд."
        )

    except FileNotFoundError as e:
        return f"❌ Ошибка: {str(e)}"

    except Exception as e:
        logger.error("document_ingestion_failed", error=str(e), exc_info=True)
        return f"❌ Ошибка при загрузке документа: {str(e)}"
