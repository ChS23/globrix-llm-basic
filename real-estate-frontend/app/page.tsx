"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();
  const [dealId, setDealId] = useState("");
  const [isHovering, setIsHovering] = useState<string | null>(null);

  const handleCreateDeal = () => {
    const newDealId = crypto.randomUUID();
    router.push(`/deal/${newDealId}`);
  };

  const handleOpenDeal = () => {
    if (dealId.trim()) {
      router.push(`/deal/${dealId.trim()}`);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Ambient Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Gradient orbs */}
        <div
          className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full animate-float"
          style={{
            background: "radial-gradient(circle, rgba(212, 168, 83, 0.08) 0%, transparent 70%)",
            filter: "blur(60px)",
          }}
        />
        <div
          className="absolute bottom-[-30%] left-[-15%] w-[800px] h-[800px] rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(212, 168, 83, 0.05) 0%, transparent 70%)",
            filter: "blur(80px)",
            animationDelay: "3s",
          }}
        />
        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(212, 168, 83, 0.3) 1px, transparent 1px),
              linear-gradient(90deg, rgba(212, 168, 83, 0.3) 1px, transparent 1px)
            `,
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Navigation */}
        <nav className="px-8 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent-dark)] to-[var(--accent-light)] flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-[var(--background)]">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9,22 9,12 15,12 15,22"/>
              </svg>
            </div>
            <span className="text-xl font-semibold tracking-tight">Globrix</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-[var(--foreground-muted)]">На базе ИИ</span>
          </div>
        </nav>

        {/* Hero Section */}
        <main className="flex-1 flex items-center justify-center px-6 py-12">
          <div className="max-w-5xl w-full">
            {/* Hero Text */}
            <div className="text-center mb-16 animate-fade-in-up">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--background-card)] border border-[var(--border)] mb-8">
                <span className="w-2 h-2 rounded-full bg-[var(--success)] animate-pulse" />
                <span className="text-sm text-[var(--foreground-muted)]">Платформа для работы с недвижимостью</span>
              </div>

              <h1 className="text-6xl md:text-7xl lg:text-8xl mb-6 leading-[0.95]">
                <span className="block text-[var(--foreground)]">Управляйте</span>
                <span className="block gradient-text">Сделками Легко</span>
              </h1>

              <p className="text-xl text-[var(--foreground-muted)] max-w-2xl mx-auto leading-relaxed">
                Трансформируйте работу с недвижимостью с помощью ИИ.
                Ищите объекты, анализируйте инвестиции и закрывайте сделки быстрее.
              </p>
            </div>

            {/* Action Cards */}
            <div className="grid md:grid-cols-2 gap-6 mb-16">
              {/* Create New Deal */}
              <div
                className="card card-hover p-8 animate-fade-in-up stagger-2"
                onMouseEnter={() => setIsHovering("create")}
                onMouseLeave={() => setIsHovering(null)}
              >
                <div className="flex items-start justify-between mb-6">
                  <div
                    className="w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300"
                    style={{
                      background: isHovering === "create"
                        ? "var(--gradient-gold)"
                        : "var(--background-elevated)",
                      boxShadow: isHovering === "create"
                        ? "0 8px 30px rgba(212, 168, 83, 0.3)"
                        : "none",
                    }}
                  >
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      className={`transition-colors duration-300 ${isHovering === "create" ? "text-[var(--background)]" : "text-[var(--accent)]"}`}
                    >
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                  </div>
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    className={`text-[var(--foreground-subtle)] transition-all duration-300 ${isHovering === "create" ? "translate-x-1 text-[var(--accent)]" : ""}`}
                  >
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <polyline points="12,5 19,12 12,19"/>
                  </svg>
                </div>

                <h2 className="text-2xl mb-3 text-[var(--foreground)]">Создать сделку</h2>
                <p className="text-[var(--foreground-muted)] mb-8 leading-relaxed">
                  Начните новую сделку с помощью ИИ-ассистента. Ищите объекты,
                  сравнивайте варианты и формируйте портфель.
                </p>

                <button
                  onClick={handleCreateDeal}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  <span>Начать сделку</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <polyline points="12,5 19,12 12,19"/>
                  </svg>
                </button>
              </div>

              {/* Open Existing Deal */}
              <div
                className="card card-hover p-8 animate-fade-in-up stagger-3"
                onMouseEnter={() => setIsHovering("open")}
                onMouseLeave={() => setIsHovering(null)}
              >
                <div className="flex items-start justify-between mb-6">
                  <div
                    className="w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300"
                    style={{
                      background: isHovering === "open"
                        ? "var(--gradient-gold)"
                        : "var(--background-elevated)",
                      boxShadow: isHovering === "open"
                        ? "0 8px 30px rgba(212, 168, 83, 0.3)"
                        : "none",
                    }}
                  >
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      className={`transition-colors duration-300 ${isHovering === "open" ? "text-[var(--background)]" : "text-[var(--accent)]"}`}
                    >
                      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                  </div>
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    className={`text-[var(--foreground-subtle)] transition-all duration-300 ${isHovering === "open" ? "translate-x-1 text-[var(--accent)]" : ""}`}
                  >
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <polyline points="12,5 19,12 12,19"/>
                  </svg>
                </div>

                <h2 className="text-2xl mb-3 text-[var(--foreground)]">Открыть сделку</h2>
                <p className="text-[var(--foreground-muted)] mb-6 leading-relaxed">
                  Продолжите работу над существующей сделкой.
                  Введите ID сделки, чтобы вернуться к работе.
                </p>

                <div className="space-y-3">
                  <input
                    type="text"
                    value={dealId}
                    onChange={(e) => setDealId(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleOpenDeal()}
                    placeholder="Введите ID сделки..."
                    className="input font-mono text-sm"
                  />
                  <button
                    onClick={handleOpenDeal}
                    disabled={!dealId.trim()}
                    className="btn-secondary w-full disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    Открыть
                  </button>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fade-in-up stagger-4">
              {features.map((feature, index) => (
                <FeatureCard key={index} {...feature} index={index} />
              ))}
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="px-8 py-6 flex items-center justify-between border-t border-[var(--border)]">
          <div className="flex items-center gap-6">
            <span className="text-sm text-[var(--foreground-subtle)]">
              Работает на Claude & LangGraph
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-[var(--foreground-subtle)] font-mono">v1.0.0</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

const features = [
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    ),
    title: "ИИ-Ассистент",
    description: "Общайтесь на естественном языке для поиска и управления сделками",
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
        <line x1="3" y1="9" x2="21" y2="9"/>
        <line x1="9" y1="21" x2="9" y2="9"/>
      </svg>
    ),
    title: "Динамический UI",
    description: "Интерфейс адаптируется под ваш разговор с ассистентом",
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <line x1="18" y1="20" x2="18" y2="10"/>
        <line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/>
      </svg>
    ),
    title: "Умная Аналитика",
    description: "Автоматические инсайты и рекомендации по сделкам",
  },
];

function FeatureCard({
  icon,
  title,
  description,
  index
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  index: number;
}) {
  return (
    <div
      className={`group p-5 rounded-2xl bg-[var(--background-card)]/50 border border-[var(--border)]
        hover:border-[var(--border-accent)] hover:bg-[var(--background-card)]
        transition-all duration-300 stagger-${index + 4}`}
    >
      <div className="flex items-center gap-3 mb-3">
        <div className="text-[var(--accent)] group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>
        <h3 className="font-semibold text-[var(--foreground)]">{title}</h3>
      </div>
      <p className="text-sm text-[var(--foreground-muted)] leading-relaxed">{description}</p>
    </div>
  );
}
