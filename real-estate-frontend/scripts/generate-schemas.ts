/**
 * Скрипт для генерации JSON схем из TypeScript типов.
 *
 * Использует ts-json-schema-generator для автоматической генерации
 * JSON Schema напрямую из TypeScript интерфейсов в types.ts
 *
 * Usage:
 *   pnpm generate-schemas
 */

import fs from "fs";
import path from "path";
import { createGenerator } from "ts-json-schema-generator";

// === Configuration ===

const TYPES_FILE = path.join(
  process.cwd(),
  "components/deal-blocks/types.ts"
);

const OUTPUT_DIR = path.join(process.cwd(), "public/component-schemas");

// Компоненты и их соответствующие Props типы
const COMPONENTS = [
  {
    type: "apartment_cards",
    name: "Apartment Cards",
    description: "Карточки апартаментов",
    propsType: "ApartmentCardsProps",
  },
  {
    type: "villa_cards",
    name: "Villa Cards",
    description: "Карточки вилл",
    propsType: "VillaCardsProps",
  },
  {
    type: "project_list",
    name: "Project List",
    description: "Список проектов",
    propsType: "ProjectListProps",
  },
  {
    type: "filters",
    name: "Search Filters",
    description: "Активные фильтры поиска",
    propsType: "FiltersProps",
  },
  {
    type: "summary",
    name: "Search Summary",
    description: "Итоговая информация по результатам поиска",
    propsType: "SummaryProps",
  },
  {
    type: "text",
    name: "Text Block",
    description: "Текстовый блок с поддержкой Markdown",
    propsType: "TextBlockProps",
  },
  {
    type: "comparison_table",
    name: "Comparison Table",
    description: "Таблица сравнения объектов",
    propsType: "ComparisonTableProps",
  },
  {
    type: "map",
    name: "Location Map",
    description: "Карта с отображением объектов",
    propsType: "MapProps",
  },
];

// === Main Logic ===

function generateSchemas() {
  console.log("🔄 Generating JSON schemas from TypeScript types...\n");

  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const config = {
    path: TYPES_FILE,
    tsconfig: path.join(process.cwd(), "tsconfig.json"),
    type: "*", // Генерируем для всех типов
    skipTypeCheck: true,
    expose: "all",
    topRef: false,
    jsDoc: "extended",
  };

  const allSchemas: Record<string, any> = {};

  // Generate schema for each component
  for (const component of COMPONENTS) {
    try {
      // Create generator for this specific type
      const generator = createGenerator({
        ...config,
        type: component.propsType,
      });

      // Generate JSON Schema
      const propsSchema = generator.createSchema(component.propsType);

      // Build component schema
      const componentSchema = {
        type: component.type,
        name: component.name,
        description: component.description,
        props_schema: propsSchema,
      };

      // Save individual schema file
      const filePath = path.join(OUTPUT_DIR, `${component.type}.json`);
      fs.writeFileSync(
        filePath,
        JSON.stringify(componentSchema, null, 2),
        "utf-8"
      );

      console.log(`✓ Generated: ${component.type}.json`);

      allSchemas[component.type] = componentSchema;
    } catch (error) {
      console.error(`✗ Failed to generate ${component.type}:`, error);
    }
  }

  // Generate index file with all schemas
  const indexPath = path.join(OUTPUT_DIR, "index.json");
  const indexData = {
    version: "1.0.0",
    generated_at: new Date().toISOString(),
    components: COMPONENTS.map((c) => c.type),
    schemas: allSchemas,
  };

  fs.writeFileSync(indexPath, JSON.stringify(indexData, null, 2), "utf-8");
  console.log(`✓ Generated: index.json`);

  console.log(
    `\n✅ Successfully generated ${Object.keys(allSchemas).length} component schemas`
  );
  console.log(`📁 Output directory: ${OUTPUT_DIR}\n`);
}

// Run
try {
  generateSchemas();
} catch (error) {
  console.error("❌ Error generating schemas:", error);
  process.exit(1);
}
