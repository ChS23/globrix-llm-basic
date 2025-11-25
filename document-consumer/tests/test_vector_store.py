"""
Тесты для векторного хранилища.

Проверяем что DocumentVectorStore работает корректно.
"""
import pytest
from langchain_core.documents import Document

from app.vector_store.store import get_vector_store, DocumentVectorStore
from app.config.settings import settings


class TestVectorStore:
    """Тесты для класса DocumentVectorStore."""

    @pytest.fixture
    def vector_store(self):
        """
        Фикстура для получения векторного хранилища.

        Фикстура - это функция, которая выполняется перед каждым тестом.
        Она создает объекты, нужные для теста.
        """
        return get_vector_store()

    def test_singleton_pattern(self):
        """
        Проверяет что DocumentVectorStore - это Singleton.

        Singleton означает что создается только один экземпляр класса.
        Если мы вызовем get_vector_store() несколько раз,
        должен вернуться один и тот же объект.
        """
        store1 = get_vector_store()
        store2 = get_vector_store()

        # Проверяем что это один и тот же объект
        assert store1 is store2, "get_vector_store() должен возвращать один экземпляр"

    def test_vector_store_initialization(self, vector_store):
        """
        Проверяет что векторное хранилище правильно инициализировано.

        Проверяем:
        - Создан клиент Qdrant
        - Созданы эмбеддинги
        - Создано векторное хранилище LangChain
        """
        assert vector_store.client is not None, "Клиент Qdrant не создан"
        assert vector_store.embeddings is not None, "Эмбеддинги не созданы"
        assert vector_store.vector_store is not None, "Векторное хранилище не создано"

    def test_collection_exists(self, vector_store):
        """
        Проверяет что коллекция создана в Qdrant.

        Коллекция - это как таблица в БД.
        Она должна автоматически создаться при первом запуске.
        """
        collections = vector_store.client.get_collections().collections
        collection_names = [c.name for c in collections]

        assert settings.qdrant_collection_name in collection_names, \
            f"Коллекция '{settings.qdrant_collection_name}' не найдена в Qdrant"

    @pytest.mark.asyncio
    async def test_add_documents(self, vector_store):
        """
        Проверяет что можем добавить документы в хранилище.

        Что проверяем:
        1. Документы сохраняются
        2. Возвращаются ID документов
        3. Количество ID совпадает с количеством документов
        """
        # Создаем тестовые документы
        test_docs = [
            Document(
                page_content="This is a test document about real estate.",
                metadata={"source": "test", "category": "real_estate"}
            ),
            Document(
                page_content="Another test document about property laws.",
                metadata={"source": "test", "category": "legal"}
            ),
        ]

        # Сохраняем документы
        doc_ids = await vector_store.add_documents(test_docs)

        # Проверяем что вернулись ID
        assert doc_ids is not None, "add_documents() должен возвращать ID"
        assert len(doc_ids) == len(test_docs), \
            f"Количество ID ({len(doc_ids)}) не совпадает с количеством документов ({len(test_docs)})"

        # Проверяем что ID не пустые
        for doc_id in doc_ids:
            assert doc_id is not None and doc_id != "", "ID документа не должен быть пустым"

    @pytest.mark.asyncio
    async def test_search(self, vector_store):
        """
        Проверяет что поиск работает корректно.

        Что проверяем:
        1. Поиск возвращает результаты
        2. Количество результатов не превышает k
        3. Результаты содержат текст и метаданные
        """
        # Сначала добавляем тестовые документы
        test_docs = [
            Document(
                page_content="Dubai has strict property ownership rules for foreigners.",
                metadata={"country": "UAE", "category": "legal"}
            ),
            Document(
                page_content="Real estate investors can get residence visa in UAE.",
                metadata={"country": "UAE", "category": "visa"}
            ),
        ]
        await vector_store.add_documents(test_docs)

        # Ищем документы
        query = "property ownership rules"
        k = 2
        results = await vector_store.search(query, k=k)

        # Проверки
        assert results is not None, "search() не должен возвращать None"
        assert len(results) <= k, f"Количество результатов ({len(results)}) превышает k ({k})"

        # Проверяем что результаты содержат нужные поля
        for doc in results:
            assert hasattr(doc, 'page_content'), "Документ должен содержать page_content"
            assert hasattr(doc, 'metadata'), "Документ должен содержать metadata"
            assert doc.page_content is not None, "page_content не должен быть None"

    @pytest.mark.asyncio
    async def test_search_relevance(self, vector_store):
        """
        Проверяет что поиск возвращает релевантные результаты.

        Мы добавляем документы на разные темы,
        а потом проверяем что поиск находит правильные документы.
        """
        # Добавляем документы на разные темы с очень разными текстами
        test_docs = [
            Document(
                page_content="Dubai property ownership laws and regulations for foreigners buying real estate.",
                metadata={"topic": "ownership", "test_id": "ownership_doc"}
            ),
            Document(
                page_content="Visa requirements for UAE residents and tourist information.",
                metadata={"topic": "visa", "test_id": "visa_doc"}
            ),
            Document(
                page_content="Service charges and maintenance fees in Dubai buildings.",
                metadata={"topic": "fees", "test_id": "fees_doc"}
            ),
        ]
        await vector_store.add_documents(test_docs)

        # Ищем документ про ownership (берем топ-3 результата)
        results = await vector_store.search("property ownership laws", k=3)

        # Проверяем что нашли результаты
        assert len(results) > 0, "Поиск должен вернуть хотя бы один результат"

        # Проверяем что среди топ-3 есть документ про ownership
        topics = [doc.metadata.get("topic", "") for doc in results]
        assert "ownership" in topics, \
            f"Среди топ-3 результатов должен быть документ про ownership. Найдено: {topics}"
