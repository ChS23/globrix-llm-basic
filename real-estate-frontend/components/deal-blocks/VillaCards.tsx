import React from "react";
import type { VillaCardsProps, Villa } from "./types";

/**
 * Premium villa cards component for the deal page.
 * Displays villa listings with plot area and amenities.
 */
export function VillaCards({ items }: VillaCardsProps) {
  if (!items || items.length === 0) {
    return (
      <div className="card p-12 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[var(--background-elevated)] flex items-center justify-center mx-auto mb-4">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--foreground-subtle)]">
            <path d="M3 21h18"/>
            <path d="M5 21V7l7-4 7 4v14"/>
            <path d="M9 21v-6h6v6"/>
          </svg>
        </div>
        <p className="text-[var(--foreground-muted)]">Виллы не найдены</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl text-[var(--foreground)]">Доступные виллы</h2>
          <p className="text-sm text-[var(--foreground-muted)] mt-1">Найдено: {items.length}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="badge badge-success">
            {items.filter(v => v.status === "available").length} доступно
          </span>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {items.map((villa, index) => (
          <VillaCard key={villa.id} villa={villa} index={index} />
        ))}
      </div>
    </div>
  );
}

function VillaCard({ villa, index }: { villa: Villa; index: number }) {
  const statusConfig = {
    available: { label: "Доступно", class: "badge-success" },
    reserved: { label: "Забронировано", class: "badge-warning" },
    sold: { label: "Продано", class: "badge-error" },
  };

  const status = statusConfig[villa.status || "available"] || statusConfig.available;
  const hasImage = villa.images && villa.images.length > 0;

  return (
    <div className={`card card-hover overflow-hidden animate-fade-in-up stagger-${Math.min(index + 1, 6)}`}>
      {hasImage ? (
        <div className="relative h-56 bg-[var(--background-elevated)]">
          <img
            src={villa.images![0]}
            alt={`Villa in ${villa.location}`}
            className="w-full h-full object-cover"
          />
          <div className="absolute top-3 right-3">
            <span className={`badge ${status.class}`}>{status.label}</span>
          </div>
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
            <p className="text-white font-medium">{villa.location}</p>
          </div>
        </div>
      ) : (
        <div className="p-5 border-b border-[var(--border)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--accent-dark)]/20 to-[var(--accent-light)]/10 border border-[var(--border-accent)] flex items-center justify-center">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--accent)]">
                  <path d="M3 21h18"/>
                  <path d="M5 21V7l7-4 7 4v14"/>
                </svg>
              </div>
              <div>
                <p className="font-medium text-[var(--foreground)]">{villa.location}</p>
                <p className="text-xs text-[var(--foreground-subtle)]">{villa.id}</p>
              </div>
            </div>
            <span className={`badge ${status.class}`}>{status.label}</span>
          </div>
        </div>
      )}

      <div className="p-5">
        {/* Price */}
        <div className="mb-4">
          <span className="text-2xl font-semibold text-[var(--foreground)]">
            {formatPrice(villa.price, villa.currency)}
          </span>
        </div>

        {/* Details */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <DetailItem
            icon={<BedroomIcon />}
            label="Спальни"
            value={villa.bedrooms.toString()}
          />
          {villa.bathrooms !== undefined && (
            <DetailItem
              icon={<BathroomIcon />}
              label="Ванные"
              value={villa.bathrooms.toString()}
            />
          )}
          <DetailItem
            icon={<AreaIcon />}
            label="Площадь"
            value={`${villa.area} м²`}
          />
          {villa.plot_area && (
            <DetailItem
              icon={<PlotIcon />}
              label="Участок"
              value={`${villa.plot_area} м²`}
            />
          )}
        </div>

        {/* Amenities */}
        {villa.amenities && villa.amenities.length > 0 && (
          <div className="pt-4 border-t border-[var(--border)] mb-4">
            <div className="flex flex-wrap gap-2">
              {villa.amenities.slice(0, 4).map((amenity, i) => (
                <span
                  key={i}
                  className="px-2 py-1 rounded-md bg-[var(--background-elevated)] text-xs text-[var(--foreground-muted)]"
                >
                  {amenity}
                </span>
              ))}
              {villa.amenities.length > 4 && (
                <span className="px-2 py-1 rounded-md bg-[var(--background-elevated)] text-xs text-[var(--foreground-muted)]">
                  +{villa.amenities.length - 4}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Action Button */}
        <button className="btn-primary w-full flex items-center justify-center gap-2">
          <span>Подробнее</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12,5 19,12 12,19"/>
          </svg>
        </button>
      </div>
    </div>
  );
}

function DetailItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg bg-[var(--background-elevated)]">
      <div className="text-[var(--accent)]">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="text-[10px] text-[var(--foreground-subtle)] uppercase tracking-wider">{label}</div>
        <div className="text-sm text-[var(--foreground)] font-medium truncate">{value}</div>
      </div>
    </div>
  );
}

// Icons
function AreaIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
    </svg>
  );
}

function PlotIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2L2 7l10 5 10-5-10-5z"/>
      <path d="M2 17l10 5 10-5"/>
      <path d="M2 12l10 5 10-5"/>
    </svg>
  );
}

function BedroomIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 7v11a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7"/>
      <path d="M21 7H3a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  );
}

function BathroomIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M9 6l6 6"/>
      <path d="M9 12l6-6"/>
    </svg>
  );
}

function formatPrice(price: number, currency: string = "AED"): string {
  if (currency === "THB") {
    return `฿${price.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
  }

  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  } catch {
    return `${currency} ${price.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
  }
}
