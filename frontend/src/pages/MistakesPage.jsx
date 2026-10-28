import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  AlertCircle, 
  Bookmark, 
  Search, 
  Trash2, 
  Edit3, 
  CheckCircle2, 
  Sparkles, 
  ArrowRight, 
  RotateCcw,
  Tag,
  BookOpen,
  Filter
} from 'lucide-react';
import { 
  listMistakes, 
  updateMistake, 
  deleteMistake 
} from '../services/mistakeService';
import LatexRenderer from '../components/common/LatexRenderer';
import { QuestionCardSkeleton } from '../components/common/LoadingSkeleton';
import EmptyState from '../components/common/EmptyState';
import ExplanationModal from '../components/ai/ExplanationModal';
import HintDrawer from '../components/ai/HintDrawer';

export const MistakesPage = () => {
  const [mistakes, setMistakes] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Filters
  const [subjectFilter, setSubjectFilter] = useState('All');
  const [tagFilter, setTagFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  // Editing Note
  const [editingId, setEditingId] = useState(null);
  const [editingNoteText, setEditingNoteText] = useState('');
  const [editingTag, setEditingTag] = useState('');

  // AI Modals
  const [explainingQuestion, setExplainingQuestion] = useState(null);
  const [hintingQuestion, setHintingQuestion] = useState(null);

  const navigate = useNavigate();

  const fetchMistakes = async () => {
    try {
      setLoading(true);
      const params = {
        subject: subjectFilter !== 'All' ? subjectFilter : null,
        mistakeTag: tagFilter !== 'All' ? tagFilter : null,
        reviewStatus: statusFilter !== 'All' ? statusFilter : null,
      };
      const res = await listMistakes(params);
      setMistakes(res.mistakes || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error("Failed to load mistakes:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMistakes();
  }, [subjectFilter, tagFilter, statusFilter]);

  const handleDelete = async (mistakeId) => {
    if (!window.confirm("Remove this question from your mistake notebook?")) return;
    try {
      await deleteMistake(mistakeId);
      setMistakes(prev => prev.filter(m => m.mistake_id !== mistakeId));
      setTotal(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error("Delete mistake failed:", err);
    }
  };

  const handleStartEditing = (m) => {
    setEditingId(m.mistake_id);
    setEditingNoteText(m.user_notes || '');
    setEditingTag(m.mistake_tag || 'Conceptual Gap');
  };

  const handleSaveEdit = async (mistakeId) => {
    try {
      await updateMistake(mistakeId, {
        user_notes: editingNoteText,
        mistake_tag: editingTag,
      });
      setMistakes(prev => prev.map(m => m.mistake_id === mistakeId ? {
        ...m,
        user_notes: editingNoteText,
        mistake_tag: editingTag
      } : m));
      setEditingId(null);
    } catch (err) {
      console.error("Update mistake failed:", err);
    }
  };

  const handleStatusChange = async (mistakeId, newStatus) => {
    try {
      await updateMistake(mistakeId, { review_status: newStatus });
      setMistakes(prev => prev.map(m => m.mistake_id === mistakeId ? {
        ...m,
        review_status: newStatus
      } : m));
    } catch (err) {
      console.error("Status update failed:", err);
    }
  };

  const handlePracticeMyMistakes = () => {
    const questionIds = mistakes.map(m => m.question_id).filter(Boolean);
    if (questionIds.length === 0) {
      alert("No mistakes available to practice.");
      return;
    }
    navigate(`/practice?practice_mistakes=true`);
  };

  const tags = ['All', 'Conceptual Gap', 'Calculation Error', 'Time Management', 'Formula Recall'];
  const statuses = ['All', 'Needs Review', 'Reviewed', 'Mastered'];

  return (
    <div className="space-y-8 animate-fade-up max-w-5xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-terracotta-soft text-qnx-terracotta text-xs font-bold border border-qnx-terracotta-soft">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Spaced Repetition Notebook</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-qnx-text">
            Mistake Notebook ({total})
          </h1>
          <p className="text-xs text-qnx-muted">
            Track incorrect answers, record root-cause tags, and retry until mastered.
          </p>
        </div>

        {mistakes.length > 0 && (
          <button
            onClick={handlePracticeMyMistakes}
            className="px-5 py-2.5 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-xs rounded-xl shadow-paper-sm transition-all hover:-translate-y-0.5 flex items-center gap-2 self-start sm:self-auto"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Practice My Mistakes ({mistakes.length})</span>
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="bg-white border border-qnx-border rounded-xl p-4 shadow-paper-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          {/* Subject Pills */}
          <div className="flex items-center gap-2">
            {['All', 'Physics', 'Chemistry', 'Mathematics'].map((s) => (
              <button
                key={s}
                onClick={() => setSubjectFilter(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  subjectFilter === s
                    ? 'bg-qnx-olive text-white shadow-paper-sm'
                    : 'bg-qnx-cream-paper border border-qnx-border text-qnx-text hover:bg-qnx-cream'
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Tag & Status Dropdowns */}
          <div className="flex items-center gap-2 text-xs">
            <select
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-qnx-cream-paper border border-qnx-border rounded-lg text-qnx-text font-medium focus:outline-none focus:border-qnx-olive"
            >
              {tags.map(t => (
                <option key={t} value={t}>{t === 'All' ? 'All Tags' : t}</option>
              ))}
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-qnx-cream-paper border border-qnx-border rounded-lg text-qnx-text font-medium focus:outline-none focus:border-qnx-olive"
            >
              {statuses.map(st => (
                <option key={st} value={st}>{st === 'All' ? 'All Status' : st}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Mistake Records List */}
      {loading ? (
        <div className="space-y-4">
          <QuestionCardSkeleton />
          <QuestionCardSkeleton />
        </div>
      ) : mistakes.length > 0 ? (
        <div className="space-y-5">
          {mistakes.map((m) => {
            const q = m.question;
            const isEditing = editingId === m.mistake_id;

            return (
              <div
                key={m.mistake_id}
                className="bg-white border border-qnx-border rounded-2xl p-6 shadow-paper-sm space-y-4 hover:shadow-paper transition-all"
              >
                {/* Header */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-qnx-border-light pb-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-qnx-sage-soft text-qnx-olive border border-qnx-sage/30">
                      {m.subject || q?.subject}
                    </span>
                    <span className="text-xs font-semibold text-qnx-muted">
                      {m.chapter || q?.chapter} • {m.concept || q?.concept}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-qnx-terracotta-soft text-qnx-terracotta border border-qnx-terracotta-soft">
                      {m.mistake_tag}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Status Pill Selector */}
                    <select
                      value={m.review_status}
                      onChange={(e) => handleStatusChange(m.mistake_id, e.target.value)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${
                        m.review_status === 'Mastered'
                          ? 'bg-qnx-sage-soft text-qnx-olive border-qnx-sage/40'
                          : m.review_status === 'Reviewed'
                          ? 'bg-qnx-blue-soft text-[#38679E] border-qnx-blue-soft'
                          : 'bg-qnx-mustard-soft text-[#946E14] border-qnx-mustard-soft'
                      }`}
                    >
                      <option value="Needs Review">Needs Review</option>
                      <option value="Reviewed">Reviewed</option>
                      <option value="Mastered">Mastered</option>
                    </select>

                    <button
                      onClick={() => handleStartEditing(m)}
                      className="p-1.5 text-qnx-muted hover:text-qnx-olive rounded-lg hover:bg-qnx-cream-paper transition-colors"
                      title="Edit Notes & Tag"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => handleDelete(m.mistake_id)}
                      className="p-1.5 text-qnx-muted hover:text-qnx-terracotta rounded-lg hover:bg-qnx-terracotta-soft/50 transition-colors"
                      title="Remove from Notebook"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Question Statement */}
                {q && (
                  <div className="text-sm font-normal text-qnx-text leading-relaxed">
                    <LatexRenderer content={q.content} />
                  </div>
                )}

                {/* Answer Differential Box */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-qnx-terracotta-light border border-qnx-terracotta-soft rounded-xl">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-qnx-terracotta block">
                      Your Recorded Attempt:
                    </span>
                    <span className="font-bold text-qnx-text">
                      {m.user_answer ? `Option (${m.user_answer})` : 'Unattempted / Left Blank'}
                    </span>
                  </div>

                  <div className="p-3 bg-qnx-sage-light border border-qnx-sage-soft rounded-xl">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-qnx-olive block">
                      Official Verified Key:
                    </span>
                    <span className="font-bold text-qnx-olive">
                      {m.correct_answer ? `Option (${m.correct_answer})` : 'Verified Solution Key'}
                    </span>
                  </div>
                </div>

                {/* Student Notes Editor or Display */}
                {isEditing ? (
                  <div className="p-4 bg-qnx-cream-paper border border-qnx-border rounded-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-qnx-text">Edit Student Reflection</span>
                      <select
                        value={editingTag}
                        onChange={(e) => setEditingTag(e.target.value)}
                        className="px-2 py-1 bg-white border border-qnx-border rounded text-xs"
                      >
                        <option value="Conceptual Gap">Conceptual Gap</option>
                        <option value="Calculation Error">Calculation Error</option>
                        <option value="Time Management">Time Management</option>
                        <option value="Formula Recall">Formula Recall</option>
                      </select>
                    </div>

                    <textarea
                      rows={2}
                      value={editingNoteText}
                      onChange={(e) => setEditingNoteText(e.target.value)}
                      placeholder="Write your reflection e.g. 'Remembered minus sign in cross product incorrectly.'"
                      className="w-full p-2.5 bg-white border border-qnx-border rounded-lg text-xs text-qnx-text focus:outline-none focus:border-qnx-olive"
                    />

                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => setEditingId(null)}
                        className="px-3 py-1 bg-white border border-qnx-border text-xs rounded-lg"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleSaveEdit(m.mistake_id)}
                        className="px-4 py-1 bg-qnx-olive text-white text-xs font-bold rounded-lg"
                      >
                        Save Note
                      </button>
                    </div>
                  </div>
                ) : m.user_notes ? (
                  <div className="p-3.5 bg-qnx-cream-paper border border-qnx-border rounded-xl text-xs space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-qnx-muted block">
                      Student Reflection Note:
                    </span>
                    <p className="text-qnx-text italic">"{m.user_notes}"</p>
                  </div>
                ) : null}

                {/* Footer Action Links */}
                <div className="pt-3 border-t border-qnx-border-light flex flex-wrap items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-3">
                    {q && (
                      <button
                        onClick={() => setExplainingQuestion(q)}
                        className="text-xs font-bold text-qnx-olive hover:underline flex items-center gap-1"
                      >
                        <Sparkles className="w-3.5 h-3.5" /> Explain Solution
                      </button>
                    )}
                    {q && (
                      <button
                        onClick={() => setHintingQuestion(q)}
                        className="text-xs font-bold text-[#946E14] hover:underline flex items-center gap-1"
                      >
                        Get Hint
                      </button>
                    )}
                  </div>

                  <Link
                    to={`/question/${m.question_id}`}
                    className="text-xs font-bold text-qnx-olive hover:underline flex items-center gap-1"
                  >
                    <span>Open Question View</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="Your Mistake Notebook is empty"
          description="When you practice and answer incorrectly, save questions here to build your personalized review deck."
          actionText="Start Practice Session"
          actionLink="/practice"
        />
      )}

      {explainingQuestion && (
        <ExplanationModal
          question={explainingQuestion}
          onClose={() => setExplainingQuestion(null)}
        />
      )}

      {hintingQuestion && (
        <HintDrawer
          question={hintingQuestion}
          onClose={() => setHintingQuestion(null)}
        />
      )}
    </div>
  );
};

export default MistakesPage;
