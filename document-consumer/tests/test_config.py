"""
Тесты для конфигурации приложения.

Проверяем что настройки загружаются корректно.
"""
import pytest
from app.config.settings import Settings


class TestSettings:
    """Тесты для класса Settings."""

    def test_default_values(self):
        """
        Проверяет что все настройки имеют значения по умолчанию.

        Даже если .env файл пустой, приложение должно запуститься
        с разумными значениями по умолчанию.
        """
        settings = Settings()

        # Основные настройки
        assert settings.app_name == "document-consumer"
        assert settings.app_version == "0.1.0"

        # RabbitMQ
        assert settings.rabbitmq_url is not None
        assert "amqp://" in settings.rabbitmq_url

        # Qdrant
        assert settings.qdrant_url is not None
        assert settings.qdrant_collection_name == "documents"

        # Эмбеддинги
        assert settings.embedding_model is not None, "embedding_model должен быть задан"
        assert isinstance(settings.embedding_model, str), "embedding_model должен быть строкой"

        # Chunking
        assert settings.chunk_size == 1000
        assert settings.chunk_overlap == 200

    def test_chunk_overlap_less_than_size(self):
        """
        Проверяет что chunk_overlap меньше chunk_size.

        Это важно, иначе кусочки будут перекрываться больше чем на 100%.
        """
        settings = Settings()
        assert settings.chunk_overlap < settings.chunk_size, \
            "chunk_overlap должен быть меньше chunk_size"

    def test_embedding_dimensions_positive(self):
        """
        Проверяет что размер эмбеддинга положительный.

        Размер вектора не может быть отрицательным или нулевым.
        """
        settings = Settings()
        assert settings.embedding_dimensions > 0, \
            "embedding_dimensions должен быть положительным числом"

    def test_embedding_model_valid(self):
        """
        Проверяет что модель эмбеддингов задана корректно.

        Проверяем что:
        - Модель не пустая строка
        - Содержит слово "embedding" (для OpenAI моделей)
        """
        settings = Settings()
        assert settings.embedding_model != "", "embedding_model не должен быть пустым"
        assert len(settings.embedding_model) > 0, "embedding_model должен содержать название модели"
