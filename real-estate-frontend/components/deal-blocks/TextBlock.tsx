import React from "react";
import type { TextBlockProps } from "./types";

/**
 * Компонент для отображения текстовых блоков с поддержкой Markdown.
 * Используется для вывода произвольного контента, инструкций, предупреждений и т.д.
 */
export function TextBlock({ content, variant = "default" }: TextBlockProps) {
  const variantStyles = {
    default: "bg-[var(--background-card)] border-[var(--border)] text-[var(--foreground)]",
    info: "bg-blue-500/10 border-blue-500/30 text-[var(--foreground)]",
    warning: "bg-[var(--warning-muted)] border-[var(--warning)]/30 text-[var(--foreground)]",
    error: "bg-[var(--error-muted)] border-[var(--error)]/30 text-[var(--foreground)]",
  };

  const variantIcons = {
    default: null,
    info: (
      <svg
        className="w-4 h-4 md:w-5 md:h-5 text-blue-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    warning: (
      <svg
        className="w-4 h-4 md:w-5 md:h-5 text-[var(--warning)]"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
    ),
    error: (
      <svg
        className="w-4 h-4 md:w-5 md:h-5 text-[var(--error)]"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  };

  return (
    <div
      className={`border rounded-xl p-4 md:p-6 ${variantStyles[variant]}`}
    >
      {variantIcons[variant] && (
        <div className="flex items-start gap-2 md:gap-3">
          <div className="flex-shrink-0 mt-0.5">{variantIcons[variant]}</div>
          <div className="flex-1 min-w-0">
            <MarkdownContent content={content} />
          </div>
        </div>
      )}
      {!variantIcons[variant] && (
        <MarkdownContent content={content} />
      )}
    </div>
  );
}

/**
 * Простой рендерер Markdown (базовая поддержка).
 * В продакшене можно использовать библиотеку типа react-markdown.
 */
function MarkdownContent({ content }: { content: string }) {
  // Базовая обработка Markdown
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];

  lines.forEach((line, index) => {
    // Headers
    if (line.startsWith("### ")) {
      elements.push(
        <h3 key={index} className="text-base md:text-lg font-semibold mt-3 md:mt-4 mb-2 text-[var(--foreground)]">
          {line.replace("### ", "")}
        </h3>
      );
    } else if (line.startsWith("## ")) {
      elements.push(
        <h2 key={index} className="text-lg md:text-xl font-bold mt-3 md:mt-4 mb-2 text-[var(--foreground)]">
          {line.replace("## ", "")}
        </h2>
      );
    } else if (line.startsWith("# ")) {
      elements.push(
        <h1 key={index} className="text-xl md:text-2xl font-bold mt-3 md:mt-4 mb-2 text-[var(--foreground)]">
          {line.replace("# ", "")}
        </h1>
      );
    }
    // Lists
    else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <li key={index} className="ml-4 text-sm md:text-base text-[var(--foreground-muted)] leading-relaxed">
          {line.replace(/^[-*] /, "")}
        </li>
      );
    }
    // Numbered lists
    else if (/^\d+\. /.test(line)) {
      elements.push(
        <li key={index} className="ml-4 text-sm md:text-base text-[var(--foreground-muted)] leading-relaxed list-decimal">
          {line.replace(/^\d+\. /, "")}
        </li>
      );
    }
    // Paragraphs
    else if (line.trim()) {
      elements.push(
        <p key={index} className="mb-2 text-sm md:text-base text-[var(--foreground-muted)] leading-relaxed">
          {line}
        </p>
      );
    }
    // Empty lines - skip extra line breaks
    else if (elements.length > 0) {
      const lastElement = elements[elements.length - 1];
      const isLastBr = React.isValidElement(lastElement) && lastElement.type === 'br';
      if (!isLastBr) {
        elements.push(<div key={index} className="h-2" />);
      }
    }
  });

  return <div className="space-y-1">{elements}</div>;
}
