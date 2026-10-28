import React, { useState, useEffect } from 'react';
import { X, Sparkles, HelpCircle, ChevronRight, CheckCircle2, ArrowRight } from 'lucide-react';
import { getQuestionHint } from '../../services/aiService';
import LatexRenderer from '../common/LatexRenderer';

export const HintDrawer = ({ question, onClose }) => {
  const [currentLevel, setCurrentLevel] = useState(1);
  const [hints, setHints] = useState({});
  const [loading, setLoading] = useState(false);

  const fetchHintForLevel = async (lvl) => {
    if (hints[lvl]) return;
    try {
      setLoading(true);
      const res = await getQuestionHint(question.question_id, lvl);
      setHints(prev => ({ ...prev, [lvl]: res.hint_text }));
    } catch (err) {
      console.error("Hint generation failed:", err);
      setHints(prev => ({
        ...prev,
        [lvl]: "Focus on identifying known variables and standard governing formulas."
      }));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (question?.question_id) {
      fetchHintForLevel(1);
    }
  }, [question]);

  const handleNextLevel = () => {
    if (currentLevel < 3) {
      const next = currentLevel + 1;
      setCurrentLevel(next);
      fetchHintForLevel(next);
    }
  };

  if (!question) return null;

  const hintTitles = {
    1: 'Level 1: Conceptual Direction',
    2: 'Level 2: Formula & Variable Setup',
    3: 'Level 3: Critical Transformation Step'
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-qnx-text/30 backdrop-blur-xs animate-fade-in">
      <div className="bg-[#FCFAF5] border-l border-qnx-border w-full max-w-md h-full flex flex-col justify-between shadow-paper-lg animate-slide-in">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-qnx-border bg-white">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-qnx-mustard-soft text-[#946E14] flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-serif text-lg font-bold text-qnx-text">
                Progressive AI Hints
              </h3>
              <p className="text-[11px] text-qnx-muted">Non-spoiler guidance</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-qnx-muted hover:text-qnx-text rounded-lg hover:bg-qnx-cream-paper transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1 text-xs sm:text-sm">
          {/* Level Progress Indicator */}
          <div className="flex items-center justify-between border-b border-qnx-border-light pb-3">
            {[1, 2, 3].map((lvl) => (
              <button
                key={lvl}
                onClick={() => {
                  setCurrentLevel(lvl);
                  fetchHintForLevel(lvl);
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  currentLevel === lvl
                    ? 'bg-[#946E14] text-white shadow-paper-sm'
                    : hints[lvl]
                    ? 'bg-qnx-mustard-soft text-[#946E14] border border-qnx-mustard-soft'
                    : 'bg-white border border-qnx-border text-qnx-muted'
                }`}
              >
                Hint {lvl}
              </button>
            ))}
          </div>

          {/* Hint Cards */}
          <div className="space-y-4">
            {[1, 2, 3].slice(0, currentLevel).map((lvl) => (
              <div
                key={lvl}
                className="bg-white border border-qnx-border rounded-xl p-4 shadow-paper-sm space-y-2 animate-fade-up"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold uppercase tracking-wide text-[#946E14]">
                    {hintTitles[lvl]}
                  </span>
                  <span className="text-[10px] text-qnx-muted">Level {lvl}/3</span>
                </div>

                <div className="text-xs leading-relaxed text-qnx-text pt-1">
                  {hints[lvl] ? (
                    <LatexRenderer content={hints[lvl]} />
                  ) : loading ? (
                    <span className="text-qnx-muted italic">Generating progressive clue...</span>
                  ) : (
                    <span className="text-qnx-muted">Click to reveal clue.</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-white border-t border-qnx-border flex items-center justify-between">
          <span className="text-[11px] text-qnx-muted">Never reveals final answer.</span>
          {currentLevel < 3 ? (
            <button
              onClick={handleNextLevel}
              disabled={loading}
              className="px-4 py-2 bg-[#946E14] hover:bg-[#7D5C0E] text-white font-semibold text-xs rounded-xl shadow-paper-sm transition-all hover:-translate-y-0.5 flex items-center gap-1.5"
            >
              <span>Next Hint Level ({currentLevel + 1})</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              onClick={onClose}
              className="px-4 py-2 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-xs rounded-xl transition-colors"
            >
              I Understand
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default HintDrawer;
