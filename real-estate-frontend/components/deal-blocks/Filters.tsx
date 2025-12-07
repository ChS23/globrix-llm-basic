import React from "react";
import type { FiltersProps } from "./types";

/**
 * Компонент для отображения активных фильтров поиска.
 * Показывает текущие параметры поиска недвижимости.
 */
export function Filters({
  price_min,
  price_max,
  bedrooms,
  location,
  property_type,
  status,
}: FiltersProps) {
  const activeFilters = [
    price_min && { label: "Min Price", value: formatPrice(price_min) },
    price_max && { label: "Max Price", value: formatPrice(price_max) },
    bedrooms && { label: "Bedrooms", value: bedrooms.toUpperCase() },
    location && { label: "Location", value: location },
    property_type && { label: "Type", value: capitalize(property_type) },
    status && { label: "Status", value: capitalize(status) },
  ].filter(Boolean);

  if (activeFilters.length === 0) {
    return null;
  }

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <svg
          className="w-5 h-5 text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
        <h3 className="text-sm font-semibold text-gray-700">Active Filters</h3>
      </div>

      <div className="flex flex-wrap gap-2">
        {activeFilters.map((filter, index) => (
          <div
            key={index}
            className="inline-flex items-center gap-2 bg-white border border-gray-300 rounded-full px-3 py-1.5"
          >
            <span className="text-xs font-medium text-gray-500">
              {filter!.label}:
            </span>
            <span className="text-sm font-semibold text-gray-900">
              {filter!.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "AED",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
