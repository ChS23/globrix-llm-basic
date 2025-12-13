"""
Скрипт для загрузки всех PDF документов из папки Globrix Docs в Qdrant.

Отправляет каждый PDF файл в RabbitMQ для обработки document-consumer сервисом.

Использование:
    cd document-consumer
    uv run python tests/send_all_documents.py
"""
import base64
import asyncio
import uuid
from pathlib import Path

from faststream.rabbit import RabbitBroker

from app.models.events import DocumentIngestEvent
from app.config.settings import settings


async def send_all_documents():
    """
    Находит все PDF файлы в test_data и отправляет их в RabbitMQ.
    """
    # Папка с документами
    docs_path = Path("test_data")

    if not docs_path.exists():
        print(f"❌ Папка не найдена: {docs_path}")
        return

    # Находим все PDF файлы рекурсивно
    pdf_files = list(docs_path.rglob("*.pdf"))

    if not pdf_files:
        print(f"❌ PDF файлы не найдены в {docs_path}")
        return

    print(f"📁 Найдено {len(pdf_files)} PDF файлов:")
    for pdf in pdf_files:
        print(f"   - {pdf}")

    print(f"\n📤 Подключение к RabbitMQ: {settings.rabbitmq_url}")

    async with RabbitBroker(url=settings.rabbitmq_url) as broker:
        for pdf_path in pdf_files:
            # Определяем регион из пути к файлу
            parts = pdf_path.parts
            region = "Unknown"
            for part in parts:
                if part in ["Indonesia", "Malaysia", "Thailand"]:
                    region = part
                    break

            # Читаем и кодируем файл
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

            # Создаём уникальный ID для документа
            doc_id = f"{region.lower()}-{uuid.uuid4().hex[:8]}"

            # Создаём событие
            event = DocumentIngestEvent(
                document_id=doc_id,
                file_name=pdf_path.name,
                file_content_base64=pdf_base64,
                metadata={
                    "region": region,
                    "source": "globrix_docs",
                    "category": "legal_guide",
                }
            )

            # Отправляем в RabbitMQ
            await broker.publish(
                event.model_dump(),
                queue=settings.topic_documents_ingest,
            )

            print(f"✅ Отправлен: {pdf_path.name}")
            print(f"   ID: {doc_id}")
            print(f"   Регион: {region}")
            print(f"   Размер: {len(pdf_bytes)} байт")
            print()

    print(f"\n🎉 Все {len(pdf_files)} документов отправлены в очередь!")
    print(f"\n💡 Проверьте:")
    print(f"   - Логи document-consumer для статуса обработки")
    print(f"   - Qdrant: curl http://localhost:6333/collections/{settings.qdrant_collection_name}")


if __name__ == "__main__":
    asyncio.run(send_all_documents())
