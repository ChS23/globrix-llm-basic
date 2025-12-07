/**
 * Типы для UI блоков сделки.
 * Эти типы используются для генерации JSON схем через скрипт generate-schemas.ts
 */

// === Base Types ===

export type PropertyStatus = "available" | "reserved" | "sold";
export type ApartmentType = "studio" | "1br" | "2br" | "3br" | "4br" | "penthouse";
export type Currency = "AED" | "USD" | "EUR";

// === Apartment ===

export interface Apartment {
  id: string;
  type: ApartmentType;
  area: number;
  price: number;
  currency?: Currency;
  status: PropertyStatus;
  floor?: number;
  project_id: string;
  images?: string[];
  bedrooms?: number;
  bathrooms?: number;
  developer?: string;
  completion_date?: string;
}

// === Villa ===

export interface Villa {
  id: string;
  bedrooms: number;
  bathrooms?: number;
  area: number;
  plot_area?: number;
  price: number;
  currency?: Currency;
  location: string;
  amenities?: string[];
  images?: string[];
  status?: PropertyStatus;
}

// === Project ===

export interface Project {
  id: string;
  name: string;
  developer: string;
  location: string;
  total_units: number;
  image_url?: string;
  completion_date?: string;
  min_price?: number;
  max_price?: number;
}

// === Block Props ===

export interface ApartmentCardsProps {
  items: Apartment[];
}

export interface VillaCardsProps {
  items: Villa[];
}

export interface ProjectListProps {
  projects: Project[];
}

export interface FiltersProps {
  price_min?: number;
  price_max?: number;
  bedrooms?: ApartmentType;
  location?: string;
  property_type?: "apartment" | "villa";
  status?: PropertyStatus;
}

export interface SummaryProps {
  total_found: number;
  average_price?: number;
  message: string;
  stats?: {
    min_price?: number;
    max_price?: number;
    avg_area?: number;
  };
}

export interface TextBlockProps {
  content: string;
  variant?: "default" | "info" | "warning" | "error";
}

export interface ComparisonTableProps {
  items: Array<Record<string, any>>;
  columns: Array<{
    key: string;
    label: string;
    type: "text" | "number" | "currency";
  }>;
}

export interface MapProps {
  center: {
    lat: number;
    lng: number;
  };
  markers: Array<{
    id: string;
    lat: number;
    lng: number;
    title: string;
    price?: number;
  }>;
  zoom?: number;
}

// === Block Types ===

export type BlockType =
  | "apartment_cards"
  | "villa_cards"
  | "project_list"
  | "filters"
  | "summary"
  | "text"
  | "comparison_table"
  | "map";

export interface Block<T = any> {
  type: BlockType;
  props: T;
}

// === Deal State ===

export interface DealState {
  deal_id: string;
  blocks: Block[];
  metadata?: {
    schema_version?: string;
    last_updated?: string;
  };
}
