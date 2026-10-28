import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  BookOpen, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  ArrowRight, 
  ArrowLeft, 
  Bookmark, 
  Award, 
  RotateCcw,
  Sparkles,
  Layers,
  ChevronRight
} from 'lucide-react';
import { 
  startPracticeSession, 
  recordPracticeAnswer, 
  submitPracticeSession 
} from '../services/practiceService';
import { saveMistake } from '../services/mistakeService';
import Timer from '../components/practice/Timer';
import QuestionPalette from '../components/practice/QuestionPalette';
import OptionSelector from '../components/practice/OptionSelector';
import LatexRenderer from '../components/common/LatexRenderer';
import QuestionDiagram from '../components/common/QuestionDiagram';
import StatCard from '../components/common/StatCard';
import ExplanationModal from '../components/ai/ExplanationModal';
import HintDrawer from '../components/ai/HintDrawer';
import { DEFAULT_SYLLABUS_HIERARCHY } from '../data/syllabusHierarchy';

export const PracticePage = () => {
  const [searchParams] = useSearchParams();
  const preSubject = searchParams.get('subject') || 'All';
  const preChapter = searchParams.get('chapter') || '';
  const preConcept = searchParams.get('concept') || '';
  const prePaperId = searchParams.get('paper_id') || '';

  // Configuration Form State
  const [config, setConfig] = useState({
    subject: preSubject,
    chapter: preChapter,
    concept: preConcept,
    difficulty: 'All',
    year: 'All',
    session: 'All',
    shift: 'All',
    num_questions: 10,
    paper_id: prePaperId,
  });

  // Session State
  const [session, setSession] = useState(null); // PracticeStartResponse
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({}); // { [index]: { selected_answer, time_spent } }
  const [markedForReview, setMarkedForReview] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null); // PracticeSubmitResponse

  // AI Modal States
  const [explainingQuestion, setExplainingQuestion] = useState(null);
  const [hintingQuestion, setHintingQuestion] = useState(null);

  const handleStartSession = async (e) => {
    if (e) e.preventDefault();
    try {
      setLoading(true);
      setResult(null);
      setAnswers({});
      setMarkedForReview({});
      setCurrentIndex(0);

      const res = await startPracticeSession(config);
      setSession(res);
    } catch (err) {
      console.error("Failed to start session:", err);
      alert("Could not start practice session. Please adjust your criteria.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = async (optionId) => {
    if (!session) return;
    const q = session.questions[currentIndex];
    const updatedAnswers = {
      ...answers,
      [currentIndex]: {
        selected_answer: optionId,
        time_spent_seconds: (answers[currentIndex]?.time_spent_seconds || 0) + 10,
      }
    };
    setAnswers(updatedAnswers);

    try {
      await recordPracticeAnswer(session.session_id, {
        questionId: q.question_id,
        selectedAnswer: optionId,
        timeSpentSeconds: updatedAnswers[currentIndex].time_spent_seconds,
        markedForReview: !!markedForReview[currentIndex],
      });
    } catch (err) {
      console.warn("Could not save answer selection:", err);
    }
  };

  const handleToggleReview = () => {
    const updated = {
      ...markedForReview,
      [currentIndex]: !markedForReview[currentIndex]
    };
    setMarkedForReview(updated);
  };

  const handleSubmit = async () => {
    if (!session) return;
    const confirm = window.confirm("Are you sure you want to submit your practice test and evaluate your score?");
    if (!confirm) return;

    try {
      setSubmitting(true);
      const res = await submitPracticeSession(session.session_id);
      setResult(res);
    } catch (err) {
      console.error("Submission failed:", err);
      alert("Submission error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSaveMistakeFromResult = async (qRes) => {
    try {
      await saveMistake({
        questionId: qRes.question.question_id,
        userAnswer: qRes.selected_answer,
        correctAnswer: qRes.correct_answer,
        mistakeTag: qRes.is_attempted ? 'Calculation Error' : 'Unattempted / Conceptual',
        userNotes: 'Saved from Practice Mode evaluation.',
      });
      alert(`Question ${qRes.question.question_id} bookmarked in Mistake Notebook.`);
    } catch (err) {
      console.error("Save mistake failed:", err);
    }
  };

  // 1. EVALUATION / RESULT VIEW
  if (result) {
    const scoreColor = result.score > (result.max_score * 0.6) ? 'text-qnx-olive' : 'text-qnx-terracotta';

    return (
      <div className="space-y-8 animate-fade-up max-w-4xl mx-auto pb-16">
        {/* Results Banner */}
        <div className="bg-white border border-qnx-border rounded-2xl p-6 sm:p-8 shadow-paper space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-qnx-border-light pb-6">
            <div className="space-y-1">
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-qnx-sage-soft text-qnx-olive border border-qnx-sage/30">
                Session Evaluation Complete
              </span>
              <h1 className="font-serif text-3xl font-bold text-qnx-text pt-1">
                Your Practice Test Summary
              </h1>
              <p className="text-xs text-qnx-muted">
                Official JEE Main Scheme (+4 Correct, -1 Incorrect MCQ, 0 Unattempted)
              </p>
            </div>

            <div className="text-right sm:border-l sm:border-qnx-border sm:pl-6">
              <p className="text-xs font-bold uppercase tracking-wider text-qnx-muted">Total Score</p>
              <p className={`font-serif text-4xl font-bold ${scoreColor}`}>
                {result.score} <span className="text-lg text-qnx-muted font-normal">/ {result.max_score}</span>
              </p>
            </div>
          </div>

          {/* Metric Stats Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <StatCard
              title="Accuracy"
              value={`${result.accuracy_percentage}%`}
              variant="olive"
              trend={result.accuracy_percentage >= 60 ? "Mastery Target" : "Review Needed"}
            />
            <StatCard
              title="Correct"
              value={result.correct_count}
              variant="sage"
              trend={`+${result.correct_count * 4} Marks`}
            />
            <StatCard
              title="Incorrect"
              value={result.incorrect_count}
              variant="terracotta"
              trend={`-${result.incorrect_count} Negative`}
            />
            <StatCard
              title="Unanswered"
              value={result.unattempted_count}
              variant="blue"
              trend="0 Penalty"
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-qnx-border-light">
            <button
              onClick={() => { setSession(null); setResult(null); }}
              className="px-5 py-2.5 bg-qnx-cream-paper hover:bg-qnx-cream border border-qnx-border text-qnx-text font-semibold text-xs rounded-xl transition-colors flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Configure New Session</span>
            </button>

            <Link
              to="/mistakes"
              className="px-5 py-2.5 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-xs rounded-xl shadow-paper-sm transition-all hover:-translate-y-0.5 flex items-center gap-1.5"
            >
              <span>Go to Mistake Notebook</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Individual Questions Breakdown */}
        <div className="space-y-4">
          <h2 className="font-serif text-2xl font-bold text-qnx-text">Detailed Answer Review</h2>
          {result.results.map((qRes, idx) => (
            <div
              key={idx}
              className={`bg-white border rounded-2xl p-6 shadow-paper-sm space-y-4 ${
                qRes.is_correct
                  ? 'border-qnx-sage'
                  : qRes.is_attempted
                  ? 'border-qnx-terracotta-soft'
                  : 'border-qnx-border'
              }`}
            >
              <div className="flex items-center justify-between border-b border-qnx-border-light pb-3">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-xs text-qnx-text">Q{idx + 1}.</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-qnx-sage-soft text-qnx-olive">
                    {qRes.question.subject}
                  </span>
                  <span className="text-xs text-qnx-muted">
                    {qRes.question.chapter} • {qRes.question.concept}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                      qRes.is_correct
                        ? 'bg-qnx-sage-soft text-qnx-olive'
                        : qRes.is_attempted
                        ? 'bg-qnx-terracotta-soft text-qnx-terracotta'
                        : 'bg-qnx-border-light text-qnx-muted'
                    }`}
                  >
                    {qRes.is_correct
                      ? '+4 Correct'
                      : qRes.is_attempted
                      ? '-1 Incorrect'
                      : 'Unattempted'}
                  </span>

                  <button
                    onClick={() => handleSaveMistakeFromResult(qRes)}
                    className="p-1 text-qnx-muted hover:text-qnx-terracotta transition-colors"
                    title="Bookmark in Mistakes"
                  >
                    <Bookmark className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Statement */}
              <div className="text-sm leading-relaxed text-qnx-text">
                <LatexRenderer content={qRes.question.content} />
              </div>

              {/* Diagram if present */}
              <QuestionDiagram imageUrls={qRes.question.image_urls} />

              {/* Options or Numerical Result */}
              {(!qRes.question.options || qRes.question.options.length === 0 || qRes.question.question_type === 'NUMERICAL') ? (
                <div className="p-4 rounded-xl bg-qnx-cream-paper border border-qnx-border space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-qnx-muted font-semibold">Your Entered Answer:</span>
                    <span className={`font-bold text-sm ${qRes.is_correct ? 'text-qnx-olive' : qRes.is_attempted ? 'text-qnx-terracotta' : 'text-qnx-muted'}`}>
                      {qRes.selected_answer ? qRes.selected_answer : 'Unattempted'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between border-t border-qnx-border-light pt-2">
                    <span className="text-qnx-muted font-semibold">Official Answer Key:</span>
                    <span className="font-bold text-sm text-qnx-olive">
                      {qRes.correct_answer || 'Verified Key'}
                    </span>
                  </div>
                </div>
              ) : (
                qRes.question.options && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-xs">
                    {qRes.question.options.map((opt) => {
                      const isSelected = qRes.selected_answer === opt.id;
                      const isCorrect = qRes.correct_answer === opt.id;

                      return (
                        <div
                          key={opt.id}
                          className={`p-3 rounded-lg border flex items-center gap-2 ${
                            isCorrect
                              ? 'bg-qnx-sage-soft border-qnx-olive font-bold text-qnx-olive'
                              : isSelected
                              ? 'bg-qnx-terracotta-soft border-qnx-terracotta text-qnx-terracotta'
                              : 'bg-qnx-cream-paper border-qnx-border text-qnx-text'
                          }`}
                        >
                          <span className="font-bold shrink-0">({opt.id})</span>
                          {opt.content && opt.content.trim() ? (
                            <LatexRenderer content={opt.content} inline={true} />
                          ) : (
                            <span className="text-qnx-muted italic text-xs">(See diagram in question)</span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )
              )}

              {/* Solution / AI Explain */}
              <div className="pt-3 border-t border-qnx-border-light flex items-center justify-between">
                <span className="text-xs text-qnx-muted">
                  Correct Answer: <strong>({qRes.correct_answer || 'Verified Key'})</strong>
                </span>
                <button
                  onClick={() => setExplainingQuestion(qRes.question)}
                  className="text-xs font-bold text-qnx-olive hover:underline flex items-center gap-1"
                >
                  <Sparkles className="w-3.5 h-3.5" /> Explain Solution →
                </button>
              </div>
            </div>
          ))}
        </div>

        {explainingQuestion && (
          <ExplanationModal
            question={explainingQuestion}
            onClose={() => setExplainingQuestion(null)}
          />
        )}
      </div>
    );
  }

  // 2. ACTIVE TEST WORKSPACE VIEW
  if (session && session.questions && session.questions.length > 0) {
    const currentQ = session.questions[currentIndex];
    const isAnswered = !!answers[currentIndex]?.selected_answer;
    const isMarked = !!markedForReview[currentIndex];

    return (
      <div className="space-y-6 animate-fade-up max-w-6xl mx-auto pb-16">
        {/* Active Test Top Bar */}
        <div className="bg-white border border-qnx-border rounded-2xl p-4 sm:p-5 shadow-paper-sm flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-qnx-olive text-white text-xs font-bold rounded-lg">
              Question {currentIndex + 1} of {session.total_questions}
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-qnx-olive hidden sm:inline">
              {currentQ.subject} • {currentQ.chapter}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <Timer initialMinutes={session.duration_minutes || 30} onTimeUp={handleSubmit} />
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="px-4 py-2 bg-qnx-terracotta hover:bg-[#B55F43] text-white text-xs font-bold rounded-xl shadow-paper-sm transition-all hover:-translate-y-0.5"
            >
              {submitting ? 'Submitting...' : 'Submit Test'}
            </button>
          </div>
        </div>

        {/* Test Center Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Question Area (8 cols) */}
          <div className="lg:col-span-8 bg-white border border-qnx-border rounded-2xl p-6 sm:p-8 shadow-paper space-y-6 flex flex-col justify-between">
            <div className="space-y-6">
              {/* Question Statement */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-qnx-muted border-b border-qnx-border-light pb-2">
                  <span>Concept: <strong>{currentQ.concept}</strong></span>
                  <span className="px-2 py-0.5 rounded bg-qnx-mustard-soft text-[#946E14] text-[10px] font-bold">
                    {currentQ.difficulty}
                  </span>
                </div>
                <div className="text-base font-normal text-qnx-text leading-relaxed pt-2">
                  <LatexRenderer content={currentQ.content} />
                </div>
              </div>

              {/* Question Diagram if present */}
              <QuestionDiagram imageUrls={currentQ.image_urls} />

              {/* Options or Numerical Input */}
              {(!currentQ.options || currentQ.options.length === 0 || currentQ.question_type === 'NUMERICAL') ? (
                <div className="space-y-3 p-5 bg-qnx-cream-paper border border-qnx-border rounded-xl">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold uppercase tracking-wider text-qnx-muted">
                      Enter Numerical Answer
                    </label>
                    {answers[currentIndex]?.selected_answer && (
                      <button
                        type="button"
                        onClick={() => handleSelectOption('')}
                        className="text-[11px] text-qnx-terracotta hover:underline font-semibold"
                      >
                        Clear Answer
                      </button>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <input
                      type="text"
                      inputMode="decimal"
                      placeholder="Type your numerical answer (e.g. 15, 0.75)..."
                      value={answers[currentIndex]?.selected_answer || ''}
                      onChange={(e) => handleSelectOption(e.target.value)}
                      className="w-full sm:w-80 px-4 py-3 bg-white border border-qnx-border rounded-xl text-base font-semibold text-qnx-text focus:outline-none focus:border-qnx-olive shadow-paper-sm"
                    />
                    {answers[currentIndex]?.selected_answer && (
                      <span className="text-xs font-semibold text-qnx-olive flex items-center gap-1 shrink-0">
                        <CheckCircle2 className="w-4 h-4" /> Saved
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-qnx-muted">
                    Accepts integer or decimal numbers as per official JEE Main evaluation keys.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <OptionSelector
                    options={currentQ.options}
                    selectedOption={answers[currentIndex]?.selected_answer || null}
                    onSelectOption={handleSelectOption}
                  />
                  {answers[currentIndex]?.selected_answer && (
                    <div className="flex justify-end">
                      <button
                        type="button"
                        onClick={() => handleSelectOption(null)}
                        className="text-[11px] text-qnx-terracotta hover:underline font-semibold"
                      >
                        Clear Selection
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Bottom Controls */}
            <div className="pt-6 border-t border-qnx-border-light flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <button
                  onClick={handleToggleReview}
                  className={`px-3 py-2 rounded-xl text-xs font-semibold border transition-colors ${
                    isMarked
                      ? 'bg-qnx-mustard-soft text-[#946E14] border-qnx-mustard'
                      : 'bg-qnx-cream-paper border-qnx-border text-qnx-text hover:bg-qnx-cream'
                  }`}
                >
                  {isMarked ? '★ Marked for Review' : '☆ Mark for Review'}
                </button>

                <button
                  onClick={() => setHintingQuestion(currentQ)}
                  className="px-3 py-2 bg-qnx-mustard-soft/60 hover:bg-qnx-mustard-soft text-[#946E14] font-semibold text-xs rounded-xl border border-qnx-mustard-soft transition-colors flex items-center gap-1"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Hint</span>
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button
                  disabled={currentIndex === 0}
                  onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
                  className="px-4 py-2 bg-qnx-cream-paper hover:bg-qnx-cream disabled:opacity-40 border border-qnx-border text-qnx-text font-semibold text-xs rounded-xl transition-colors flex items-center gap-1.5"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>

                <button
                  disabled={currentIndex === session.total_questions - 1}
                  onClick={() => setCurrentIndex(prev => Math.min(session.total_questions - 1, prev + 1))}
                  className="px-4 py-2 bg-qnx-olive hover:bg-qnx-olive-dark disabled:opacity-40 text-white font-semibold text-xs rounded-xl shadow-paper-sm transition-all flex items-center gap-1.5"
                >
                  <span>Next</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Right Palette Area (4 cols) */}
          <div className="lg:col-span-4 space-y-4">
            <QuestionPalette
              totalQuestions={session.total_questions}
              currentIndex={currentIndex}
              answers={answers}
              markedForReview={markedForReview}
              onSelectQuestion={(idx) => setCurrentIndex(idx)}
            />
          </div>
        </div>

        {hintingQuestion && (
          <HintDrawer
            question={hintingQuestion}
            onClose={() => setHintingQuestion(null)}
          />
        )}
      </div>
    );
  }

  const currentSubjectChapters = (DEFAULT_SYLLABUS_HIERARCHY.find(
    s => s.subject.toLowerCase() === (config.subject || '').toLowerCase()
  )?.chapters || []);

  const currentChapterConcepts = (currentSubjectChapters.find(
    c => c.chapter.toLowerCase() === (config.chapter || '').toLowerCase()
  )?.concepts || []);

  // 3. DEFAULT CONFIGURATION FORM VIEW
  return (
    <div className="space-y-8 animate-fade-up max-w-4xl mx-auto pb-16">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-sage-soft text-qnx-olive text-xs font-bold border border-qnx-sage/30">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Adaptive JEE Main Practice Workspace</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-qnx-text">
          Configure Your Practice Session
        </h1>
        <p className="text-sm text-qnx-muted max-w-2xl leading-relaxed">
          Select target subjects, chapters, and question counts. All questions are sourced directly from authentic JEE Main previous year papers without synthetic generation.
        </p>
      </div>

      <form onSubmit={handleStartSession} className="bg-white border border-qnx-border rounded-2xl p-6 sm:p-8 shadow-paper space-y-6">
        {/* Subject Choice */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-wider text-qnx-muted block">
            Select Subject
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {['All', 'Physics', 'Chemistry', 'Mathematics'].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setConfig({ ...config, subject: s, chapter: '', concept: '' })}
                className={`p-3.5 rounded-xl border text-left font-semibold text-xs transition-all ${
                  config.subject === s
                    ? 'border-qnx-olive bg-qnx-sage-soft text-qnx-olive shadow-paper-sm font-bold'
                    : 'border-qnx-border bg-qnx-cream-paper text-qnx-text hover:bg-qnx-cream'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Detailed Grid: Difficulty, Question Count, Chapter */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider text-qnx-muted block mb-1.5">
              Difficulty
            </label>
            <select
              value={config.difficulty}
              onChange={(e) => setConfig({ ...config, difficulty: e.target.value })}
              className="w-full px-3 py-2.5 bg-qnx-cream-paper border border-qnx-border rounded-xl font-medium text-qnx-text focus:outline-none focus:border-qnx-olive"
            >
              <option value="All">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider text-qnx-muted block mb-1.5">
              Number of Questions
            </label>
            <select
              value={config.num_questions}
              onChange={(e) => setConfig({ ...config, num_questions: parseInt(e.target.value, 10) })}
              className="w-full px-3 py-2.5 bg-qnx-cream-paper border border-qnx-border rounded-xl font-medium text-qnx-text focus:outline-none focus:border-qnx-olive"
            >
              <option value={5}>5 Questions (15 mins)</option>
              <option value={10}>10 Questions (30 mins)</option>
              <option value={15}>15 Questions (45 mins)</option>
              <option value={25}>25 Questions (75 mins)</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider text-qnx-muted block mb-1.5">
              Specific Chapter (Optional)
            </label>
            <input
              type="text"
              list="practice-chapters-list"
              placeholder={config.subject === 'Mathematics' ? 'e.g. Trigonometry & Statistics' : 'e.g. Rotational Motion'}
              value={config.chapter}
              onChange={(e) => setConfig({ ...config, chapter: e.target.value })}
              className="w-full px-3 py-2.5 bg-qnx-cream-paper border border-qnx-border rounded-xl text-xs text-qnx-text placeholder:text-qnx-muted focus:outline-none focus:border-qnx-olive"
            />
            <datalist id="practice-chapters-list">
              {currentSubjectChapters.map(ch => (
                <option key={ch.chapter} value={ch.chapter} />
              ))}
            </datalist>
          </div>

          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider text-qnx-muted block mb-1.5">
              Specific Concept (Optional)
            </label>
            <input
              type="text"
              list="practice-concepts-list"
              placeholder={config.subject === 'Mathematics' ? 'e.g. Trigonometric Equations' : 'e.g. Moment of Inertia'}
              value={config.concept}
              onChange={(e) => setConfig({ ...config, concept: e.target.value })}
              className="w-full px-3 py-2.5 bg-qnx-cream-paper border border-qnx-border rounded-xl text-xs text-qnx-text placeholder:text-qnx-muted focus:outline-none focus:border-qnx-olive"
            />
            <datalist id="practice-concepts-list">
              {currentChapterConcepts.map(c => (
                <option key={c} value={c} />
              ))}
            </datalist>
          </div>
        </div>

            {/* Concept / Paper specific notice if preset */}
            <div className="flex flex-wrap gap-2">
              {config.concept && (
                <div className="p-2.5 px-3 bg-qnx-mustard-soft border border-qnx-mustard-soft rounded-xl text-xs text-[#946E14] flex items-center justify-between gap-3">
                  <span>Filtered for Concept: <strong>{config.concept}</strong></span>
                  <button
                    type="button"
                    onClick={() => setConfig({ ...config, concept: '' })}
                    className="text-[11px] underline font-semibold"
                  >
                    Clear
                  </button>
                </div>
              )}

              {config.paper_id && (
                <div className="p-2.5 px-3 bg-qnx-sage-light border border-qnx-sage-soft rounded-xl text-xs text-qnx-olive flex items-center justify-between gap-3">
                  <span>Filtered for Paper: <strong>{config.paper_id}</strong></span>
                  <button
                    type="button"
                    onClick={() => setConfig({ ...config, paper_id: '' })}
                    className="text-[11px] underline font-semibold"
                  >
                    Clear Paper Lock
                  </button>
                </div>
              )}
            </div>

        {/* Submit Start */}
        <div className="pt-4 border-t border-qnx-border-light flex items-center justify-between">
          <span className="text-xs text-qnx-muted">Official +4 / -1 JEE Main marking rules apply.</span>
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-3.5 bg-qnx-olive hover:bg-qnx-olive-dark disabled:opacity-60 text-white font-bold text-sm rounded-xl shadow-paper hover:shadow-paper-lift transition-all hover:-translate-y-0.5 flex items-center gap-2"
          >
            {loading ? (
              <span>Preparing questions...</span>
            ) : (
              <>
                <span>Begin Test</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PracticePage;
