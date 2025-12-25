#!/usr/bin/env python3
"""
Скрипт для переиндексации документов в Qdrant.

Использование:
    uv run python scripts/reindex.py
"""
import asyncio
import base64
import sys
from pathlib import Path

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.events import DocumentIngestEvent
from app.services.document_ingestion import DocumentIngestionService


async def reindex_documents():
    """Переиндексирует все PDF документы из test_data."""

    test_data_dir = Path(__file__).parent.parent / "test_data"

    # Находим все PDF файлы
    pdf_files = list(test_data_dir.rglob("*.pdf"))

    if not pdf_files:
        print("❌ PDF файлы не найдены в test_data/")
        return

    print(f"📄 Найдено {len(pdf_files)} PDF файлов")

    service = DocumentIngestionService()

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Индексируем: {pdf_path.name}")

        # Читаем файл и конвертируем в base64
        pdf_bytes = pdf_path.read_bytes()
        file_content_base64 = base64.b64encode(pdf_bytes).decode()

        # Создаём событие
        event = DocumentIngestEvent(
            document_id=f"reindex_{pdf_path.stem}",
            file_name=pdf_path.name,
            file_content_base64=file_content_base64,
            metadata={
                "region": pdf_path.parent.name,
                "source": "reindex_script",
            }
        )

        # Обрабатываем
        result = await service.ingest_document(event)

        if result.status == "success":
            print(f"   ✅ {result.chunks_count} chunks")
        elif result.status == "duplicate":
            print(f"   ⏭️  Дубликат (пропускаем)")
        else:
            print(f"   ❌ Ошибка: {result.error_message}")

    print("\n✅ Готово!")


if __name__ == "__main__":
    asyncio.run(reindex_documents())
