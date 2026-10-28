import React from 'react';
import LatexRenderer from '../common/LatexRenderer';

export const OptionSelector = ({
  options = [],
  selectedOption = null,
  onSelectOption,
  disabled = false,
}) => {
  if (!options || options.length === 0) return null;

  return (
    <div className="space-y-2.5">
      <p className="text-xs font-bold uppercase tracking-wider text-qnx-muted">Select Your Option</p>
      <div className="grid grid-cols-1 gap-2.5">
        {options.map((opt) => {
          const isSelected = selectedOption === opt.id;

          return (
            <button
              key={opt.id}
              type="button"
              disabled={disabled}
              onClick={() => onSelectOption(opt.id)}
              className={`w-full p-4 rounded-xl border text-left text-xs transition-all flex items-start gap-3.5 ${
                isSelected
                  ? 'bg-qnx-sage-soft border-qnx-olive text-qnx-text font-semibold shadow-paper-sm'
                  : 'bg-white border-qnx-border text-qnx-text hover:bg-qnx-cream-paper'
              } ${disabled ? 'cursor-not-allowed opacity-75' : ''}`}
            >
              <span
                className={`w-6 h-6 rounded-full border flex items-center justify-center font-bold text-xs shrink-0 transition-colors ${
                  isSelected
                    ? 'bg-qnx-olive border-qnx-olive text-white'
                    : 'bg-qnx-cream-paper border-qnx-border text-qnx-muted'
                }`}
              >
                {opt.id}
              </span>
              <div className="flex-1 overflow-x-auto pt-0.5 leading-relaxed text-sm">
                {opt.content && opt.content.trim() ? (
                  <LatexRenderer content={opt.content} inline={true} />
                ) : (
                  <span className="text-qnx-muted italic text-xs">(See diagram in question)</span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default OptionSelector;
