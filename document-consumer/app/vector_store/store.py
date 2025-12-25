"""
Класс для работы с векторным хранилищем Qdrant.

Что он делает:
- Подключается к Qdrant
- Сохраняет документы с эмбеддингами
- Ищет похожие документы по запросу
"""
from typing import List

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import structlog

from app.config.settings import settings
from app.utils.http_client import get_http_client

logger = structlog.get_logger()


class DocumentVectorStore:
    """
    Класс для работы с векторным хранилищем.

    Использует паттерн Singleton - создается только один экземпляр.
    Зачем? Чтобы не создавать много подключений к БД.
    """

    _instance = None  # Здесь будет храниться единственный экземпляр

    def __new__(cls):
        """
        Метод создания объекта.

        Если объект уже создан - возвращаем его.
        Если нет - создаем новый.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Инициализация векторного хранилища.

        Выполняется только один раз, при первом создании объекта.
        """
        # Если уже инициализировали - ничего не делаем
        if self._initialized:
            return

        logger.info("initializing_vector_store")

        # 1. Создаем клиент для подключения к Qdrant
        self.client = QdrantClient(url=settings.qdrant_url)

        # 2. Создаем объект для генерации эмбеддингов
        # Используем отдельный ключ для эмбеддингов если задан
        # Явно указываем base_url для OpenAI, чтобы не подхватывать OPENAI_BASE_URL из env
        embedding_key = settings.embedding_api_key or settings.openai_api_key

        # HTTP клиент с прокси (если настроен)
        http_client = get_http_client()

        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=embedding_key,
            openai_api_base="https://api.openai.com/v1",  # Явно OpenAI для эмбеддингов
            http_client=http_client,
            check_embedding_ctx_length=False,  # Отключаем tiktoken (требует скачивания через прокси)
        )

        # 3. Создаем коллекцию в Qdrant (если еще не создана)
        self._ensure_collection_exists()

        # 4. Создаем векторное хранилище LangChain
        # Оно будет автоматически создавать эмбеддинги и сохранять в Qdrant
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=settings.qdrant_collection_name,
            embedding=self.embeddings
        )

        self._initialized = True
        logger.info("vector_store_initialized")

    def _ensure_collection_exists(self):
        """
        Создает коллекцию в Qdrant, если она еще не существует.

        Коллекция - это как таблица в обычной БД.
        Здесь мы храним все векторы документов.
        """
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if settings.qdrant_collection_name not in collection_names:
            logger.info(
                "creating_collection",
                name=settings.qdrant_collection_name
            )

            self.client.create_collection(
                collection_name=settings.qdrant_collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimensions,  # Размер вектора из настроек
                    distance=Distance.COSINE  # Метрика для сравнения векторов (косинусное расстояние)
                )
            )

            logger.info("collection_created")

    async def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Добавляет документы в векторное хранилище.

        Что происходит:
        1. Для каждого документа создается эмбеддинг (вектор)
        2. Вектор сохраняется в Qdrant вместе с текстом и метаданными

        Аргументы:
            documents: Список документов LangChain

        Возвращает:
            Список ID сохраненных документов
        """
        logger.info("adding_documents", count=len(documents))

        # LangChain автоматически:
        # 1. Создаст эмбеддинги для каждого документа через OpenAI
        # 2. Сохранит их в Qdrant
        ids = await self.vector_store.aadd_documents(documents)

        logger.info("documents_added", count=len(ids))
        return ids

    async def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Ищет похожие документы по запросу.

        Что происходит:
        1. Запрос превращается в эмбеддинг (вектор)
        2. Ищутся k самых близких векторов в Qdrant
        3. Возвращаются соответствующие документы

        Аргументы:
            query: Текст запроса
            k: Сколько документов вернуть

        Возвращает:
            Список найденных документов
        """
        logger.info("searching_documents", query=query, k=k)

        # Ищем похожие документы
        docs = await self.vector_store.asimilarity_search(query, k=k)

        logger.info("documents_found", count=len(docs))
        return docs


# Глобальная функция для получения векторного хранилища
def get_vector_store() -> DocumentVectorStore:
    """
    Возвращает глобальный экземпляр векторного хранилища.

    Используйте эту функцию везде, где нужен доступ к Qdrant.
    """
    return DocumentVectorStore()