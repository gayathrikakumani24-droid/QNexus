import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Bookmark, 
  ArrowRight, 
  Sparkles, 
  Layers, 
  CheckCircle2, 
  Flame, 
  FileText,
  Clock
} from 'lucide-react';
import LatexRenderer from '../common/LatexRenderer';
import QuestionDiagram from '../common/QuestionDiagram';

export const QuestionCard = ({
  question,
  similarityScore,
  isBookmarked = false,
  onToggleBookmark,
  onExplain,
  onHint,
  onSimilar,
  className = ''
}) => {
  if (!question) return null;

  const {
    question_id,
    question_number,
    content,
    options = [],
    subject = 'General',
    chapter = 'General',
    concept = 'Core Concept',
    difficulty = 'Medium',
    question_type = 'MCQ',
    year = 2026,
    shift = 'Shift 1',
    paper_id
  } = question;

  // Determine semantic colors
  const subjectBadges = {
    Physics: 'bg-qnx-sage-soft text-qnx-olive border-qnx-sage/40',
    Chemistry: 'bg-qnx-blue-soft text-[#38679E] border-qnx-blue-soft',
    Mathematics: 'bg-qnx-terracotta-soft text-qnx-terracotta border-qnx-terracotta-soft',
    General: 'bg-qnx-border-light text-qnx-muted border-qnx-border',
  };

  const difficultyBadges = {
    Easy: 'bg-qnx-sage-light text-qnx-olive border-qnx-sage/30',
    Medium: 'bg-qnx-mustard-light text-[#946E14] border-qnx-mustard-soft',
    Hard: 'bg-qnx-terracotta-light text-qnx-terracotta border-qnx-terracotta-soft',
  };

  // Check if concept is high-frequency
  const isHighFrequency = ['torque', 'rotational motion', 'definite integrals', 'matrices', 'thermodynamics', 'chemical bonding'].some(
    k => (concept || '').toLowerCase().includes(k) || (chapter || '').toLowerCase().includes(k)
  );

  return (
    <div className={`bg-white border border-qnx-border rounded-card p-5 sm:p-6 shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-0.5 space-y-4 ${className}`}>
      {/* Top Header: Subject, Exam, Year, Shift, & High-Frequency Tag */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-qnx-border-light pb-3">
        <div className="flex flex-wrap items-center gap-2">
          {/* Subject Badge */}
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border uppercase tracking-wider ${subjectBadges[subject] || subjectBadges.General}`}>
            {subject}
          </span>

          {/* Exam, Year & Shift */}
          <span className="text-xs font-semibold text-qnx-muted">
            JEE Main {year} • {shift}
          </span>

          {/* Question Number */}
          {question_number && (
            <span className="text-xs text-qnx-muted/70">
              (Q.{question_number})
            </span>
          )}

          {/* High-Frequency Tag (Mustard) */}
          {isHighFrequency && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-qnx-mustard-soft text-[#946E14] border border-qnx-mustard-soft flex items-center gap-1">
              🟡 High Frequency
            </span>
          )}

          {/* Similarity Score Badge */}
          {similarityScore !== undefined && similarityScore !== null && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-qnx-blue-soft text-[#38679E] border border-qnx-blue-soft">
              {Math.round(similarityScore * 100)}% Match
            </span>
          )}
        </div>

        {/* Bookmark Button */}
        {onToggleBookmark && (
          <button
            onClick={() => onToggleBookmark(question)}
            className={`p-1.5 rounded-lg border transition-colors ${
              isBookmarked
                ? 'bg-qnx-terracotta-soft text-qnx-terracotta border-qnx-terracotta-soft'
                : 'text-qnx-muted hover:text-qnx-olive hover:bg-qnx-sage-soft border-transparent'
            }`}
            title={isBookmarked ? 'Remove from Mistakes' : 'Save to Mistakes'}
          >
            <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-current' : ''}`} />
          </button>
        )}
      </div>

      {/* Main Question Statement */}
      <div className="text-sm sm:text-base font-normal text-qnx-text leading-relaxed">
        <LatexRenderer content={content} />
      </div>

      {/* Question Diagram if present */}
      <QuestionDiagram imageUrls={question.image_urls} />

      {/* Options (if present) */}
      {options && options.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
          {options.map((opt) => (
            <div
              key={opt.id}
              className="px-3 py-2 bg-qnx-cream-paper border border-qnx-border rounded-lg text-xs text-qnx-text flex items-start gap-2.5"
            >
              <span className="font-bold text-qnx-olive shrink-0">({opt.id})</span>
              <div className="flex-1 overflow-x-auto">
                {opt.content && opt.content.trim() ? (
                  <LatexRenderer content={opt.content} inline={true} />
                ) : (
                  <span className="text-qnx-muted italic text-[11px]">(See diagram in question)</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Chapter & Concept Metadata Footer */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-qnx-border-light text-xs">
        <div className="flex flex-wrap items-center gap-3 text-qnx-muted">
          <span>
            <strong className="text-qnx-text font-semibold">Chapter:</strong> {chapter}
          </span>
          <span className="text-qnx-border">•</span>
          <span>
            <strong className="text-qnx-text font-semibold">Concept:</strong> {concept}
          </span>
          <span className="text-qnx-border">•</span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${difficultyBadges[difficulty] || difficultyBadges.Medium}`}>
            {difficulty}
          </span>
        </div>

        {/* Action CTAs */}
        <div className="flex items-center gap-2">
          {onExplain && (
            <button
              onClick={() => onExplain(question)}
              className="px-2.5 py-1 text-xs font-semibold text-[#38679E] bg-qnx-blue-soft/60 hover:bg-qnx-blue-soft rounded-lg transition-colors"
            >
              Explain
            </button>
          )}

          {onHint && (
            <button
              onClick={() => onHint(question)}
              className="px-2.5 py-1 text-xs font-semibold text-[#946E14] bg-qnx-mustard-soft/60 hover:bg-qnx-mustard-soft rounded-lg transition-colors"
            >
              Hint
            </button>
          )}

          <Link
            to={`/question/${question_id}`}
            className="inline-flex items-center gap-1 px-3 py-1 bg-qnx-olive hover:bg-qnx-olive-dark text-white text-xs font-semibold rounded-lg shadow-paper-sm transition-all hover:-translate-y-0.5"
          >
            <span>View Question</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default QuestionCard;
