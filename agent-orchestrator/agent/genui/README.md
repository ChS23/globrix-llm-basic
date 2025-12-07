# GenUI Agent

GenUI Agent — это специализированный агент для трансформации JSON-состояния UI страницы сделки.

## Назначение

GenUI Agent работает как **Agent-as-a-Tool** для главного агента (Realtor Agent).

Он **НЕ** ведёт диалоги с пользователем.
Он **НЕ** принимает решения о бизнес-логике.
Он **ТОЛЬКО** трансформирует UI состояние на основе инструкций.

## Архитектура

```
Realtor Agent
    │
    ├── analyze request
    ├── fetch data (apartments, projects, etc.)
    │
    └── call genui_tool(deal_id, instruction)
            │
            ▼
        GenUI Agent (LangGraph)
            │
            ├── load_context
            │   ├── read current UI state from Supabase
            │   └── fetch component schemas from frontend
            │
            ├── analyze_instruction
            │   └── LLM reasoning about what to change
            │
            ├── transform_ui
            │   ├── generate new blocks (JSON)
            │   └── validate against schemas
            │
            └── save_state
                └── write to Supabase
```

## Использование

### Из Realtor Agent

```python
from agent.tools.genui_tool import genui_tool

# В главном агенте
result = await genui_tool(
    deal_id="abc-123",
    instruction="Add apartment cards with search results"
)
```

### Прямой вызов GenUI Agent

```python
from agent.genui.agent import GenUIAgent

agent = GenUIAgent()

result = await agent.run(
    deal_id="abc-123",
    instruction="Add filters block: location=Dubai Marina, bedrooms=2br"
)

if result["success"]:
    print(f"Created {len(result['blocks'])} blocks")
else:
    print(f"Error: {result['error']}")
```

## Компоненты

### agent.py
Основной LangGraph агент с reasoning.

**Nodes:**
- `load_context` - загрузка текущего состояния и схем
- `analyze_instruction` - анализ инструкции через LLM
- `transform_ui` - генерация новых блоков
- `save_state` - сохранение в Supabase

### state.py
TypedDict схема состояния GenUI Agent.

**Поля:**
- `deal_id` - UUID сделки
- `instruction` - инструкция от главного агента
- `current_blocks` - текущие блоки из Supabase
- `new_blocks` - новые блоки после трансформации
- `component_schemas` - схемы компонентов с фронтенда
- `reasoning` - промежуточные рассуждения LLM
- `error` - ошибка, если произошла

### tools.py
Internal tools для работы с данными.

**Functions:**
- `read_deal_state(deal_id)` - читает UI state из Supabase
- `write_deal_state(deal_id, blocks, metadata)` - пишет в Supabase
- `fetch_component_schemas()` - получает схемы с фронтенда
- `validate_block(block)` - валидирует блок против схемы
- `validate_blocks(blocks)` - валидирует массив блоков

## Environment Variables

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
ANTHROPIC_API_KEY=sk-ant-...
FRONTEND_URL=http://localhost:3000

# Optional
GENUI_MODEL=claude-3-5-sonnet-20241022  # По умолчанию
```

## Примеры инструкций

```python
# Добавить карточки апартаментов
instruction = "Add apartment cards with 5 items"

# Показать фильтры
instruction = "Show filters: location=Dubai Marina, bedrooms=2br, price_max=2000000"

# Добавить summary блок
instruction = "Add summary: 42 apartments found, average price 1.75M AED"

# Обновить существующие блоки
instruction = "Update filters: change location to Business Bay"

# Комплексная инструкция
instruction = """
Add the following blocks:
1. Filters block with: location=Dubai Marina, bedrooms=2br
2. Apartment cards with search results (5 items)
3. Summary block: total 42 apartments, average price 1.75M
"""
```

## Workflow

### 1. Чтение состояния

```python
ui_state = await read_deal_state("abc-123")
# {
#   "deal_id": "abc-123",
#   "blocks": [...],
#   "metadata": {...}
# }
```

### 2. Анализ инструкции

LLM анализирует инструкцию и текущее состояние:

```
REASONING: User wants to add apartment cards. Current page has only filters.
Need to add apartment_cards block after filters.

ACTIONS:
- Keep existing filters block
- Add apartment_cards block with items
```

### 3. Генерация блоков

LLM генерирует JSON блоков:

```json
[
  {
    "type": "filters",
    "props": { "location": "Dubai Marina", "bedrooms": "2br" }
  },
  {
    "type": "apartment_cards",
    "props": {
      "items": [...]
    }
  }
]
```

### 4. Валидация

Каждый блок валидируется против схемы компонента с фронтенда.

### 5. Сохранение

Обновлённое состояние сохраняется в Supabase:

```python
await write_deal_state(
    deal_id="abc-123",
    blocks=new_blocks,
    metadata={"last_updated": "2025-12-07T20:00:00Z"}
)
```

## Добавление нового типа блока

1. **На фронтенде:** создать компонент + типы
2. **Сгенерировать схему:** `pnpm generate-schemas`
3. **GenUI автоматически подхватит** новый тип через API

Никаких изменений в GenUI Agent не требуется!

## Отладка

```python
import structlog
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
)

# Теперь все logger.debug() будут видны
```

## См. также

- [ARCHITECTURE.md](./ARCHITECTURE.md) - полная архитектура системы
- [../../README.md](../../README.md) - документация по Realtor Agent
- [frontend/components/deal-blocks/README.md](../../../real-estate-frontend/components/deal-blocks/README.md) - UI компоненты
