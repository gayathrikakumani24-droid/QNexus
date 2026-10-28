import React from 'react';
import { BookOpen, Search, ArrowRight, RotateCcw, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const EmptyState = ({
  icon: Icon = Search,
  title = "No questions found",
  description = "Try adjusting your filters, searching for a different concept, or exploring chapters.",
  actionText = "Clear Filters",
  onAction,
  actionLink,
  secondaryActionText,
  onSecondaryAction,
  className = ""
}) => {
  return (
    <div className={`text-center py-12 px-6 bg-white border border-qnx-border rounded-card shadow-paper-sm max-w-xl mx-auto my-6 animate-fade-up ${className}`}>
      <div className="w-14 h-14 bg-qnx-sage-soft text-qnx-olive rounded-full flex items-center justify-center mx-auto mb-4 border border-qnx-sage/30">
        <Icon className="w-7 h-7" />
      </div>
      <h3 className="font-serif text-2xl text-qnx-text font-bold mb-2">{title}</h3>
      <p className="text-qnx-muted text-sm leading-relaxed max-w-md mx-auto mb-6">
        {description}
      </p>

      <div className="flex flex-wrap items-center justify-center gap-3">
        {actionLink ? (
          <Link
            to={actionLink}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-qnx-olive hover:bg-qnx-olive-dark text-white text-sm font-medium rounded-lg shadow-paper-sm transition-all hover:-translate-y-0.5"
          >
            {actionText} <ArrowRight className="w-4 h-4" />
          </Link>
        ) : onAction ? (
          <button
            onClick={onAction}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-qnx-olive hover:bg-qnx-olive-dark text-white text-sm font-medium rounded-lg shadow-paper-sm transition-all hover:-translate-y-0.5"
          >
            <RotateCcw className="w-4 h-4" /> {actionText}
          </button>
        ) : null}

        {onSecondaryAction && secondaryActionText && (
          <button
            onClick={onSecondaryAction}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-qnx-cream-paper hover:bg-qnx-cream border border-qnx-border text-qnx-text text-sm font-medium rounded-lg transition-colors"
          >
            {secondaryActionText}
          </button>
        )}
      </div>
    </div>
  );
};

export default EmptyState;
