"use client";

import React, { use, useState, useEffect } from "react";
import Link from "next/link";
import { DealRenderer } from "@/lib/deal-renderer";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { useDealState } from "@/lib/hooks/useDealState";

interface DealPageProps {
  params: Promise<{ id: string }>;
}

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  return isMobile;
}

export default function DealPage({ params }: DealPageProps) {
  const { id } = use(params);
  const { data, isLoading, error, refetch } = useDealState(id);
  const [isChatOpen, setIsChatOpen] = useState(true);
  const isMobile = useIsMobile();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full border-2 border-[var(--border)]" />
            <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-[var(--accent)] animate-spin" />
          </div>
          <p className="text-[var(--foreground-muted)]">Загрузка сделки...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="card max-w-md w-full p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-[var(--error-muted)] flex items-center justify-center mx-auto mb-6">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--error)]">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <h2 className="text-2xl mb-3 text-[var(--foreground)]">Ошибка загрузки</h2>
          <p className="text-[var(--foreground-muted)] mb-6">{error.message}</p>
          <button onClick={() => refetch()} className="btn-primary">
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 glass z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[var(--accent-dark)] to-[var(--accent-light)] flex items-center justify-center group-hover:scale-105 transition-transform">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-[var(--background)]">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9,22 9,12 15,12 15,22"/>
              </svg>
            </div>
            <span className="text-lg font-semibold tracking-tight">Globrix</span>
          </Link>

          <div className="h-6 w-px bg-[var(--border)]" />

          <div className="flex items-center gap-3">
            <span className="text-sm text-[var(--foreground-muted)]">Сделка</span>
            <code className="px-3 py-1.5 rounded-lg bg-[var(--background-card)] border border-[var(--border)] text-xs font-mono text-[var(--foreground-muted)]">
              {id.slice(0, 8)}...
            </code>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            className="btn-ghost flex items-center gap-2 px-4 py-2"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23,4 23,10 17,10"/>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            <span className="text-sm">Обновить</span>
          </button>

          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className={`btn-secondary flex items-center gap-2 px-4 py-2 ${isChatOpen ? "bg-[var(--accent-glow)] border-[var(--border-accent)]" : ""}`}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span className="text-sm">Чат</span>
          </button>
        </div>
      </header>

      {/* Main Layout - fills remaining height */}
      <div className="flex-1 flex min-h-0">
        {/* Content Area - scrolls independently */}
        <main className="flex-1 overflow-y-auto">
          {data && data.blocks && data.blocks.length > 0 ? (
            <div className="p-6 animate-fade-in">
              <DealRenderer blocks={data.blocks} />
            </div>
          ) : (
            <EmptyState />
          )}
        </main>

        {/* Chat Sidebar - fixed height, scrolls independently */}
        <aside
          className={`flex-shrink-0 transition-all duration-300 ease-out ${
            isChatOpen ? "w-[420px]" : "w-0"
          } overflow-hidden`}
        >
          <div className="h-full">
            <ChatPanel dealId={id} onUpdate={() => refetch()} />
          </div>
        </aside>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="h-full flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="relative w-24 h-24 mx-auto mb-8">
          {/* Animated rings */}
          <div className="absolute inset-0 rounded-full border border-[var(--border)] animate-ping opacity-20" />
          <div className="absolute inset-2 rounded-full border border-[var(--border)] animate-ping opacity-30" style={{ animationDelay: "0.5s" }} />
          <div className="absolute inset-4 rounded-full bg-[var(--background-card)] border border-[var(--border)] flex items-center justify-center">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--accent)]">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
        </div>

        <h2 className="text-2xl mb-3 text-[var(--foreground)]">Начните сделку</h2>
        <p className="text-[var(--foreground-muted)] leading-relaxed mb-8">
          Используйте чат для поиска объектов, задавайте вопросы о недвижимости
          и ведите сделку шаг за шагом.
        </p>

        <div className="space-y-3">
          <SuggestionPill>Найди двушки в Дубай Марина</SuggestionPill>
          <SuggestionPill>Покажи пентхаусы до 5М AED</SuggestionPill>
          <SuggestionPill>Какие налоги в Таиланде?</SuggestionPill>
        </div>
      </div>
    </div>
  );
}

function SuggestionPill({ children }: { children: React.ReactNode }) {
  return (
    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--background-card)] border border-[var(--border)] text-sm text-[var(--foreground-muted)] hover:border-[var(--border-accent)] hover:text-[var(--foreground)] transition-all cursor-pointer mr-2 mb-2">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--accent)]">
        <polyline points="9,18 15,12 9,6"/>
      </svg>
      {children}
    </div>
  );
}
