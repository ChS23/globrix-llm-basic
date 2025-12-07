import React from "react";
import type { SummaryProps } from "./types";

/**
 * Компонент для отображения итоговой информации по результатам поиска.
 * Показывает количество найденных объектов, среднюю цену и другую статистику.
 */
export function Summary({
  total_found,
  average_price,
  message,
  stats,
}: SummaryProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
      {/* Main Message */}
      <div className="flex items-start gap-3 mb-4">
        <div className="flex-shrink-0">
          <svg
            className="w-6 h-6 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            Search Results
          </h3>
          <p className="text-gray-700">{message}</p>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total Found */}
        <StatCard
          label="Properties Found"
          value={total_found.toString()}
          icon="🏢"
        />

        {/* Average Price */}
        {average_price && (
          <StatCard
            label="Average Price"
            value={formatPrice(average_price)}
            icon="💰"
          />
        )}

        {/* Min Price */}
        {stats?.min_price && (
          <StatCard
            label="Min Price"
            value={formatPrice(stats.min_price)}
            icon="📉"
          />
        )}

        {/* Max Price */}
        {stats?.max_price && (
          <StatCard
            label="Max Price"
            value={formatPrice(stats.max_price)}
            icon="📈"
          />
        )}

        {/* Average Area */}
        {stats?.avg_area && (
          <StatCard
            label="Avg Area"
            value={`${stats.avg_area.toFixed(0)} sq.m`}
            icon="📏"
          />
        )}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: string;
}) {
  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200">
      <div className="text-2xl mb-2">{icon}</div>
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-lg font-bold text-gray-900">{value}</div>
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
