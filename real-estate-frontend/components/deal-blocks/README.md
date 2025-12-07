# Deal Blocks Components

UI компоненты для динамического рендеринга страницы сделки.

## Структура

```
components/deal-blocks/
├── types.ts              # TypeScript типы и интерфейсы
├── ApartmentCards.tsx    # Компонент карточек апартаментов
├── Filters.tsx           # Компонент активных фильтров
├── Summary.tsx           # Компонент итоговой информации
├── TextBlock.tsx         # Текстовый блок (Markdown)
└── index.ts              # Экспорты
```

## Генерация JSON схем

Схемы автоматически генерируются из TypeScript типов:

```bash
pnpm generate-schemas
```

Это создаст файлы в `public/component-schemas/`:
- `apartment_cards.json`
- `filters.json`
- `summary.json`
- `text.json`
- `index.json` (сводный файл)

## API Endpoint

**GET /api/ui-components**
- Возвращает все доступные компоненты и их схемы

**GET /api/ui-components?type=apartment_cards**
- Возвращает схему конкретного компонента

### Пример ответа

```json
{
  "version": "1.0.0",
  "generated_at": "2025-12-07T20:00:00Z",
  "components": ["apartment_cards", "filters", "summary", "text"],
  "schemas": {
    "apartment_cards": {
      "type": "apartment_cards",
      "name": "Apartment Cards",
      "description": "Карточки апартаментов",
      "props_schema": { ... }
    }
  }
}
```

## Использование в GenUI Agent

GenUI Agent запрашивает схемы при инициализации:

```python
# Получить список доступных компонентов
response = requests.get("https://frontend/api/ui-components")
schemas = response.json()["schemas"]

# Валидировать блок перед сохранением
block = {
    "type": "apartment_cards",
    "props": { "items": [...] }
}

# Проверка на соответствие схеме
validate_block(block, schemas["apartment_cards"]["props_schema"])
```

## Добавление нового компонента

1. **Создать TypeScript интерфейс** в `types.ts`:
```typescript
export interface NewComponentProps {
  title: string;
  items: string[];
}
```

2. **Создать React компонент** `NewComponent.tsx`:
```tsx
import type { NewComponentProps } from "./types";

export function NewComponent({ title, items }: NewComponentProps) {
  return <div>...</div>;
}
```

3. **Экспортировать** в `index.ts`:
```typescript
export { NewComponent } from "./NewComponent";
export type { NewComponentProps } from "./types";
```

4. **Добавить в скрипт** `scripts/generate-schemas.ts`:
```typescript
const COMPONENTS = [
  // ...existing
  {
    type: "new_component",
    name: "New Component",
    description: "Description",
    propsType: "NewComponentProps",
  },
];
```

5. **Сгенерировать схемы**:
```bash
pnpm generate-schemas
```

## Компоненты

### ApartmentCards
Отображение карточек апартаментов с ценой, площадью, статусом.

**Props:** `ApartmentCardsProps`

### Filters
Отображение активных фильтров поиска (цена, локация, тип).

**Props:** `FiltersProps`

### Summary
Итоговая статистика по результатам поиска.

**Props:** `SummaryProps`

### TextBlock
Произвольный текстовый блок с поддержкой Markdown и вариантов (info, warning, error).

**Props:** `TextBlockProps`
