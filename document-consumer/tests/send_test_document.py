"""
Скрипт для тестирования обработки документов.

Отправляет тестовый PDF документ в RabbitMQ и проверяет результат обработки.

Использование:
    python tests/send_test_document.py
"""
import base64
import asyncio
from pathlib import Path

from faststream.rabbit import RabbitBroker

from app.models.events import DocumentIngestEvent
from app.config.settings import settings


async def send_test_document():
    """
    Отправляет тестовый PDF документ в RabbitMQ.

    Шаги:
    1. Читает PDF файл из test_data/
    2. Кодирует в base64
    3. Создаёт событие DocumentIngestEvent
    4. Отправляет в RabbitMQ топик documents.ingest
    """
    # Путь к тестовому PDF файлу
    pdf_path = Path("test_data/Thailand_Real_Estate_Legal_Guide_Comprehensive.pdf")

    # Проверяем что файл существует
    if not pdf_path.exists():
        print(f"❌ Файл не найден: {pdf_path}")
        print("📝 Положите тестовый PDF файл в папку test_data/")
        return

    # Читаем PDF и кодируем в base64
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    print(f"📄 Файл прочитан: {pdf_path}")
    print(f"📏 Размер: {len(pdf_bytes)} байт")
    print(f"🔐 Base64 длина: {len(pdf_base64)} символов")

    # Создаём событие для отправки
    event = DocumentIngestEvent(
        document_id="test-doc-001",
        file_name=pdf_path.name,
        file_content_base64=pdf_base64,
    )

    print(f"\n📤 Отправка документа в RabbitMQ...")
    print(f"   Топик: {settings.topic_documents_ingest}")
    print(f"   RabbitMQ: {settings.rabbitmq_url}")

    # Подключаемся к RabbitMQ и отправляем сообщение
    async with RabbitBroker(url=settings.rabbitmq_url) as broker:
        await broker.publish(
            event.model_dump(),  # Преобразуем Pydantic модель в dict
            queue=settings.topic_documents_ingest,
        )

    print(f"\n✅ Документ успешно отправлен!")
    print(f"\n💡 Проверьте логи FastStream приложения:")
    print(f"   - Должны увидеть логи обработки документа")
    print(f"   - Статус: success/failed/duplicate")
    print(f"\n💡 Проверьте Qdrant:")
    print(
        f"   curl http://localhost:6333/collections/{settings.qdrant_collection_name}"
    )


if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(send_test_document())
