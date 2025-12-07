/**
 * API endpoint для получения схем UI компонентов.
 *
 * GET /api/ui-components
 * - Возвращает список всех доступных компонентов и их JSON схемы
 *
 * GET /api/ui-components?type=apartment_cards
 * - Возвращает схему конкретного компонента
 *
 * Используется GenUI Agent для валидации и построения UI блоков.
 */

import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const SCHEMAS_DIR = path.join(process.cwd(), "public", "component-schemas");

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const componentType = searchParams.get("type");

    // If specific component requested
    if (componentType) {
      return getComponentSchema(componentType);
    }

    // Otherwise return all schemas
    return getAllSchemas();
  } catch (error) {
    console.error("Error fetching UI component schemas:", error);
    return NextResponse.json(
      { error: "Failed to fetch component schemas" },
      { status: 500 }
    );
  }
}

/**
 * Get schema for a specific component type
 */
function getComponentSchema(componentType: string) {
  const schemaPath = path.join(SCHEMAS_DIR, `${componentType}.json`);

  if (!fs.existsSync(schemaPath)) {
    return NextResponse.json(
      { error: `Component type '${componentType}' not found` },
      { status: 404 }
    );
  }

  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf-8"));

  return NextResponse.json(schema);
}

/**
 * Get all component schemas
 */
function getAllSchemas() {
  const indexPath = path.join(SCHEMAS_DIR, "index.json");

  // If index.json exists, use it
  if (fs.existsSync(indexPath)) {
    const indexData = JSON.parse(fs.readFileSync(indexPath, "utf-8"));
    return NextResponse.json(indexData);
  }

  // Otherwise, read all schema files
  const schemas: Record<string, any> = {};
  const componentTypes: string[] = [];

  if (!fs.existsSync(SCHEMAS_DIR)) {
    return NextResponse.json({
      version: "1.0.0",
      components: [],
      schemas: {},
      warning: "Schema directory does not exist. Run 'pnpm generate-schemas' first.",
    });
  }

  const files = fs.readdirSync(SCHEMAS_DIR);

  for (const file of files) {
    if (file.endsWith(".json") && file !== "index.json") {
      const componentType = file.replace(".json", "");
      const schemaPath = path.join(SCHEMAS_DIR, file);
      const schema = JSON.parse(fs.readFileSync(schemaPath, "utf-8"));

      schemas[componentType] = schema;
      componentTypes.push(componentType);
    }
  }

  return NextResponse.json({
    version: "1.0.0",
    generated_at: new Date().toISOString(),
    components: componentTypes,
    schemas,
  });
}
