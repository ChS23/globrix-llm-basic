import React from "react";
import type { ApartmentCardsProps, Apartment } from "./types";

/**
 * Premium apartment cards component for the deal page.
 * Displays property listings with a luxury editorial aesthetic.
 */
export function ApartmentCards({ items }: ApartmentCardsProps) {
  if (!items || items.length === 0) {
    return (
      <div className="card p-12 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[var(--background-elevated)] flex items-center justify-center mx-auto mb-4">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--foreground-subtle)]">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9,22 9,12 15,12 15,22"/>
          </svg>
        </div>
        <p className="text-[var(--foreground-muted)]">Апартаменты не найдены</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl text-[var(--foreground)]">Доступные объекты</h2>
          <p className="text-sm text-[var(--foreground-muted)] mt-1">Найдено: {items.length}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="badge badge-success">{items.filter(a => a.status === "available").length} доступно</span>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {items.map((apartment, index) => (
          <ApartmentCard key={apartment.id} apartment={apartment} index={index} />
        ))}
      </div>
    </div>
  );
}

function ApartmentCard({ apartment, index }: { apartment: Apartment; index: number }) {
  const statusConfig = {
    available: { label: "Доступно", class: "badge-success" },
    reserved: { label: "Забронировано", class: "badge-warning" },
    sold: { label: "Продано", class: "badge-error" },
  };

  const status = statusConfig[apartment.status] || statusConfig.available;
  const hasImage = apartment.images && apartment.images.length > 0;

  // Compact card variant for apartments without photos
  if (!hasImage) {
    return (
      <div
        className={`card card-hover overflow-hidden animate-fade-in-up stagger-${Math.min(index + 1, 6)}`}
      >
        <div className="p-5">
          {/* Header row: Type, ID, Status */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--accent-dark)]/20 to-[var(--accent-light)]/10 border border-[var(--border-accent)] flex items-center justify-center">
                <span className="text-sm font-bold text-[var(--accent)] uppercase">{apartment.type}</span>
              </div>
              <div>
                <span className="text-sm font-mono text-[var(--foreground-muted)]">{apartment.id}</span>
                {apartment.floor && (
                  <p className="text-xs text-[var(--foreground-subtle)]">Этаж {apartment.floor}</p>
                )}
              </div>
            </div>
            <span className={`badge ${status.class}`}>{status.label}</span>
          </div>

          {/* Price - prominent */}
          <div className="mb-4 pb-4 border-b border-[var(--border)]">
            <span className="text-2xl font-semibold text-[var(--foreground)]">
              {formatPrice(apartment.price, apartment.currency)}
            </span>
          </div>

          {/* Details row - horizontal */}
          <div className="flex flex-wrap gap-4 mb-4">
            <div className="flex items-center gap-2">
              <AreaIcon />
              <span className="text-sm text-[var(--foreground)]">{apartment.area} м²</span>
            </div>
            {apartment.bedrooms !== undefined && (
              <div className="flex items-center gap-2">
                <BedroomIcon />
                <span className="text-sm text-[var(--foreground)]">{apartment.bedrooms} спальн.</span>
              </div>
            )}
            {apartment.bathrooms !== undefined && (
              <div className="flex items-center gap-2">
                <BathroomIcon />
                <span className="text-sm text-[var(--foreground)]">{apartment.bathrooms} ванн.</span>
              </div>
            )}
          </div>

          {/* Developer & Completion - inline */}
          {(apartment.developer || apartment.completion_date) && (
            <div className="flex flex-wrap gap-4 text-sm text-[var(--foreground-muted)] mb-4">
              {apartment.developer && (
                <div className="flex items-center gap-1.5">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--foreground-subtle)]">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="9" y1="3" x2="9" y2="21"/>
                  </svg>
                  <span>{apartment.developer}</span>
                </div>
              )}
              {apartment.completion_date && (
                <div className="flex items-center gap-1.5">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--foreground-subtle)]">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  <span>{apartment.completion_date}</span>
                </div>
              )}
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

  // Full card variant with image
  return (
    <div
      className={`card card-hover overflow-hidden animate-fade-in-up stagger-${Math.min(index + 1, 6)}`}
    >
      {/* Image */}
      <div className="relative h-48 bg-[var(--background-elevated)]">
        <img
          src={apartment.images![0]}
          alt={`${apartment.type} apartment`}
          className="w-full h-full object-cover"
        />

        {/* Status Badge */}
        <div className="absolute top-3 right-3">
          <span className={`badge ${status.class}`}>{status.label}</span>
        </div>

        {/* Type Badge */}
        <div className="absolute top-3 left-3">
          <span className="px-3 py-1.5 rounded-lg bg-[var(--background)]/80 backdrop-blur-sm text-xs font-semibold text-[var(--foreground)] uppercase tracking-wide">
            {apartment.type}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        {/* ID & Floor */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-mono text-[var(--accent)]">{apartment.id}</span>
          {apartment.floor && (
            <span className="text-xs text-[var(--foreground-subtle)]">Этаж {apartment.floor}</span>
          )}
        </div>

        {/* Price */}
        <div className="mb-4">
          <span className="text-2xl font-semibold text-[var(--foreground)]">
            {formatPrice(apartment.price, apartment.currency)}
          </span>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <DetailItem icon={<AreaIcon />} label="Площадь" value={`${apartment.area} м²`} />
          {apartment.bedrooms !== undefined && (
            <DetailItem icon={<BedroomIcon />} label="Спальни" value={apartment.bedrooms.toString()} />
          )}
          {apartment.bathrooms !== undefined && (
            <DetailItem icon={<BathroomIcon />} label="Ванные" value={apartment.bathrooms.toString()} />
          )}
          {apartment.currency && (
            <DetailItem icon={<CurrencyIcon />} label="Валюта" value={apartment.currency} />
          )}
        </div>

        {/* Developer & Completion */}
        {(apartment.developer || apartment.completion_date) && (
          <div className="pt-4 border-t border-[var(--border)] space-y-2">
            {apartment.developer && (
              <div className="flex items-center gap-2 text-sm">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--foreground-subtle)]">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="9" y1="3" x2="9" y2="21"/>
                </svg>
                <span className="text-[var(--foreground-muted)]">{apartment.developer}</span>
              </div>
            )}
            {apartment.completion_date && (
              <div className="flex items-center gap-2 text-sm">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--foreground-subtle)]">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                <span className="text-[var(--foreground-muted)]">{apartment.completion_date}</span>
              </div>
            )}
          </div>
        )}

        {/* Action Button */}
        <button className="btn-primary w-full mt-5 flex items-center justify-center gap-2">
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

function CurrencyIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="12" y1="1" x2="12" y2="23"/>
      <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
    </svg>
  );
}

function formatPrice(price: number, currency: string = "AED"): string {
  // Handle THB (Thai Baht) separately since Intl might not support it well
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
