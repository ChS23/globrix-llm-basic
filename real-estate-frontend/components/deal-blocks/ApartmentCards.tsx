import React from "react";
import type { ApartmentCardsProps, Apartment } from "./types";

/**
 * Компонент для отображения карточек апартаментов.
 * Используется GenUI Agent для динамического добавления на страницу сделки.
 */
export function ApartmentCards({ items }: ApartmentCardsProps) {
  if (!items || items.length === 0) {
    return (
      <div className="p-4 text-gray-500 text-center">
        No apartments found
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
      {items.map((apartment) => (
        <ApartmentCard key={apartment.id} apartment={apartment} />
      ))}
    </div>
  );
}

function ApartmentCard({ apartment }: { apartment: Apartment }) {
  const statusColors = {
    available: "bg-green-100 text-green-800",
    reserved: "bg-yellow-100 text-yellow-800",
    sold: "bg-red-100 text-red-800",
  };

  return (
    <div className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      {/* Image */}
      {apartment.images && apartment.images.length > 0 ? (
        <img
          src={apartment.images[0]}
          alt={`${apartment.type} apartment`}
          className="w-full h-48 object-cover"
        />
      ) : (
        <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
          <span className="text-gray-400">No Image</span>
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        {/* Type & Status */}
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold uppercase">{apartment.type}</h3>
          <span
            className={`px-2 py-1 rounded text-xs font-medium ${
              statusColors[apartment.status]
            }`}
          >
            {apartment.status}
          </span>
        </div>

        {/* Area */}
        <div className="text-sm text-gray-600 mb-2">
          {apartment.area} sq.m
          {apartment.floor && ` • Floor ${apartment.floor}`}
        </div>

        {/* Price */}
        <div className="text-xl font-bold text-gray-900 mb-2">
          {formatPrice(apartment.price, apartment.currency)}
        </div>

        {/* Additional Info */}
        {apartment.developer && (
          <div className="text-sm text-gray-500 mb-1">
            Developer: {apartment.developer}
          </div>
        )}

        {apartment.completion_date && (
          <div className="text-sm text-gray-500">
            Completion: {apartment.completion_date}
          </div>
        )}

        {/* Action Button */}
        <button className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors">
          View Details
        </button>
      </div>
    </div>
  );
}

function formatPrice(price: number, currency: string = "AED"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
}
