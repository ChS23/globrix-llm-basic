"""
Сервис для загрузки документов в векторную базу.

Этот класс содержит всю бизнес-логику обработки PDF документов:
1. Декодирование base64
2. Извлечение текста из PDF
3. Проверка дубликатов по хешу
4. Разбиение на chunks
5. Сохранение в Qdrant
"""
import base64
import hashlib
from typing import Optional

import structlog
from langchain_core.document_loaders import Blob
from langchain_pymupdf4llm import PyMuPDF4LLMParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config.settings import settings
from app.models.events import DocumentIngestEvent, DocumentProcessedEvent
from app.vector_store.store import get_vector_store

logger = structlog.get_logger()


class DocumentIngestionService:
    """
    Сервис для обработки и загрузки документов в векторную БД.
    """

    def __init__(self):
        """Инициализация сервиса."""
        self.vector_store = get_vector_store()

    async def ingest_document(
        self, event: DocumentIngestEvent
    ) -> DocumentProcessedEvent:
        """
        Обрабатывает документ и сохраняет в векторную БД.

        Шаги обработки:
        1. Декодируем base64 → PDF байты
        2. Вычисляем SHA256 хеш для проверки дубликатов
        3. Проверяем, не загружали ли этот документ ранее
        4. Извлекаем текст из PDF
        5. Разбиваем на chunks
        6. Сохраняем в Qdrant с метаданными

        Аргументы:
            event: Событие с данными документа из RabbitMQ

        Возвращает:
            Результат обработки (успех, ошибка или дубликат)
        """
        logger.info(
            "processing_document_started",
            document_id=event.document_id,
            file_name=event.file_name,
        )

        try:
            # Шаг 1: Декодируем base64 в байты PDF
            pdf_bytes = base64.b64decode(event.file_content_base64)
            logger.info("pdf_decoded", size_bytes=len(pdf_bytes))

            # Шаг 2: Вычисляем хеш документа для проверки дубликатов
            document_hash = hashlib.sha256(pdf_bytes).hexdigest()
            logger.info("document_hash_calculated", hash=document_hash)

            # Шаг 3: Проверяем, не загружали ли уже этот документ
            is_duplicate = await self._check_duplicate(document_hash)
            if is_duplicate:
                logger.warning(
                    "duplicate_document_detected",
                    document_id=event.document_id,
                    hash=document_hash,
                )
                return DocumentProcessedEvent(
                    document_id=event.document_id,
                    status="duplicate",
                    document_hash=document_hash,
                    error_message=f"Документ с хешем {document_hash} уже существует",
                )

            # Шаг 4: Извлекаем текст из PDF
            documents = await self._extract_text_from_pdf(pdf_bytes)
            logger.info("pdf_loaded", pages_count=len(documents))

            # Шаг 5: Разбиваем на chunks
            chunks = self._split_into_chunks(documents)
            logger.info("document_split", chunks_count=len(chunks))

            # Шаг 6: Добавляем метаданные к каждому chunk
            self._add_metadata_to_chunks(
                chunks=chunks,
                document_id=event.document_id,
                file_name=event.file_name,
                document_hash=document_hash,
                additional_metadata=event.metadata,
            )

            # Шаг 7: Сохраняем в векторную БД
            await self.vector_store.add_documents(chunks)

            logger.info(
                "document_processed_successfully",
                document_id=event.document_id,
                chunks_count=len(chunks),
                document_hash=document_hash,
            )

            return DocumentProcessedEvent(
                document_id=event.document_id,
                status="success",
                chunks_count=len(chunks),
                document_hash=document_hash,
            )

        except Exception as e:
            logger.error(
                "document_processing_failed",
                document_id=event.document_id,
                error=str(e),
                exc_info=True,
            )

            return DocumentProcessedEvent(
                document_id=event.document_id,
                status="failed",
                error_message=str(e),
            )

    async def _check_duplicate(self, document_hash: str) -> bool:
        """
        Проверяет наличие документа с таким хешем в БД.

        Аргументы:
            document_hash: SHA256 хеш документа

        Возвращает:
            True если документ уже существует, False если нет
        """
        try:
            # Ищем документы с таким хешем в Qdrant
            # Используем фильтр по метаданным
            results = self.vector_store.client.scroll(
                collection_name=settings.qdrant_collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.document_hash",
                            match=MatchValue(value=document_hash),
                        )
                    ]
                ),
                limit=1,  # Нам достаточно найти хотя бы один
            )

            # Если нашли хотя бы один chunk с таким хешем - это дубликат
            return len(results[0]) > 0

        except Exception as e:
            logger.warning(
                "duplicate_check_failed", error=str(e), exc_info=True
            )
            # В случае ошибки проверки - считаем что это не дубликат
            # Лучше обработать документ дважды, чем потерять данные
            return False

    async def _extract_text_from_pdf(self, pdf_bytes: bytes):
        """
        Извлекает текст из PDF файла.

        Использует PyMuPDF4LLMParser для работы напрямую с байтами:
        1. Создаём Blob из байтов PDF
        2. Парсим через PyMuPDF4LLMParser (оптимизирован для LLM)
        3. Возвращаем документы в Markdown формате

        Аргументы:
            pdf_bytes: Содержимое PDF в байтах

        Возвращает:
            Список LangChain Document объектов
        """
        # Создаём Blob из байтов
        blob = Blob.from_data(pdf_bytes, mime_type="application/pdf")

        # Парсим PDF с помощью PyMuPDF4LLM (оптимизирован для LLM)
        parser = PyMuPDF4LLMParser()
        documents = list(parser.parse(blob))

        return documents

    def _split_into_chunks(self, documents):
        """
        Разбивает документы на кусочки (chunks).

        Используем RecursiveCharacterTextSplitter:
        - Пытается разделять по параграфам, а не посередине предложения
        - Сохраняет перекрытие между chunks для контекста

        Аргументы:
            documents: Список LangChain Document объектов

        Возвращает:
            Список chunks (тоже Document объекты)
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,  # Размер chunk
            chunk_overlap=settings.chunk_overlap,  # Перекрытие
            length_function=len,  # Как измеряем длину
        )

        chunks = text_splitter.split_documents(documents)
        return chunks

    def _add_metadata_to_chunks(
        self,
        chunks,
        document_id: str,
        file_name: str,
        document_hash: str,
        additional_metadata: dict,
    ):
        """
        Добавляет метаданные к каждому chunk.

        Метаданные используются для:
        - Идентификации документа
        - Проверки дубликатов
        - Фильтрации при поиске

        Аргументы:
            chunks: Список chunks для обновления
            document_id: ID документа
            file_name: Имя файла
            document_hash: SHA256 хеш
            additional_metadata: Дополнительные метаданные из события
        """
        for i, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "document_id": document_id,
                    "file_name": file_name,
                    "document_hash": document_hash,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **additional_metadata,  # Добавляем всё из события
                }
            )
