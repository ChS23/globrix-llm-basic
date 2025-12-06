"""
Тесты для моделей данных (Pydantic models).

Проверяем валидацию и сериализацию моделей.
"""
import pytest
from pydantic import ValidationError

from app.models.events import DocumentIngestEvent, DocumentProcessedEvent


class TestDocumentIngestEvent:
    """Тесты для модели DocumentIngestEvent."""

    def test_valid_event(self):
        """Тест создания валидного события."""
        event = DocumentIngestEvent(
            document_id="test-123",
            file_name="test.pdf",
            file_content_base64="YmFzZTY0X2RhdGE=",
            metadata={"country": "UAE"},
        )

        assert event.document_id == "test-123"
        assert event.file_name == "test.pdf"
        assert event.file_content_base64 == "YmFzZTY0X2RhdGE="
        assert event.metadata == {"country": "UAE"}

    def test_event_without_metadata(self):
        """Тест создания события без метаданных (должны быть пустой dict)."""
        event = DocumentIngestEvent(
            document_id="test-123",
            file_name="test.pdf",
            file_content_base64="YmFzZTY0X2RhdGE=",
        )

        assert event.metadata == {}

    def test_missing_required_fields(self):
        """Тест валидации - должна быть ошибка если нет обязательных полей."""
        with pytest.raises(ValidationError):
            DocumentIngestEvent(
                document_id="test-123",
                # file_name отсутствует - должна быть ошибка
                file_content_base64="YmFzZTY0X2RhdGE=",
            )

    def test_model_dump(self):
        """Тест сериализации модели в dict."""
        event = DocumentIngestEvent(
            document_id="test-123",
            file_name="test.pdf",
            file_content_base64="YmFzZTY0X2RhdGE=",
            metadata={"country": "UAE"},
        )

        data = event.model_dump()

        assert data["document_id"] == "test-123"
        assert data["file_name"] == "test.pdf"
        assert data["metadata"]["country"] == "UAE"


class TestDocumentProcessedEvent:
    """Тесты для модели DocumentProcessedEvent."""

    def test_success_event(self):
        """Тест события успешной обработки."""
        event = DocumentProcessedEvent(
            document_id="test-123",
            status="success",
            chunks_count=10,
            document_hash="abc123",
        )

        assert event.document_id == "test-123"
        assert event.status == "success"
        assert event.chunks_count == 10
        assert event.document_hash == "abc123"
        assert event.error_message is None

    def test_failed_event(self):
        """Тест события с ошибкой."""
        event = DocumentProcessedEvent(
            document_id="test-123",
            status="failed",
            error_message="PDF parsing failed",
        )

        assert event.status == "failed"
        assert event.error_message == "PDF parsing failed"
        assert event.chunks_count is None

    def test_duplicate_event(self):
        """Тест события дубликата."""
        event = DocumentProcessedEvent(
            document_id="test-123",
            status="duplicate",
            document_hash="abc123",
            error_message="Document already exists",
        )

        assert event.status == "duplicate"
        assert event.document_hash == "abc123"
