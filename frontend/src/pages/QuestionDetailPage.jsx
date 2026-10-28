import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Sparkles, 
  BookOpen, 
  Bookmark, 
  Eye, 
  EyeOff, 
  CheckCircle2, 
  XCircle, 
  Layers, 
  ArrowRight,
  TrendingUp,
  Award
} from 'lucide-react';
import { getQuestionById, getSimilarQuestions } from '../services/aiService';
import { saveMistake } from '../services/mistakeService';
import LatexRenderer from '../components/common/LatexRenderer';
import QuestionDiagram from '../components/common/QuestionDiagram';
import QuestionCard from '../components/questions/QuestionCard';
import { QuestionCardSkeleton } from '../components/common/LoadingSkeleton';
import EmptyState from '../components/common/EmptyState';
import ExplanationModal from '../components/ai/ExplanationModal';
import HintDrawer from '../components/ai/HintDrawer';

export const QuestionDetailPage = () => {
  const { id } = useParams();
  const [question, setQuestion] = useState(null);
  const [similarQuestions, setSimilarQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAnswer, setShowAnswer] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);
  const [isBookmarked, setIsBookmarked] = useState(false);

  // Modals
  const [isExplainOpen, setIsExplainOpen] = useState(false);
  const [isHintOpen, setIsHintOpen] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const fetchQuestionAndSimilar = async () => {
      try {
        setLoading(true);
        setShowAnswer(false);
        setSelectedOption(null);

        const qDoc = await getQuestionById(id);
        if (isMounted) {
          setQuestion(qDoc);
        }

        // Fetch similar PYQs
        try {
          const simRes = await getSimilarQuestions(id, 4);
          if (isMounted) setSimilarQuestions(simRes || []);
        } catch (simErr) {
          console.warn("Could not fetch similar questions:", simErr);
        }

      } catch (err) {
        console.error("Failed to load question details:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchQuestionAndSimilar();
    return () => { isMounted = false; };
  }, [id]);

  const handleSaveMistake = async () => {
    if (!question) return;
    try {
      await saveMistake({
        questionId: question.question_id,
        userAnswer: selectedOption,
        correctAnswer: question.correct_option || (question.numerical_answer !== null ? String(question.numerical_answer) : null),
        mistakeTag: 'Conceptual Gap',
        userNotes: 'Saved from Question Detail View for focused practice.',
      });
      setIsBookmarked(true);
      alert('Question saved to Mistake Notebook.');
    } catch (err) {
      console.error("Save mistake failed:", err);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-8 space-y-6">
        <QuestionCardSkeleton />
      </div>
    );
  }

  if (!question) {
    return (
      <EmptyState
        title="Question Not Found"
        description={`We could not locate question with ID '${id}'.`}
        actionText="Back to Browse"
        actionLink="/search"
      />
    );
  }

  const {
    question_id,
    content,
    options = [],
    subject = 'General',
    chapter = 'General',
    concept = 'Core Concept',
    difficulty = 'Medium',
    year = 2026,
    shift = 'Shift 1',
    question_type = 'MCQ',
    image_urls = [],
    correct_option,
    numerical_answer,
    official_solution
  } = question;

  const verifiedAnswer = correct_option || (numerical_answer !== null && numerical_answer !== undefined ? String(numerical_answer) : null);

  return (
    <div className="space-y-8 animate-fade-up max-w-4xl mx-auto pb-16">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Link
          to="/search"
          className="inline-flex items-center gap-2 text-xs font-semibold text-qnx-muted hover:text-qnx-olive transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Questions</span>
        </Link>

        <button
          onClick={handleSaveMistake}
          className={`px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition-colors ${
            isBookmarked
              ? 'bg-qnx-terracotta-soft text-qnx-terracotta border-qnx-terracotta-soft'
              : 'bg-white border-qnx-border text-qnx-text hover:bg-qnx-cream-paper'
          }`}
        >
          <Bookmark className={`w-3.5 h-3.5 ${isBookmarked ? 'fill-current' : ''}`} />
          <span>{isBookmarked ? 'Saved in Mistakes' : 'Save to Mistakes'}</span>
        </button>
      </div>

      {/* Main Question Card */}
      <div className="bg-white border border-qnx-border rounded-2xl p-6 sm:p-8 shadow-paper space-y-6">
        {/* Header Metadata */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-qnx-border-light pb-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-qnx-sage-soft text-qnx-olive border border-qnx-sage/30 uppercase tracking-wider">
              {subject}
            </span>
            <span className="text-xs font-semibold text-qnx-muted">
              JEE Main {year} • {shift}
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-qnx-mustard-soft text-[#946E14] border border-qnx-mustard-soft">
              {difficulty}
            </span>
          </div>
        </div>

        {/* Question Statement */}
        <div className="text-base sm:text-lg font-normal text-qnx-text leading-relaxed">
          <LatexRenderer content={content} />
        </div>

        {/* Question Diagram if present */}
        <QuestionDiagram imageUrls={image_urls || question.image_urls || []} />

        {/* Interactive Option Selector / Numerical Input */}
        {(!options || options.length === 0 || question_type === 'NUMERICAL') ? (
          <div className="space-y-3 p-5 bg-qnx-cream-paper border border-qnx-border rounded-xl">
            <p className="text-xs font-bold uppercase tracking-wider text-qnx-muted">Numerical Question</p>
            <div className="flex items-center gap-3">
              <input
                type="text"
                placeholder="Enter your numerical answer to test..."
                value={selectedOption || ''}
                disabled={showAnswer}
                onChange={(e) => setSelectedOption(e.target.value)}
                className="w-full sm:w-80 px-4 py-2.5 bg-white border border-qnx-border rounded-xl text-sm font-semibold text-qnx-text focus:outline-none focus:border-qnx-olive shadow-paper-sm"
              />
              {selectedOption && (
                <button
                  type="button"
                  onClick={() => setSelectedOption('')}
                  className="text-xs text-qnx-muted hover:text-qnx-terracotta underline"
                >
                  Clear
                </button>
              )}
            </div>
            {showAnswer && verifiedAnswer && (
              <div className="p-3 bg-white border border-qnx-border rounded-lg text-xs space-y-1">
                <p className="text-qnx-muted">
                  Your Answer: <strong className={selectedOption && selectedOption.trim() === verifiedAnswer.trim() ? 'text-qnx-olive' : 'text-qnx-terracotta'}>{selectedOption || 'None'}</strong>
                </p>
                <p className="text-qnx-olive font-bold">
                  Official Key: {verifiedAnswer}
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-2.5 pt-2">
            <p className="text-xs font-bold uppercase tracking-wider text-qnx-muted">Options</p>
            <div className="grid grid-cols-1 gap-2.5">
              {options.map((opt) => {
                const isSelected = selectedOption === opt.id;
                const isCorrect = showAnswer && verifiedAnswer && verifiedAnswer.toUpperCase() === opt.id.toUpperCase();
                const isWrong = showAnswer && isSelected && !isCorrect;

                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => !showAnswer && setSelectedOption(opt.id)}
                    className={`w-full p-3.5 rounded-xl border text-left text-xs transition-all flex items-start gap-3 ${
                      isCorrect
                        ? 'bg-qnx-sage-soft border-qnx-olive text-qnx-olive font-bold'
                        : isWrong
                        ? 'bg-qnx-terracotta-soft border-qnx-terracotta text-qnx-terracotta'
                        : isSelected
                        ? 'bg-qnx-cream border-qnx-olive text-qnx-text font-semibold shadow-paper-sm'
                        : 'bg-qnx-cream-paper border-qnx-border text-qnx-text hover:bg-qnx-cream'
                    }`}
                  >
                    <span className="w-6 h-6 rounded-full bg-white border border-qnx-border flex items-center justify-center font-bold shrink-0">
                      {opt.id}
                    </span>
                    <div className="flex-1 overflow-x-auto pt-0.5">
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
        )}

        {/* Progressive Disclosure Controls */}
        <div className="pt-4 border-t border-qnx-border-light flex flex-wrap items-center justify-between gap-3">
          <button
            onClick={() => setShowAnswer(!showAnswer)}
            className="px-4 py-2 bg-qnx-cream-paper hover:bg-qnx-cream border border-qnx-border text-qnx-text font-semibold text-xs rounded-xl transition-colors flex items-center gap-2"
          >
            {showAnswer ? <EyeOff className="w-4 h-4 text-qnx-muted" /> : <Eye className="w-4 h-4 text-qnx-muted" />}
            <span>{showAnswer ? 'Hide Solution & Answer' : 'Reveal Official Solution'}</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsHintOpen(true)}
              className="px-4 py-2 bg-qnx-mustard-soft hover:bg-qnx-mustard text-[#946E14] font-semibold text-xs rounded-xl border border-qnx-mustard-soft transition-colors flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Get Hint</span>
            </button>

            <button
              onClick={() => setIsExplainOpen(true)}
              className="px-4 py-2 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-xs rounded-xl shadow-paper-sm transition-all hover:-translate-y-0.5 flex items-center gap-1.5"
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Step-by-Step AI Explanation</span>
            </button>
          </div>
        </div>

        {/* Revealed Solution Box */}
        {showAnswer && (
          <div className="p-5 bg-qnx-sage-light border border-qnx-sage-soft rounded-xl space-y-3 animate-fade-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-qnx-olive flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Official Verified Answer
              </span>
              <span className="font-serif text-lg font-bold text-qnx-olive">
                {verifiedAnswer ? `Option (${verifiedAnswer})` : 'Numerical Answer Verified'}
              </span>
            </div>

            {official_solution && (
              <div className="text-xs text-qnx-text pt-2 border-t border-qnx-sage-soft leading-relaxed">
                <LatexRenderer content={official_solution} />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Similar PYQs Section */}
      {similarQuestions.length > 0 && (
        <div className="space-y-4 pt-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <h2 className="font-serif text-2xl font-bold text-qnx-text">
                Semantically Similar PYQs
              </h2>
              <p className="text-xs text-qnx-muted">
                Questions testing related principles across other exam shifts.
              </p>
            </div>
            <Link to={`/search?concept=${encodeURIComponent(concept)}`} className="text-xs font-bold text-qnx-olive hover:underline">
              Search Concept →
            </Link>
          </div>

          <div className="space-y-3">
            {similarQuestions.map((simItem, idx) => {
              const q = simItem.question || simItem;
              if (!q) return null;
              return (
                <QuestionCard
                  key={q.question_id || idx}
                  question={q}
                  similarityScore={simItem.similarity_score}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* Modals */}
      {isExplainOpen && (
        <ExplanationModal
          question={question}
          userAttempt={selectedOption}
          onClose={() => setIsExplainOpen(false)}
        />
      )}

      {isHintOpen && (
        <HintDrawer
          question={question}
          onClose={() => setIsHintOpen(false)}
        />
      )}
    </div>
  );
};

export default QuestionDetailPage;
