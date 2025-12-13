import React from "react";
import type { TimelineProps, TimelineStep } from "./types";

/**
 * Timeline component for displaying deal stages or project milestones.
 */
export function Timeline({ title, steps, currentStep }: TimelineProps) {
  if (!steps || steps.length === 0) {
    return (
      <div className="card p-12 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[var(--background-elevated)] flex items-center justify-center mx-auto mb-4">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--foreground-subtle)]">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12,6 12,12 16,14"/>
          </svg>
        </div>
        <p className="text-[var(--foreground-muted)]">Этапы не определены</p>
      </div>
    );
  }

  // Find current step index
  const currentIndex = currentStep
    ? steps.findIndex(s => s.id === currentStep)
    : steps.findIndex(s => s.status === "current");

  return (
    <div className="space-y-6">
      <h2 className="text-2xl text-[var(--foreground)]">{title || "Этапы сделки"}</h2>

      <div className="card p-6">
        {/* Desktop Timeline */}
        <div className="hidden md:block">
          <div className="relative">
            {/* Progress Line */}
            <div className="absolute top-6 left-0 right-0 h-0.5 bg-[var(--border)]">
              <div
                className="h-full bg-[var(--accent)] transition-all duration-500"
                style={{
                  width: currentIndex >= 0
                    ? `${((currentIndex + 0.5) / steps.length) * 100}%`
                    : "0%"
                }}
              />
            </div>

            {/* Steps */}
            <div className="relative flex justify-between">
              {steps.map((step, index) => (
                <TimelineStepDesktop
                  key={step.id}
                  step={step}
                  index={index}
                  isActive={currentIndex >= 0 ? index <= currentIndex : step.status === "completed"}
                  isCurrent={currentIndex === index || step.status === "current"}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Mobile Timeline */}
        <div className="md:hidden space-y-4">
          {steps.map((step, index) => (
            <TimelineStepMobile
              key={step.id}
              step={step}
              index={index}
              isActive={currentIndex >= 0 ? index <= currentIndex : step.status === "completed"}
              isCurrent={currentIndex === index || step.status === "current"}
              isLast={index === steps.length - 1}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function TimelineStepDesktop({
  step,
  index,
  isActive,
  isCurrent
}: {
  step: TimelineStep;
  index: number;
  isActive: boolean;
  isCurrent: boolean;
}) {
  return (
    <div className="flex flex-col items-center" style={{ width: "120px" }}>
      {/* Circle */}
      <div
        className={`w-12 h-12 rounded-full flex items-center justify-center z-10 transition-all duration-300 ${
          isCurrent
            ? "bg-[var(--accent)] text-[var(--background)] ring-4 ring-[var(--accent-glow)]"
            : isActive
            ? "bg-[var(--accent)] text-[var(--background)]"
            : "bg-[var(--background-card)] border-2 border-[var(--border)] text-[var(--foreground-subtle)]"
        }`}
      >
        {step.status === "completed" ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="20,6 9,17 4,12"/>
          </svg>
        ) : (
          <span className="text-sm font-bold">{index + 1}</span>
        )}
      </div>

      {/* Content */}
      <div className="mt-3 text-center">
        <p className={`text-sm font-medium ${isCurrent ? "text-[var(--accent)]" : "text-[var(--foreground)]"}`}>
          {step.title}
        </p>
        {step.date && (
          <p className="text-xs text-[var(--foreground-subtle)] mt-1">{step.date}</p>
        )}
        {step.description && (
          <p className="text-xs text-[var(--foreground-muted)] mt-1 max-w-[100px]">{step.description}</p>
        )}
      </div>
    </div>
  );
}

function TimelineStepMobile({
  step,
  index,
  isActive,
  isCurrent,
  isLast
}: {
  step: TimelineStep;
  index: number;
  isActive: boolean;
  isCurrent: boolean;
  isLast: boolean;
}) {
  return (
    <div className="flex gap-4">
      {/* Line and Circle */}
      <div className="flex flex-col items-center">
        <div
          className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
            isCurrent
              ? "bg-[var(--accent)] text-[var(--background)] ring-4 ring-[var(--accent-glow)]"
              : isActive
              ? "bg-[var(--accent)] text-[var(--background)]"
              : "bg-[var(--background-card)] border-2 border-[var(--border)] text-[var(--foreground-subtle)]"
          }`}
        >
          {step.status === "completed" ? (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20,6 9,17 4,12"/>
            </svg>
          ) : (
            <span className="text-sm font-bold">{index + 1}</span>
          )}
        </div>
        {!isLast && (
          <div className={`w-0.5 flex-1 min-h-[24px] ${isActive ? "bg-[var(--accent)]" : "bg-[var(--border)]"}`} />
        )}
      </div>

      {/* Content */}
      <div className={`pb-4 ${isLast ? "" : "pb-6"}`}>
        <p className={`font-medium ${isCurrent ? "text-[var(--accent)]" : "text-[var(--foreground)]"}`}>
          {step.title}
        </p>
        {step.date && (
          <p className="text-xs text-[var(--foreground-subtle)] mt-0.5">{step.date}</p>
        )}
        {step.description && (
          <p className="text-sm text-[var(--foreground-muted)] mt-1">{step.description}</p>
        )}
      </div>
    </div>
  );
}
