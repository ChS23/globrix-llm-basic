/**
 * Dynamic block renderer for deal pages.
 *
 * Renders UI blocks based on JSON state from backend.
 */

import React from "react";
import { ApartmentCards } from "@/components/deal-blocks/ApartmentCards";
import { VillaCards } from "@/components/deal-blocks/VillaCards";
import { ProjectList } from "@/components/deal-blocks/ProjectList";
import { Filters } from "@/components/deal-blocks/Filters";
import { Summary } from "@/components/deal-blocks/Summary";
import { TextBlock } from "@/components/deal-blocks/TextBlock";
import { ComparisonTable } from "@/components/deal-blocks/ComparisonTable";
import { MapBlock } from "@/components/deal-blocks/MapBlock";
import { AmenitiesList } from "@/components/deal-blocks/AmenitiesList";
import { Timeline } from "@/components/deal-blocks/Timeline";
import type { Block } from "@/components/deal-blocks/types";

interface DealRendererProps {
  blocks: Block[];
}

export function DealRenderer({ blocks }: DealRendererProps) {
  if (!blocks || blocks.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-gray-500">
        <div className="text-center">
          <p className="text-lg mb-2">No content yet</p>
          <p className="text-sm">Start chatting to build this deal page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {blocks.map((block, index) => (
        <BlockRenderer key={index} block={block} index={index} />
      ))}
    </div>
  );
}

function BlockRenderer({ block, index }: { block: Block; index: number }) {
  const { type, props } = block;

  try {
    switch (type) {
      case "apartment_cards":
        return <ApartmentCards {...props} />;

      case "filters":
        return <Filters {...props} />;

      case "summary":
        return <Summary {...props} />;

      case "text":
        return <TextBlock {...props} />;

      case "villa_cards":
        return <VillaCards {...props} />;

      case "project_list":
        return <ProjectList {...props} />;

      case "comparison_table":
        return <ComparisonTable {...props} />;

      case "map":
        return <MapBlock {...props} />;

      case "amenities":
        return <AmenitiesList {...props} />;

      case "timeline":
        return <Timeline {...props} />;

      default:
        return (
          <div className="p-4 bg-red-50 border border-red-200 rounded">
            <p className="text-red-800 font-medium">Unknown block type: {type}</p>
            <pre className="text-xs mt-2 text-gray-600">
              {JSON.stringify(block, null, 2)}
            </pre>
          </div>
        );
    }
  } catch (error) {
    console.error(`Error rendering block ${index} (type: ${type}):`, error);
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded">
        <p className="text-red-800 font-medium">Error rendering block</p>
        <p className="text-sm text-gray-600 mt-1">
          {error instanceof Error ? error.message : "Unknown error"}
        </p>
      </div>
    );
  }
}
