import React, { useState, useEffect } from 'react';
import { X, Sparkles, BookOpen, AlertCircle, CheckCircle2, ChevronRight, Layers } from 'lucide-react';
import { explainQuestion } from '../../services/aiService';
import LatexRenderer from '../common/LatexRenderer';

export const ExplanationModal = ({ question, userAttempt = null, onClose }) => {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchExplanation = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await explainQuestion(question.question_id, userAttempt);
        if (isMounted) {
          setExplanation(data);
        }
      } catch (err) {
        console.error("Explanation generation failed:", err);
        if (isMounted) {
          setError("Step-by-step pedagogical explanation is temporarily unavailable.");
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    if (question?.question_id) {
      fetchExplanation();
    }
    return () => { isMounted = false; };
  }, [question, userAttempt]);

  if (!question) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-qnx-text/40 backdrop-blur-xs animate-fade-in">
      <div className="bg-[#FCFAF5] border border-qnx-border rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-paper-lg overflow-hidden animate-scale-in">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-qnx-border bg-white">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-qnx-olive text-white flex items-center justify-center">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-serif text-lg font-bold text-qnx-text">
                Pedagogical Step-by-Step Explanation
              </h3>
              <p className="text-[11px] text-qnx-muted">
                {question.subject} • {question.chapter} • {question.concept}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-qnx-muted hover:text-qnx-text rounded-lg hover:bg-qnx-cream-paper transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs sm:text-sm">
          {loading ? (
            <div className="py-12 text-center space-y-3">
              <div className="w-8 h-8 border-3 border-qnx-olive border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="font-serif text-base text-qnx-text font-bold">
                Synthesizing Pedagogical Explanation...
              </p>
              <p className="text-xs text-qnx-muted">
                Connecting theoretical concepts, governing equations, and derivation steps.
              </p>
            </div>
          ) : error ? (
            <div className="p-4 bg-qnx-terracotta-soft text-qnx-terracotta rounded-xl flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          ) : explanation ? (
            <div className="space-y-6">
              {/* Concept Overview Box */}
              {explanation.concept_summary && (
                <div className="p-4 bg-qnx-sage-light border border-qnx-sage-soft rounded-xl space-y-1.5">
                  <p className="text-xs font-bold uppercase tracking-wider text-qnx-olive flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" /> Conceptual Overview
                  </p>
                  <p className="text-xs text-qnx-text leading-relaxed">
                    {explanation.concept_summary}
                  </p>
                </div>
              )}

              {/* Key Formulae */}
              {explanation.key_formulae && explanation.key_formulae.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wider text-qnx-muted">
                    Governing Formulae
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {explanation.key_formulae.map((f, i) => (
                      <div
                        key={i}
                        className="px-3 py-1.5 bg-white border border-qnx-border rounded-lg text-xs font-serif"
                      >
                        <LatexRenderer content={f} inline={true} />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Detailed Step-by-Step Derivation */}
              <div className="space-y-2">
                <p className="text-xs font-bold uppercase tracking-wider text-qnx-muted">
                  Step-by-Step Solution & Derivation
                </p>
                <div className="p-5 bg-white border border-qnx-border rounded-xl shadow-paper-sm leading-relaxed text-qnx-text">
                  <LatexRenderer content={explanation.step_by_step_solution} />
                </div>
              </div>

              {/* Common Pitfalls Box */}
              {explanation.common_pitfalls && (
                <div className="p-4 bg-qnx-terracotta-light border border-qnx-terracotta-soft rounded-xl space-y-1.5">
                  <p className="text-xs font-bold uppercase tracking-wider text-qnx-terracotta flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5" /> Common Exam Pitfalls
                  </p>
                  <p className="text-xs text-qnx-text leading-relaxed">
                    {explanation.common_pitfalls}
                  </p>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 bg-white border-t border-qnx-border flex items-center justify-between">
          <span className="text-[11px] text-qnx-muted">
            Ground-truth derived from official JEE Main answer keys.
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-xs rounded-lg transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExplanationModal;
