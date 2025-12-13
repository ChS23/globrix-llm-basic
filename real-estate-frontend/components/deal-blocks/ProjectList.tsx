import React from "react";
import type { ProjectListProps, Project } from "./types";

/**
 * Project list component for displaying real estate developments.
 */
export function ProjectList({ projects }: ProjectListProps) {
  if (!projects || projects.length === 0) {
    return (
      <div className="card p-12 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[var(--background-elevated)] flex items-center justify-center mx-auto mb-4">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--foreground-subtle)]">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <line x1="9" y1="3" x2="9" y2="21"/>
          </svg>
        </div>
        <p className="text-[var(--foreground-muted)]">Проекты не найдены</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl text-[var(--foreground)]">Проекты</h2>
          <p className="text-sm text-[var(--foreground-muted)] mt-1">Найдено: {projects.length}</p>
        </div>
      </div>

      {/* Projects List */}
      <div className="space-y-4">
        {projects.map((project, index) => (
          <ProjectCard key={project.id} project={project} index={index} />
        ))}
      </div>
    </div>
  );
}

function ProjectCard({ project, index }: { project: Project; index: number }) {
  const hasImage = project.image_url;

  return (
    <div className={`card card-hover overflow-hidden animate-fade-in-up stagger-${Math.min(index + 1, 6)}`}>
      <div className="flex flex-col md:flex-row">
        {/* Image / Placeholder */}
        {hasImage ? (
          <div className="md:w-64 h-48 md:h-auto flex-shrink-0 bg-[var(--background-elevated)]">
            <img
              src={project.image_url}
              alt={project.name}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="md:w-64 h-48 md:h-auto flex-shrink-0 bg-gradient-to-br from-[var(--accent-dark)]/10 to-[var(--accent-light)]/5 flex items-center justify-center">
            <div className="w-16 h-16 rounded-2xl bg-[var(--background-card)] border border-[var(--border)] flex items-center justify-center">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--accent)]">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="9" y1="3" x2="9" y2="21"/>
              </svg>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 p-5">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-xl font-semibold text-[var(--foreground)] mb-1">{project.name}</h3>
              <p className="text-sm text-[var(--foreground-muted)]">{project.developer}</p>
            </div>
            {project.completion_date && (
              <span className="badge badge-primary">
                Сдача: {project.completion_date}
              </span>
            )}
          </div>

          {/* Location */}
          <div className="flex items-center gap-2 text-sm text-[var(--foreground-muted)] mb-4">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            <span>{project.location}</span>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap gap-4 mb-4">
            <div className="flex items-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--accent)]">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              </svg>
              <span className="text-sm text-[var(--foreground)]">{project.total_units} юнитов</span>
            </div>

            {(project.min_price || project.max_price) && (
              <div className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--accent)]">
                  <line x1="12" y1="1" x2="12" y2="23"/>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
                <span className="text-sm text-[var(--foreground)]">
                  {project.min_price && project.max_price
                    ? `от ${formatCompact(project.min_price)} до ${formatCompact(project.max_price)}`
                    : project.min_price
                    ? `от ${formatCompact(project.min_price)}`
                    : `до ${formatCompact(project.max_price!)}`}
                </span>
              </div>
            )}
          </div>

          {/* Action */}
          <button className="btn-secondary flex items-center gap-2">
            <span>Смотреть юниты</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="5" y1="12" x2="19" y2="12"/>
              <polyline points="12,5 19,12 12,19"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

function formatCompact(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(0)}K`;
  }
  return num.toString();
}
