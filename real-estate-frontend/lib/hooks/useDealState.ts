"use client";

import { useState, useEffect, useCallback } from "react";
import type { DealState } from "@/components/deal-blocks/types";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface UseDealStateReturn {
  data: DealState | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

/**
 * Hook для получения и обновления состояния сделки.
 *
 * @param dealId - UUID сделки
 * @param autoRefetch - Автоматическое обновление (polling)
 * @param refetchInterval - Интервал автообновления в мс
 */
export function useDealState(
  dealId: string,
  autoRefetch = false,
  refetchInterval = 5000
): UseDealStateReturn {
  const [data, setData] = useState<DealState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchDealState = useCallback(async () => {
    try {
      setError(null);

      const response = await fetch(`${BACKEND_URL}/api/deal/${dealId}/state`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const dealState = await response.json();
      setData(dealState);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);
      console.error("Failed to fetch deal state:", error);
    } finally {
      setIsLoading(false);
    }
  }, [dealId]);

  // Initial fetch
  useEffect(() => {
    fetchDealState();
  }, [fetchDealState]);

  // Auto-refetch (polling)
  useEffect(() => {
    if (!autoRefetch) return;

    const interval = setInterval(() => {
      fetchDealState();
    }, refetchInterval);

    return () => clearInterval(interval);
  }, [autoRefetch, refetchInterval, fetchDealState]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchDealState,
  };
}
