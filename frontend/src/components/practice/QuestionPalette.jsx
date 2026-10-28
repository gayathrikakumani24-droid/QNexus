import React from 'react';

export const QuestionPalette = ({
  totalQuestions = 10,
  currentIndex = 0,
  answers = {},
  markedForReview = {},
  onSelectQuestion,
}) => {
  return (
    <div className="bg-white border border-qnx-border rounded-2xl p-5 shadow-paper-sm space-y-4">
      <div className="flex items-center justify-between border-b border-qnx-border-light pb-3">
        <h3 className="font-serif text-base font-bold text-qnx-text">Question Palette</h3>
        <span className="text-xs font-semibold text-qnx-muted">
          {Object.keys(answers).filter(k => answers[k]?.selected_answer).length}/{totalQuestions} Answered
        </span>
      </div>

      {/* Palette Legend */}
      <div className="grid grid-cols-2 gap-2 text-[11px] text-qnx-muted pb-2 border-b border-qnx-border-light">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-qnx-sage-soft border border-qnx-sage/40"></span>
          <span>Answered</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-qnx-mustard-soft border border-qnx-mustard-soft"></span>
          <span>Review</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-white border border-qnx-border"></span>
          <span>Unanswered</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-qnx-olive border border-qnx-olive"></span>
          <span>Current</span>
        </div>
      </div>

      {/* Numbers Grid */}
      <div className="grid grid-cols-5 gap-2 max-h-60 overflow-y-auto pr-1">
        {Array.from({ length: totalQuestions }).map((_, idx) => {
          const isCurrent = currentIndex === idx;
          const isAnswered = !!answers[idx]?.selected_answer;
          const isMarked = !!markedForReview[idx];

          let btnStyle = 'bg-white border-qnx-border text-qnx-text hover:bg-qnx-cream-paper';
          if (isCurrent) {
            btnStyle = 'bg-qnx-olive text-white border-qnx-olive font-bold ring-2 ring-qnx-sage-soft';
          } else if (isMarked) {
            btnStyle = 'bg-qnx-mustard-soft border-qnx-mustard text-[#946E14] font-bold';
          } else if (isAnswered) {
            btnStyle = 'bg-qnx-sage-soft border-qnx-sage text-qnx-olive font-bold';
          }

          return (
            <button
              key={idx}
              onClick={() => onSelectQuestion(idx)}
              className={`h-9 w-full rounded-lg border text-xs font-semibold transition-all flex items-center justify-center ${btnStyle}`}
            >
              {idx + 1}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuestionPalette;
