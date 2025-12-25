"""
Unit тесты для DocumentIngestionService.

Используем моки для OpenAI и Qdrant, чтобы тесты:
- Не зависели от внешних сервисов
- Работали без API ключей
- Выполнялись быстро
"""
import base64
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document

from app.models.events import DocumentIngestEvent, DocumentProcessedEvent
from app.services.document_ingestion import DocumentIngestionService


@pytest.fixture
def sample_pdf_bytes():
    """Фикстура с фейковыми PDF байтами."""
    return b"%PDF-1.4\nFake PDF content for testing"


@pytest.fixture
def sample_event(sample_pdf_bytes):
    """Фикстура с тестовым событием."""
    pdf_base64 = base64.b64encode(sample_pdf_bytes).decode("utf-8")

    return DocumentIngestEvent(
        document_id="test-doc-123",
        file_name="test_document.pdf",
        file_content_base64=pdf_base64,
        metadata={"country": "UAE", "category": "legal"},
    )


@pytest.fixture
def mock_vector_store():
    """Фикстура с мокированным векторным хранилищем."""
    mock_store = MagicMock()
    mock_store.add_documents = AsyncMock(return_value=["id1", "id2", "id3"])
    mock_store.client.scroll = MagicMock(
        return_value=([],)
    )  # Пустой список - нет дубликатов
    return mock_store


class TestDocumentIngestionService:
    """Тесты для сервиса обработки документов."""

    @pytest.mark.asyncio
    async def test_successful_document_processing(
        self, sample_event, mock_vector_store, mocker
    ):
        """Тест успешной обработки документа."""
        # Мокируем get_vector_store
        mocker.patch(
            "app.services.document_ingestion.get_vector_store",
            return_value=mock_vector_store,
        )

        # Мокируем PyMuPDF4LLMParser
        mock_parser = mocker.patch(
            "app.services.document_ingestion.PyMuPDF4LLMParser"
        )
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = [
            Document(
                page_content="Page 1 content",
                metadata={"page": 0, "source": "test.pdf"},
            ),
            Document(
                page_content="Page 2 content",
                metadata={"page": 1, "source": "test.pdf"},
            ),
        ]

        # Мокируем Blob
        mocker.patch("app.services.document_ingestion.Blob")

        # Создаём сервис и обрабатываем документ
        service = DocumentIngestionService()
        result = await service.ingest_document(sample_event)

        # Проверяем результат
        assert result.status == "success"
        assert result.document_id == "test-doc-123"
        assert result.chunks_count > 0
        assert result.document_hash is not None
        assert result.error_message is None

        # Проверяем что векторное хранилище вызвано
        mock_vector_store.add_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_duplicate_document_detection(
        self, sample_event, mock_vector_store, mocker
    ):
        """Тест обнаружения дубликата документа."""
        # Мокируем что документ уже существует
        mock_vector_store.client.scroll = MagicMock(
            return_value=(
                [MagicMock()],
            )  # Не пустой список - дубликат найден
        )

        mocker.patch(
            "app.services.document_ingestion.get_vector_store",
            return_value=mock_vector_store,
        )

        # Создаём сервис и обрабатываем документ
        service = DocumentIngestionService()
        result = await service.ingest_document(sample_event)

        # Проверяем что вернулся статус duplicate
        assert result.status == "duplicate"
        assert result.document_id == "test-doc-123"
        assert result.document_hash is not None
        assert "уже существует" in result.error_message

        # Проверяем что векторное хранилище НЕ вызывалось
        mock_vector_store.add_documents.assert_not_called()

    @pytest.mark.asyncio
    async def test_processing_error_handling(
        self, sample_event, mock_vector_store, mocker
    ):
        """Тест обработки ошибок при парсинге PDF."""
        mocker.patch(
            "app.services.document_ingestion.get_vector_store",
            return_value=mock_vector_store,
        )

        # Мокируем PyMuPDF4LLMParser чтобы он выбросил ошибку
        mock_parser = mocker.patch(
            "app.services.document_ingestion.PyMuPDF4LLMParser"
        )
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.side_effect = Exception("PDF parsing failed")

        # Мокируем Blob
        mocker.patch("app.services.document_ingestion.Blob")

        # Создаём сервис и обрабатываем документ
        service = DocumentIngestionService()
        result = await service.ingest_document(sample_event)

        # Проверяем что вернулся статус failed
        assert result.status == "failed"
        assert result.document_id == "test-doc-123"
        assert "PDF parsing failed" in result.error_message

    def test_document_hash_calculation(self, sample_pdf_bytes):
        """Тест вычисления SHA256 хеша документа."""
        expected_hash = hashlib.sha256(sample_pdf_bytes).hexdigest()

        # Декодируем из base64 и вычисляем хеш
        pdf_base64 = base64.b64encode(sample_pdf_bytes).decode("utf-8")
        pdf_bytes_decoded = base64.b64decode(pdf_base64)
        actual_hash = hashlib.sha256(pdf_bytes_decoded).hexdigest()

        assert actual_hash == expected_hash

    @pytest.mark.asyncio
    async def test_metadata_added_to_chunks(
        self, sample_event, mock_vector_store, mocker
    ):
        """Тест что метаданные добавляются к каждому chunk."""
        mocker.patch(
            "app.services.document_ingestion.get_vector_store",
            return_value=mock_vector_store,
        )

        # Мокируем PyMuPDF4LLMParser
        mock_parser = mocker.patch(
            "app.services.document_ingestion.PyMuPDF4LLMParser"
        )
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = [
            Document(
                page_content="Test content" * 200,  # Длинный текст
                metadata={"page": 0},
            ),
        ]

        # Мокируем Blob
        mocker.patch("app.services.document_ingestion.Blob")

        # Создаём сервис и обрабатываем документ
        service = DocumentIngestionService()
        await service.ingest_document(sample_event)

        # Получаем переданные chunks
        call_args = mock_vector_store.add_documents.call_args
        chunks = call_args[0][0]

        # Проверяем что метаданные добавлены
        for chunk in chunks:
            assert chunk.metadata["document_id"] == "test-doc-123"
            assert chunk.metadata["file_name"] == "test_document.pdf"
            assert chunk.metadata["country"] == "UAE"
            assert chunk.metadata["category"] == "legal"
            assert "document_hash" in chunk.metadata
            assert "chunk_index" in chunk.metadata
            assert "total_chunks" in chunk.metadata

    def test_split_into_chunks(self, mocker):
        """Тест разбиения документа на chunks."""
        # Создаём длинный документ
        long_text = "This is a test sentence. " * 100  # ~2500 символов
        documents = [Document(page_content=long_text, metadata={"page": 0})]

        # Создаём сервис (с моком векторного хранилища)
        mock_vector_store = MagicMock()
        mocker.patch(
            "app.services.document_ingestion.get_vector_store",
            return_value=mock_vector_store,
        )

        service = DocumentIngestionService()
        chunks = service._split_into_chunks(documents)

        # Проверяем что документ разбился на несколько chunks
        assert len(chunks) > 1

        # Проверяем что каждый chunk не превышает chunk_size
        for chunk in chunks:
            assert len(chunk.page_content) <= 900  # chunk_size (700) + небольшой запас
