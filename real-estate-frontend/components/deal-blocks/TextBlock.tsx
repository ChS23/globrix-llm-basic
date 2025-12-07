import React from "react";
import type { TextBlockProps } from "./types";

/**
 * Компонент для отображения текстовых блоков с поддержкой Markdown.
 * Используется для вывода произвольного контента, инструкций, предупреждений и т.д.
 */
export function TextBlock({ content, variant = "default" }: TextBlockProps) {
  const variantStyles = {
    default: "bg-white border-gray-200 text-gray-900",
    info: "bg-blue-50 border-blue-200 text-blue-900",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-900",
    error: "bg-red-50 border-red-200 text-red-900",
  };

  const variantIcons = {
    default: null,
    info: (
      <svg
        className="w-5 h-5 text-blue-600"
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
        className="w-5 h-5 text-yellow-600"
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
        className="w-5 h-5 text-red-600"
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
      className={`border rounded-lg p-6 mb-6 ${variantStyles[variant]}`}
    >
      {variantIcons[variant] && (
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">{variantIcons[variant]}</div>
          <div className="flex-1 prose prose-sm max-w-none">
            <MarkdownContent content={content} />
          </div>
        </div>
      )}
      {!variantIcons[variant] && (
        <div className="prose prose-sm max-w-none">
          <MarkdownContent content={content} />
        </div>
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
        <h3 key={index} className="text-lg font-semibold mt-4 mb-2">
          {line.replace("### ", "")}
        </h3>
      );
    } else if (line.startsWith("## ")) {
      elements.push(
        <h2 key={index} className="text-xl font-bold mt-4 mb-2">
          {line.replace("## ", "")}
        </h2>
      );
    } else if (line.startsWith("# ")) {
      elements.push(
        <h1 key={index} className="text-2xl font-bold mt-4 mb-2">
          {line.replace("# ", "")}
        </h1>
      );
    }
    // Lists
    else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <li key={index} className="ml-4">
          {line.replace(/^[-*] /, "")}
        </li>
      );
    }
    // Paragraphs
    else if (line.trim()) {
      elements.push(
        <p key={index} className="mb-2">
          {line}
        </p>
      );
    }
    // Empty lines
    else {
      elements.push(<br key={index} />);
    }
  });

  return <div>{elements}</div>;
}
