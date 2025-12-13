import React from "react";
import type { AmenitiesListProps } from "./types";

// Icon mapping for common amenities
const amenityIcons: Record<string, React.ReactNode> = {
  // Fitness & Recreation
  "gym": <GymIcon />,
  "pool": <PoolIcon />,
  "spa": <SpaIcon />,
  "sauna": <SaunaIcon />,
  "tennis": <TennisIcon />,
  "yoga": <YogaIcon />,

  // Building Features
  "parking": <ParkingIcon />,
  "security": <SecurityIcon />,
  "concierge": <ConciergeIcon />,
  "elevator": <ElevatorIcon />,

  // Outdoor
  "garden": <GardenIcon />,
  "bbq": <BbqIcon />,
  "playground": <PlaygroundIcon />,
  "beach": <BeachIcon />,

  // Services
  "restaurant": <RestaurantIcon />,
  "cafe": <CafeIcon />,
  "shops": <ShopsIcon />,

  // Technology
  "smart_home": <SmartHomeIcon />,
  "wifi": <WifiIcon />,
};

/**
 * Amenities list component for displaying project/property features.
 */
export function AmenitiesList({ title, items, categories }: AmenitiesListProps) {
  if ((!items || items.length === 0) && (!categories || categories.length === 0)) {
    return (
      <div className="card p-12 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[var(--background-elevated)] flex items-center justify-center mx-auto mb-4">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--foreground-subtle)]">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22,4 12,14.01 9,11.01"/>
          </svg>
        </div>
        <p className="text-[var(--foreground-muted)]">Удобства не указаны</p>
      </div>
    );
  }

  // If categories provided, render grouped
  if (categories && categories.length > 0) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl text-[var(--foreground)]">{title || "Удобства и сервисы"}</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {categories.map((category, index) => (
            <div key={index} className="card p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-[var(--accent-glow)] flex items-center justify-center">
                  {getCategoryIcon(category.name)}
                </div>
                <h3 className="text-lg font-semibold text-[var(--foreground)]">{category.name}</h3>
              </div>

              <div className="space-y-2">
                {category.items.map((item, i) => (
                  <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-[var(--background-elevated)] transition-colors">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--success)]">
                      <polyline points="20,6 9,17 4,12"/>
                    </svg>
                    <span className="text-sm text-[var(--foreground)]">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Simple list rendering
  return (
    <div className="space-y-6">
      <h2 className="text-2xl text-[var(--foreground)]">{title || "Удобства и сервисы"}</h2>

      <div className="card p-5">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {items!.map((item, index) => (
            <AmenityItem key={index} name={item} />
          ))}
        </div>
      </div>
    </div>
  );
}

function AmenityItem({ name }: { name: string }) {
  const iconKey = name.toLowerCase().replace(/\s+/g, "_");
  const icon = amenityIcons[iconKey] || <DefaultIcon />;

  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-[var(--background-elevated)] hover:bg-[var(--accent-glow)] transition-colors">
      <div className="w-10 h-10 rounded-lg bg-[var(--background-card)] border border-[var(--border)] flex items-center justify-center text-[var(--accent)]">
        {icon}
      </div>
      <span className="text-sm text-[var(--foreground)] font-medium">{name}</span>
    </div>
  );
}

function getCategoryIcon(category: string): React.ReactNode {
  const lower = category.toLowerCase();
  if (lower.includes("фитнес") || lower.includes("спорт")) return <GymIcon />;
  if (lower.includes("отдых") || lower.includes("релакс")) return <SpaIcon />;
  if (lower.includes("безопас")) return <SecurityIcon />;
  if (lower.includes("дет")) return <PlaygroundIcon />;
  if (lower.includes("еда") || lower.includes("ресторан")) return <RestaurantIcon />;
  return <DefaultIcon />;
}

// Icons
function DefaultIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
      <polyline points="22,4 12,14.01 9,11.01"/>
    </svg>
  );
}

function GymIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M6.5 6.5h11v11h-11z"/>
      <path d="M2 12h4M18 12h4"/>
    </svg>
  );
}

function PoolIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M2 12h20M2 16h20M2 20h20"/>
    </svg>
  );
}

function SpaIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2c.5 5-3 7.5-3 12a6 6 0 1 0 12 0c0-4.5-3.5-7-3-12"/>
    </svg>
  );
}

function SaunaIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 3v18M8 8c0-2 1.5-3 4-3s4 1 4 3M8 13c0-2 1.5-3 4-3s4 1 4 3"/>
    </svg>
  );
}

function TennisIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10"/>
      <path d="M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/>
    </svg>
  );
}

function YogaIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="5" r="2"/>
      <path d="M12 7v5l-4 4M12 12l4 4"/>
    </svg>
  );
}

function ParkingIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="2"/>
      <path d="M9 17V7h4a3 3 0 1 1 0 6H9"/>
    </svg>
  );
}

function SecurityIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
  );
}

function ConciergeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>
      <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
    </svg>
  );
}

function ElevatorIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="2"/>
      <path d="M12 8v8M9 11l3-3 3 3"/>
    </svg>
  );
}

function GardenIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 22V8"/>
      <path d="M5 12c0-4.4 3.1-8 7-8 3.9 0 7 3.6 7 8"/>
      <path d="M5 12H3"/>
      <path d="M21 12h-2"/>
    </svg>
  );
}

function BbqIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 14h18M5 14v6M19 14v6M12 2v3M6 5l2 2M18 5l-2 2"/>
      <ellipse cx="12" cy="11" rx="9" ry="4"/>
    </svg>
  );
}

function PlaygroundIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="5" r="3"/>
      <path d="M12 8v8M8 12h8"/>
    </svg>
  );
}

function BeachIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="8" r="5"/>
      <path d="M3 21h18"/>
      <path d="M12 13v5"/>
    </svg>
  );
}

function RestaurantIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/>
      <path d="M7 2v20"/>
      <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/>
    </svg>
  );
}

function CafeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17 8h1a4 4 0 1 1 0 8h-1"/>
      <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/>
      <line x1="6" y1="2" x2="6" y2="4"/>
      <line x1="10" y1="2" x2="10" y2="4"/>
      <line x1="14" y1="2" x2="14" y2="4"/>
    </svg>
  );
}

function ShopsIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
      <line x1="3" y1="6" x2="21" y2="6"/>
      <path d="M16 10a4 4 0 0 1-8 0"/>
    </svg>
  );
}

function SmartHomeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <path d="M9 12h6M12 9v6"/>
    </svg>
  );
}

function WifiIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M5 12.55a11 11 0 0 1 14.08 0"/>
      <path d="M1.42 9a16 16 0 0 1 21.16 0"/>
      <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
      <line x1="12" y1="20" x2="12.01" y2="20"/>
    </svg>
  );
}
