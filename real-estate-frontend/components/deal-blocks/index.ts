/**
 * Deal Blocks - UI компоненты для динамического рендеринга страницы сделки.
 *
 * Эти компоненты используются GenUI Agent для построения UI страницы сделки.
 * Каждый компонент имеет строгую TypeScript типизацию, которая используется
 * для генерации JSON схем через скрипт generate-schemas.ts.
 */

export { ApartmentCards } from "./ApartmentCards";
export { Filters } from "./Filters";
export { Summary } from "./Summary";
export { TextBlock } from "./TextBlock";

export type {
  // Base Types
  PropertyStatus,
  ApartmentType,
  Currency,

  // Entity Types
  Apartment,
  Villa,
  Project,

  // Component Props
  ApartmentCardsProps,
  VillaCardsProps,
  ProjectListProps,
  FiltersProps,
  SummaryProps,
  TextBlockProps,
  ComparisonTableProps,
  MapProps,

  // Block Types
  BlockType,
  Block,
  DealState,
} from "./types";
