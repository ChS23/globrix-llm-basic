import React from "react";
import type { ComparisonTableProps } from "./types";

/**
 * Comparison table component for comparing multiple properties.
 */
export function ComparisonTable({ items, columns }: ComparisonTableProps) {
  if (!items || items.length === 0 || !columns || columns.length === 0) {
    return (
      <div className="card p-12 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[var(--background-elevated)] flex items-center justify-center mx-auto mb-4">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--foreground-subtle)]">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <line x1="3" y1="9" x2="21" y2="9"/>
            <line x1="9" y1="21" x2="9" y2="9"/>
          </svg>
        </div>
        <p className="text-[var(--foreground-muted)]">Нет данных для сравнения</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl text-[var(--foreground)]">Сравнение объектов</h2>
        <span className="badge badge-primary">{items.length} объектов</span>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-[var(--background-elevated)]">
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className="px-4 py-3 text-left text-xs font-semibold text-[var(--foreground-muted)] uppercase tracking-wider border-b border-[var(--border)]"
                  >
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((item, rowIndex) => (
                <tr
                  key={rowIndex}
                  className={`${
                    rowIndex % 2 === 0 ? "bg-[var(--background-card)]" : "bg-[var(--background-elevated)]/50"
                  } hover:bg-[var(--accent-glow)] transition-colors`}
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className="px-4 py-3 text-sm text-[var(--foreground)] border-b border-[var(--border)]"
                    >
                      {formatCellValue(item[column.key], column.type)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary */}
      <div className="flex flex-wrap gap-4 text-sm text-[var(--foreground-muted)]">
        <div className="flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--accent)]">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>Нажмите на строку для подробностей</span>
        </div>
      </div>
    </div>
  );
}

function formatCellValue(value: any, type: "text" | "number" | "currency"): string {
  if (value === null || value === undefined) {
    return "—";
  }

  switch (type) {
    case "number":
      return typeof value === "number"
        ? value.toLocaleString("ru-RU")
        : String(value);

    case "currency":
      if (typeof value === "number") {
        return new Intl.NumberFormat("ru-RU", {
          style: "currency",
          currency: "AED",
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(value);
      }
      return String(value);

    case "text":
    default:
      return String(value);
  }
}
