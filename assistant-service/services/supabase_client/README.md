# Supabase CRUD Client

Асинхронный клиент для работы с Supabase базой данных с поддержкой Realtime.

## Структура

```
supabase_client/
├── __init__.py         # Экспорт всех классов
├── base_client.py      # Async Supabase клиент (Singleton)
├── client_crud.py      # CRUD для таблицы client
└── deal_crud.py        # CRUD для таблицы deal
```

## Установка зависимостей

```bash
cd assistant-service
uv add supabase aiohttp structlog
```

## Использование

### Базовая инициализация (с Context Manager)

```python
import asyncio
from services.supabase_client import SupabaseClientService, ClientCRUD, DealCRUD

async def main():
    # Рекомендуемый способ - с context manager для автоматической очистки
    async with SupabaseClientService.get_instance(
        url="https://qqtpcbynnczpalqhsyex.supabase.co",
        key="your-anon-key"
    ) as supabase_service:
        # Проверка подключения
        is_healthy = await supabase_service.health_check()
        print(f"Supabase connected: {is_healthy}")

        # Инициализация CRUD сервисов
        client_crud = ClientCRUD(supabase_service)
        deal_crud = DealCRUD(supabase_service)

        # Ваш код здесь...
        client = await client_crud.create()

    # Соединение автоматически закроется при выходе из контекста

if __name__ == "__main__":
    asyncio.run(main())
```

### Альтернативный способ (без context manager)

```python
async def main():
    supabase_service = SupabaseClientService.get_instance(
        url="https://qqtpcbynnczpalqhsyex.supabase.co",
        key="your-anon-key"
    )

    try:
        is_healthy = await supabase_service.health_check()
        client_crud = ClientCRUD(supabase_service)
        # Ваш код...
    finally:
        # Явное закрытие соединения
        await supabase_service.close()
```

### Client CRUD

```python
# Создание клиента
client = await client_crud.create()
# Вернет: {"id": 1, "created_at": "2025-11-23T..."}

# Получение по ID
client = await client_crud.get_by_id(1)

# Получение всех (с пагинацией)
clients = await client_crud.get_all(limit=50, offset=0)

# Подсчет
total = await client_crud.count()

# Удаление
await client_crud.delete(client_id=1)
```

### Deal CRUD

```python
# Создание сделки
deal = await deal_crud.create(
    client_id=1,
    raw_request="Хочу купить квартиру в центре",
    request_params={
        "location": "center",
        "rooms": 2,
        "budget": 5000000
    },
    status="new",
    ui_state={
        "step": 1,
        "completed": False
    }
)

# Получение по UUID
deal = await deal_crud.get_by_id(deal["id"])

# Получение всех сделок клиента
deals = await deal_crud.get_by_client_id(
    client_id=1,
    limit=100,
    offset=0
)

# Получение всех сделок
all_deals = await deal_crud.get_all(limit=100, offset=0)

# Обновление сделки
updated = await deal_crud.update(
    deal_id=deal["id"],
    status="in_progress",
    ui_state={"step": 2, "completed": False}
)

# Подсчет сделок
total_deals = await deal_crud.count()
client_deals = await deal_crud.count(client_id=1)

# Удаление
await deal_crud.delete(deal_id=deal["id"])
```

## Важные особенности

### 1. Асинхронность
Все методы асинхронные, используют `acreate_client()` для поддержки Realtime:

```python
client = await supabase_service.get_client()
```

### 2. Singleton паттерн
`SupabaseClientService` использует Singleton для переиспользования подключения:

```python
# Первый вызов создает инстанс
service1 = SupabaseClientService.get_instance(url, key)

# Второй вызов возвращает тот же инстанс
service2 = SupabaseClientService.get_instance(url, key)

assert service1 is service2  # True
```

### 3. Логирование
Все операции логируются через `structlog`:

```python
logger.info(f"Created new client: {client_id}")
logger.debug(f"Retrieved {len(clients)} clients")
logger.error(f"Failed to create deal: {error}")
```

### 4. Обработка ошибок
Все методы выбрасывают исключения при ошибках:

```python
try:
    client = await client_crud.create()
except Exception as e:
    logger.error(f"Failed: {e}")
```

## Схема БД

### Таблица `client`
- `id` - bigint (PK, auto-increment)
- `created_at` - timestamptz (default: now())

### Таблица `deal`
- `id` - uuid (PK)
- `created_at` - timestamptz (default: now())
- `client_id` - bigint (FK → client.id, nullable)
- `raw_request` - text (nullable)
- `request_params` - jsonb (nullable)
- `status` - text (nullable)
- `ui_state` - jsonb (nullable)

## Переменные окружения

```bash
SUPABASE_URL=https://qqtpcbynnczpalqhsyex.supabase.co
SUPABASE_KEY=your-anon-key
```
