# GenUI Agent Architecture

## Общая схема

GenUI Agent — это агент-инструмент, который трансформирует JSON-состояние страницы сделки.
Фронтенд динамически рендерит компоненты на основе этого JSON.

---

## Frontend Structure (Next.js)

```
real-estate-frontend/
├── components/deal-blocks/         # UI компоненты с TypeScript типами
│   ├── ApartmentCards.tsx
│   ├── ProjectList.tsx
│   ├── VillaCards.tsx
│   ├── Filters.tsx
│   ├── Summary.tsx
│   ├── TextBlock.tsx
│   ├── ComparisonTable.tsx
│   └── Map.tsx
│
├── public/component-schemas/       # Генерируются скриптом из TS типов
│   ├── apartment_cards.json
│   ├── project_list.json
│   ├── villa_cards.json
│   └── ...
│
├── scripts/
│   └── generate-schemas.ts         # Скрипт: TS типы → JSON схемы
│
├── app/
│   ├── api/ui-components/
│   │   └── route.ts                # API: список компонентов + схемы
│   │
│   └── deal/[id]/
│       └── page.tsx                # Страница сделки + чат (модалка/sidebar)
│
└── lib/
    └── deal-renderer.tsx           # Динамический рендер блоков по JSON
```

---

## Backend Structure (agent-orchestrator)

```
agent-orchestrator/
├── agent/
│   ├── genui/
│   │   ├── __init__.py
│   │   ├── ARCHITECTURE.md         # Этот файл
│   │   ├── agent.py                # GenUI LangGraph агент
│   │   ├── state.py                # State schema
│   │   ├── tools.py                # Internal tools (read/write state)
│   │   └── README.md               # Инструкции для GenUI
│   │
│   └── tools/
│       └── genui_tool.py           # Tool для главного агента
│
└── services/
    └── supabase_client/
        └── deal_crud.py            # CRUD для таблицы deal (ui_state)
```

---

## Data Flow

### 1. Генерация схем компонентов (Frontend Build Time)

```bash
# На фронтенде
pnpm run generate-schemas
```

**Скрипт делает:**
- Читает TypeScript типы из `components/deal-blocks/*.tsx`
- Генерирует JSON Schema для каждого компонента
- Сохраняет в `public/component-schemas/*.json`

**Пример: ApartmentCards.tsx**
```tsx
export interface ApartmentCardsProps {
  items: Array<{
    id: string;
    type: "studio" | "1br" | "2br" | "3br" | "4br" | "penthouse";
    area: number;
    price: number;
    currency?: string;
    status: "available" | "reserved" | "sold";
    floor?: number;
    project_id: string;
    images?: string[];
  }>;
}
```

**Генерируется: public/component-schemas/apartment_cards.json**
```json
{
  "type": "apartment_cards",
  "name": "Apartment Cards",
  "description": "Карточки апартаментов",
  "props_schema": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string", "enum": ["studio", "1br", "2br", "3br", "4br", "penthouse"] },
          "area": { "type": "number" },
          "price": { "type": "number" },
          ...
        }
      }
    }
  }
}
```

---

### 2. GenUI Agent запрашивает схемы (Runtime)

**GenUI Agent → Next.js API**
```
GET https://frontend.app/api/ui-components
```

**Response:**
```json
{
  "components": [
    {
      "type": "apartment_cards",
      "name": "Apartment Cards",
      "description": "Карточки апартаментов",
      "schema": { ... }
    },
    {
      "type": "project_list",
      ...
    }
  ]
}
```

GenUI Agent кэширует эти схемы и использует их для валидации.

---

### 3. Создание/Обновление сделки

**User → Realtor Agent (Orchestrator)**
```
POST /chat
{
  "thread_id": "user-123",
  "message": "Найди апартаменты 2br в Dubai Marina до 2M AED"
}
```

**Realtor Agent:**
1. Анализирует запрос
2. Вызывает `apartments_search` tool → получает данные
3. Вызывает `genui_tool` с инструкцией:

```python
genui_tool(
    deal_id="deal-abc-123",
    instruction="Добавь на страницу карточки найденных апартаментов и summary блок"
)
```

**GenUI Agent (внутри genui_tool):**
1. Читает текущий `ui_state` из Supabase (`DealCRUD.get_by_id()`)
2. Анализирует инструкцию (LangGraph reasoning)
3. Решает, какие блоки добавить/изменить
4. Формирует новый JSON:

```json
{
  "deal_id": "deal-abc-123",
  "blocks": [
    {
      "type": "filters",
      "props": {
        "bedrooms": "2br",
        "location": "Dubai Marina",
        "price_max": 2000000
      }
    },
    {
      "type": "apartment_cards",
      "props": {
        "items": [
          { "id": "apt-1", "type": "2br", "area": 120, "price": 1500000, ... },
          { "id": "apt-2", "type": "2br", "area": 135, "price": 1800000, ... }
        ]
      }
    },
    {
      "type": "summary",
      "props": {
        "total_found": 2,
        "average_price": 1650000,
        "message": "Найдено 2 апартамента в Dubai Marina"
      }
    }
  ]
}
```

5. Валидирует против схем компонентов
6. Сохраняет в Supabase (`DealCRUD.update(ui_state=new_state)`)

---

### 4. Рендеринг на фронтенде

**Frontend → Backend**
```
GET /api/deal/{deal_id}/state
```

**Response:**
```json
{
  "deal_id": "deal-abc-123",
  "blocks": [ ... ],
  "metadata": {
    "last_updated": "2025-12-07T20:00:00Z"
  }
}
```

**Frontend:**
```tsx
// app/deal/[id]/page.tsx
export default function DealPage({ params }) {
  const { data } = useDealState(params.id);

  return (
    <div className="flex">
      <main className="flex-1">
        <DealRenderer blocks={data.blocks} />
      </main>
      <aside>
        <ChatModal dealId={params.id} />
      </aside>
    </div>
  );
}

// lib/deal-renderer.tsx
function DealRenderer({ blocks }) {
  return blocks.map((block) => {
    switch (block.type) {
      case "apartment_cards":
        return <ApartmentCards {...block.props} />;
      case "project_list":
        return <ProjectList {...block.props} />;
      // ...
    }
  });
}
```

---

## Страница сделки (UI/UX)

### Вариант 1: Чат в модалке
```
┌─────────────────────────────────────────┐
│  [Deal #abc-123]           [💬 Chat]    │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────┐       │
│  │ Filters Block               │       │
│  └─────────────────────────────┘       │
│                                         │
│  ┌─────────────────────────────┐       │
│  │ Apartment Cards Block       │       │
│  │  - Apartment 1              │       │
│  │  - Apartment 2              │       │
│  └─────────────────────────────┘       │
│                                         │
│  ┌─────────────────────────────┐       │
│  │ Summary Block               │       │
│  └─────────────────────────────┘       │
└─────────────────────────────────────────┘
```

При клике на [💬 Chat] → открывается модалка с чатом.

### Вариант 2: Чат в сайдбаре (split screen)
```
┌──────────────────────────┬──────────────┐
│  [Deal #abc-123]         │  💬 Chat     │
├──────────────────────────┤              │
│                          │  User: ...   │
│  Filters Block           │  Agent: ...  │
│                          │              │
│  Apartment Cards Block   │  [Send...]   │
│   - Apartment 1          │              │
│   - Apartment 2          │              │
│                          │              │
│  Summary Block           │              │
│                          │              │
└──────────────────────────┴──────────────┘
```

---

## API Endpoints

### Backend (agent-orchestrator)

**GET /api/deal/{deal_id}/state**
- Возвращает JSON состояние UI для сделки

**POST /chat**
- Чат с Realtor Agent
- Может вызывать GenUI для обновления UI

### Frontend (Next.js)

**GET /api/ui-components**
- Возвращает список + схемы всех доступных компонентов
- Используется GenUI Agent для валидации

**GET /api/deal/[id]**
- Прокси к backend `/api/deal/{id}/state`

---

## Принципы работы

1. **Single Source of Truth**: `ui_state` в Supabase
2. **Schema-Driven**: Фронтенд генерирует схемы из TS типов
3. **Validation**: GenUI валидирует JSON перед сохранением
4. **Deterministic Rendering**: Фронтенд просто рендерит блоки по порядку
5. **Separation of Concerns**:
   - Realtor Agent: мышление, диалог, данные
   - GenUI Agent: трансформация UI
   - Frontend: рендеринг

---

## Next Steps

1. ✅ Создать структуру `agent/genui/`
2. ⬜ Реализовать скрипт генерации схем на фронте
3. ⬜ Создать компоненты в `components/deal-blocks/`
4. ⬜ Реализовать Next.js API `/api/ui-components`
5. ⬜ Реализовать GenUI Agent (LangGraph)
6. ⬜ Создать endpoint `/api/deal/{id}/state`
7. ⬜ Реализовать страницу сделки + чат
