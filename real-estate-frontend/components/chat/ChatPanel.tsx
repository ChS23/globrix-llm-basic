"use client";

import React, { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatPanelProps {
  dealId: string;
  onUpdate?: () => void;
}

export function ChatPanel({ dealId, onUpdate }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: textToSend,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: dealId,
          deal_id: dealId,
          message: textToSend,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Trigger page update if UI was modified
      if (onUpdate) {
        setTimeout(() => onUpdate(), 500);
      }
    } catch (error) {
      console.error("Chat error:", error);

      const errorMessage: Message = {
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Failed to send message"}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-[var(--background-elevated)] border-l border-[var(--border)] safe-area-inset-top">
      {/* Header */}
      <div className="flex-shrink-0 p-4 md:p-5 border-b border-[var(--border)] pt-14 md:pt-5">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-9 h-9 md:w-10 md:h-10 rounded-xl bg-gradient-to-br from-[var(--accent-dark)] to-[var(--accent-light)] flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--background)] md:w-[18px] md:h-[18px]">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-[var(--success)] border-2 border-[var(--background-elevated)]" />
          </div>
          <div>
            <h2 className="text-sm md:text-base font-semibold text-[var(--foreground)]">ИИ-Ассистент</h2>
            <p className="text-xs text-[var(--foreground-subtle)]">Онлайн</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && <WelcomeMessage onSend={(text) => handleSend(text)} />}

        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 p-3 md:p-4 border-t border-[var(--border)] safe-area-inset-bottom">
        <div className="relative">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Спросите что угодно..."
            className="w-full resize-none rounded-xl bg-[var(--background-card)] border border-[var(--border)] px-3 md:px-4 py-2.5 md:py-3 pr-11 md:pr-12 text-sm md:text-base text-[var(--foreground)] placeholder:text-[var(--foreground-subtle)] focus:outline-none focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent-glow)] transition-all"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="absolute right-2.5 md:right-3 bottom-2.5 md:bottom-3 w-7 h-7 md:w-8 md:h-8 rounded-lg bg-[var(--accent)] text-[var(--background)] flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:bg-[var(--accent-light)] active:scale-95 transition-all"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="md:w-4 md:h-4">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22,2 15,22 11,13 2,9 22,2"/>
            </svg>
          </button>
        </div>
        <p className="hidden md:block mt-2 text-xs text-[var(--foreground-subtle)] text-center">
          Enter — отправить, Shift + Enter — новая строка
        </p>
      </div>
    </div>
  );
}

function WelcomeMessage({ onSend }: { onSend: (text: string) => void }) {
  return (
    <div className="py-6 md:py-8 text-center">
      <div className="w-14 h-14 md:w-16 md:h-16 rounded-2xl bg-[var(--background-card)] border border-[var(--border)] flex items-center justify-center mx-auto mb-3 md:mb-4">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--accent)] md:w-7 md:h-7">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </div>
      <h3 className="text-base md:text-lg mb-2 text-[var(--foreground)]">Начните диалог</h3>
      <p className="text-xs md:text-sm text-[var(--foreground-muted)] mb-4 md:mb-6 leading-relaxed max-w-[260px] md:max-w-[280px] mx-auto">
        Я помогу найти объекты, отвечу на вопросы о недвижимости и помогу вести сделки.
      </p>
      <div className="space-y-2">
        <QuickAction onSend={onSend}>Найди доступные двушки</QuickAction>
        <QuickAction onSend={onSend}>Покажи пентхаусы до 5М</QuickAction>
        <QuickAction onSend={onSend}>Какие правила налогов?</QuickAction>
      </div>
    </div>
  );
}

function QuickAction({ children, onSend }: { children: React.ReactNode; onSend: (text: string) => void }) {
  const handleClick = () => {
    if (typeof children === "string") {
      onSend(children);
    }
  };

  return (
    <button
      onClick={handleClick}
      className="w-full px-3 md:px-4 py-2 md:py-2.5 rounded-xl bg-[var(--background-card)] border border-[var(--border)] text-xs md:text-sm text-[var(--foreground-muted)] text-left hover:border-[var(--border-accent)] hover:text-[var(--foreground)] active:scale-[0.98] transition-all group"
    >
      <span className="flex items-center gap-2">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--accent)] opacity-50 group-hover:opacity-100 transition-opacity md:w-3.5 md:h-3.5">
          <polyline points="9,18 15,12 9,6"/>
        </svg>
        {children}
      </span>
    </button>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in-up`}>
      <div
        className={`max-w-[90%] md:max-w-[85%] rounded-2xl px-3 md:px-4 py-2.5 md:py-3 ${
          isUser
            ? "bg-[var(--accent)] text-[var(--background)] rounded-br-md"
            : "bg-[var(--background-card)] border border-[var(--border)] text-[var(--foreground)] rounded-bl-md"
        }`}
      >
        <div className="text-xs md:text-sm whitespace-pre-wrap leading-relaxed">{message.content}</div>
        <div
          className={`text-[9px] md:text-[10px] mt-1.5 md:mt-2 ${
            isUser ? "text-[var(--background)]/60" : "text-[var(--foreground-subtle)]"
          }`}
        >
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start animate-fade-in">
      <div className="bg-[var(--background-card)] border border-[var(--border)] rounded-2xl rounded-bl-md px-3 md:px-4 py-2.5 md:py-3">
        <div className="flex items-center gap-1 md:gap-1.5">
          <div className="w-1.5 h-1.5 md:w-2 md:h-2 rounded-full bg-[var(--accent)] animate-bounce" style={{ animationDelay: "0ms" }} />
          <div className="w-1.5 h-1.5 md:w-2 md:h-2 rounded-full bg-[var(--accent)] animate-bounce" style={{ animationDelay: "150ms" }} />
          <div className="w-1.5 h-1.5 md:w-2 md:h-2 rounded-full bg-[var(--accent)] animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
