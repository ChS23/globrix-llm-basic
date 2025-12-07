# Globrix Frontend

Next.js frontend для AI-powered системы управления сделками в недвижимости.

## Архитектура

Динамический UI, управляемый JSON-состоянием из backend.

- **Dynamic Block Rendering** - компоненты рендерятся на основе JSON
- **AI Chat Integration** - чат с Realtor Agent для управления сделкой
- **Schema-Driven** - TypeScript типы генерируют JSON схемы для агента

## Структура

```
real-estate-frontend/
├── app/
│   ├── page.tsx                    # Главная страница (создание/открытие сделки)
│   ├── deal/[id]/page.tsx          # Страница сделки (динамический рендер + чат)
│   └── api/ui-components/route.ts  # API для получения схем компонентов
│
├── components/
│   ├── deal-blocks/                # UI компоненты для блоков
│   │   ├── ApartmentCards.tsx
│   │   ├── Filters.tsx
│   │   ├── Summary.tsx
│   │   ├── TextBlock.tsx
│   │   ├── types.ts                # TypeScript типы
│   │   └── index.ts
│   └── chat/
│       └── ChatPanel.tsx           # Чат с агентом
│
├── lib/
│   ├── deal-renderer.tsx           # Динамический рендерер блоков
│   └── hooks/
│       └── useDealState.ts         # Hook для получения состояния сделки
│
├── scripts/
│   └── generate-schemas.ts         # Генерация JSON схем из TS типов
│
└── public/
    └── component-schemas/          # Генерируемые JSON схемы
        ├── apartment_cards.json
        ├── filters.json
        └── index.json
```

## Quick Start

### 1. Установка зависимостей

```bash
pnpm install
# или
npm install
```

### 2. Настройка окружения

Создайте `.env.local`:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 3. Генерация JSON схем

```bash
pnpm generate-schemas
```

Это создаст JSON Schema файлы в `public/component-schemas/` на основе TypeScript типов.

### 4. Запуск dev сервера

```bash
pnpm dev
```

Откройте [http://localhost:3000](http://localhost:3000)

## Работа с UI компонентами

### Добавление нового компонента

1. **Создайте TypeScript интерфейс** в `components/deal-blocks/types.ts`:

```typescript
export interface NewComponentProps {
  title: string;
  items: string[];
}
```

2. **Создайте React компонент**:

```tsx
// components/deal-blocks/NewComponent.tsx
import type { NewComponentProps } from "./types";

export function NewComponent({ title, items }: NewComponentProps) {
  return (
    <div>
      <h3>{title}</h3>
      <ul>
        {items.map((item, i) => <li key={i}>{item}</li>)}
      </ul>
    </div>
  );
}
```

3. **Экспортируйте** в `components/deal-blocks/index.ts`:

```typescript
export { NewComponent } from "./NewComponent";
export type { NewComponentProps } from "./types";
```

4. **Добавьте в генератор схем** `scripts/generate-schemas.ts`:

```typescript
const COMPONENTS = [
  // ...existing
  {
    type: "new_component",
    name: "New Component",
    description: "Description here",
    propsType: "NewComponentProps",
  },
];
```

5. **Добавьте в рендерер** `lib/deal-renderer.tsx`:

```typescript
case "new_component":
  return <NewComponent {...props} />;
```

6. **Сгенерируйте схемы**:

```bash
pnpm generate-schemas
```

## API Endpoints

### GET /api/ui-components

Возвращает JSON схемы всех доступных компонентов.

**Response:**
```json
{
  "version": "1.0.0",
  "components": ["apartment_cards", "filters", "summary", "text"],
  "schemas": {
    "apartment_cards": {
      "type": "apartment_cards",
      "name": "Apartment Cards",
      "props_schema": { ... }
    }
  }
}
```

### GET /api/ui-components?type=apartment_cards

Возвращает схему конкретного компонента.

## Компоненты

### ApartmentCards
Карточки апартаментов с ценой, площадью, статусом.

**Props:** `ApartmentCardsProps`

### Filters
Активные фильтры поиска (цена, локация, тип).

**Props:** `FiltersProps`

### Summary
Итоговая статистика по результатам поиска.

**Props:** `SummaryProps`

### TextBlock
Произвольный текстовый блок (Markdown, варианты: info/warning/error).

**Props:** `TextBlockProps`

### ChatPanel
Панель чата с Realtor Agent.

**Props:** `ChatPanelProps`

## Интеграция с Backend

### useDealState Hook

```typescript
import { useDealState } from "@/lib/hooks/useDealState";

const { data, isLoading, error, refetch } = useDealState("deal-123");
```

### Страница сделки

```
┌─────────────────────────────────┬──────────────┐
│  Deal: deal-123        [Refresh]│  Chat        │
├─────────────────────────────────┤              │
│                                 │  User: ...   │
│  [Filters Block]                │  Agent: ...  │
│                                 │              │
│  [Apartment Cards Block]        │  [Send...]   │
│   - Apartment 1                 │              │
│   - Apartment 2                 │              │
│                                 │              │
│  [Summary Block]                │              │
└─────────────────────────────────┴──────────────┘
```

## Development

### Scripts

```bash
# Dev сервер
pnpm dev

# Генерация схем
pnpm generate-schemas

# Build
pnpm build

# Start production
pnpm start

# Lint
pnpm lint
```

### Tech Stack

- **Next.js 16** - React framework
- **TypeScript 5** - Type safety
- **Tailwind CSS 4** - Styling
- **ts-json-schema-generator** - Schema generation

## Environment Variables

```bash
# Required
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000  # URL бэкенда (agent-orchestrator)
```

## См. также

- [Components README](./components/deal-blocks/README.md) - детали по UI компонентам
- [Backend API](../agent-orchestrator/README.md) - документация бэкенда
- [GenUI Agent](../agent-orchestrator/agent/genui/README.md) - архитектура GenUI Agent
