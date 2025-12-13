import React from "react";
import type { MapProps } from "./types";

/**
 * Map component for displaying property locations.
 * Uses a static map placeholder since interactive maps require API keys.
 */
export function MapBlock({ center, markers, zoom = 13 }: MapProps) {
  if (!markers || markers.length === 0) {
    return (
      <div className="card p-12 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[var(--background-elevated)] flex items-center justify-center mx-auto mb-4">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--foreground-subtle)]">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
        </div>
        <p className="text-[var(--foreground-muted)]">Нет объектов для отображения на карте</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl text-[var(--foreground)]">Расположение</h2>
        <span className="badge badge-primary">{markers.length} объектов</span>
      </div>

      {/* Map Container */}
      <div className="card overflow-hidden">
        {/* Map Placeholder - styled to look like a map */}
        <div className="relative h-80 bg-[var(--background-elevated)] overflow-hidden">
          {/* Grid pattern to simulate map */}
          <div
            className="absolute inset-0 opacity-10"
            style={{
              backgroundImage: `
                linear-gradient(rgba(212, 168, 83, 0.3) 1px, transparent 1px),
                linear-gradient(90deg, rgba(212, 168, 83, 0.3) 1px, transparent 1px)
              `,
              backgroundSize: "40px 40px",
            }}
          />

          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-[var(--accent-dark)]/5 to-[var(--accent-light)]/10" />

          {/* Center indicator */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="relative">
              <div className="absolute -inset-8 rounded-full bg-[var(--accent)]/10 animate-ping" />
              <div className="absolute -inset-4 rounded-full bg-[var(--accent)]/20" />
              <div className="w-4 h-4 rounded-full bg-[var(--accent)] shadow-lg" />
            </div>
          </div>

          {/* Coordinates display */}
          <div className="absolute bottom-4 left-4 px-3 py-2 rounded-lg bg-[var(--background)]/80 backdrop-blur-sm border border-[var(--border)]">
            <p className="text-xs font-mono text-[var(--foreground-muted)]">
              {center.lat.toFixed(4)}°, {center.lng.toFixed(4)}°
            </p>
          </div>

          {/* Zoom indicator */}
          <div className="absolute bottom-4 right-4 px-3 py-2 rounded-lg bg-[var(--background)]/80 backdrop-blur-sm border border-[var(--border)]">
            <p className="text-xs text-[var(--foreground-muted)]">Zoom: {zoom}x</p>
          </div>

          {/* Map unavailable notice */}
          <div className="absolute top-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-lg bg-[var(--background)]/90 backdrop-blur-sm border border-[var(--border)]">
            <p className="text-sm text-[var(--foreground-muted)]">
              Интерактивная карта скоро будет доступна
            </p>
          </div>
        </div>

        {/* Markers List */}
        <div className="p-4 border-t border-[var(--border)]">
          <h3 className="text-sm font-semibold text-[var(--foreground-muted)] mb-3">Объекты на карте</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {markers.map((marker, index) => (
              <div
                key={marker.id}
                className="flex items-center justify-between p-3 rounded-lg bg-[var(--background-elevated)] hover:bg-[var(--accent-glow)] transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center text-[var(--background)] text-xs font-bold">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--foreground)]">{marker.title}</p>
                    <p className="text-xs text-[var(--foreground-subtle)]">
                      {marker.lat.toFixed(4)}°, {marker.lng.toFixed(4)}°
                    </p>
                  </div>
                </div>
                {marker.price && (
                  <span className="text-sm font-semibold text-[var(--accent)]">
                    {formatPrice(marker.price)}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function formatPrice(price: number): string {
  if (price >= 1000000) {
    return `${(price / 1000000).toFixed(1)}M`;
  }
  if (price >= 1000) {
    return `${(price / 1000).toFixed(0)}K`;
  }
  return price.toString();
}
