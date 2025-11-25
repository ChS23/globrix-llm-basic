"""
Главный файл приложения FastStream.

Что он делает:
- Создает подключение к RabbitMQ
- Запускает FastStream приложение
- Подключает обработчики сообщений (роутеры)
"""
import structlog
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from app.config.settings import settings
from app.consumers.document_consumer import router as document_router

# Настраиваем логирование
# structlog - это библиотека для красивых и структурированных логов
logger = structlog.get_logger()

# Создаем брокер для подключения к RabbitMQ
# URL формата: amqp://user:password@host:port/
broker = RabbitBroker(url=settings.rabbitmq_url)

# Создаем FastStream приложение
# Это главный объект, который управляет всем приложением
app = FastStream(broker)

# Подключаем роутер с обработчиками документов
# Роутер содержит функции, которые обрабатывают сообщения из RabbitMQ
broker.include_router(document_router)


@app.on_startup
async def on_startup():
    """
    Выполняется при запуске приложения.

    Здесь можно:
    - Проверить подключение к базам данных
    - Инициализировать глобальные объекты
    - Вывести информацию о конфигурации
    """
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        rabbitmq_url=settings.rabbitmq_url,
    )


@app.on_shutdown
async def on_shutdown():
    """
    Выполняется при остановке приложения.

    Здесь можно:
    - Закрыть подключения к БД
    - Сохранить состояние
    - Завершить фоновые задачи
    """
    logger.info("application_shutting_down")
