import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  BookOpen, 
  Calendar, 
  Clock, 
  FileText, 
  CheckCircle2, 
  Layers, 
  ArrowRight,
  Sparkles
} from 'lucide-react';
import apiClient from '../services/apiClient';
import QuestionCard from '../components/questions/QuestionCard';
import { QuestionCardSkeleton } from '../components/common/LoadingSkeleton';
import EmptyState from '../components/common/EmptyState';

export const PaperDetailPage = () => {
  const { id } = useParams();
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState('All');

  useEffect(() => {
    let isMounted = true;
    const fetchPaperQuestions = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/questions', {
          params: { paper_id: id, limit: 100 }
        });
        if (isMounted) {
          setQuestions(response.data || []);
        }
      } catch (err) {
        console.error("Failed to load paper questions:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchPaperQuestions();
    return () => { isMounted = false; };
  }, [id]);

  const filteredQuestions = selectedSubject === 'All'
    ? questions
    : questions.filter(q => (q.subject || '').toLowerCase() === selectedSubject.toLowerCase());

  return (
    <div className="space-y-8 animate-fade-up max-w-5xl mx-auto pb-12">
      {/* Back Button */}
      <Link
        to="/papers"
        className="inline-flex items-center gap-2 text-xs font-semibold text-qnx-muted hover:text-qnx-olive transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to All Papers</span>
      </Link>

      {/* Paper Header Banner */}
      <div className="bg-white border border-qnx-border rounded-2xl p-6 sm:p-8 shadow-paper-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-sage-soft text-qnx-olive text-xs font-bold border border-qnx-sage/30">
            <span>JEE Main {questions[0]?.year || (id?.includes('2024') ? '2024' : id?.includes('2025') ? '2025' : '2026')} Shift Paper</span>
          </div>
          <h1 className="font-serif text-3xl font-bold text-qnx-text">
            {id?.replace(/_/g, ' ')}
          </h1>
          <div className="flex flex-wrap items-center gap-4 text-xs text-qnx-muted pt-1">
            <span><strong>Exam:</strong> JEE Main</span>
            <span>•</span>
            <span><strong>Questions:</strong> {questions.length || 90} Authenticated Problems</span>
            <span>•</span>
            <span><strong>Marking:</strong> +4 / -1 JEE Scheme</span>
          </div>
        </div>

        <div>
          <Link
            to={`/practice?paper_id=${id}`}
            className="px-6 py-3 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-sm rounded-xl shadow-paper transition-all hover:-translate-y-0.5 flex items-center gap-2"
          >
            <BookOpen className="w-4 h-4" />
            <span>Practice Full Paper</span>
          </Link>
        </div>
      </div>

      {/* Subject Filter Pills */}
      <div className="flex items-center justify-between border-b border-qnx-border pb-3">
        <div className="flex items-center gap-2">
          {['All', 'Physics', 'Chemistry', 'Mathematics'].map((subj) => (
            <button
              key={subj}
              onClick={() => setSelectedSubject(subj)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedSubject === subj
                  ? 'bg-qnx-olive text-white shadow-paper-sm'
                  : 'bg-white border border-qnx-border text-qnx-text hover:bg-qnx-cream-paper'
              }`}
            >
              {subj}
            </button>
          ))}
        </div>
        <span className="text-xs text-qnx-muted">
          Showing {filteredQuestions.length} Questions
        </span>
      </div>

      {/* Question List */}
      {loading ? (
        <div className="space-y-4">
          <QuestionCardSkeleton />
          <QuestionCardSkeleton />
          <QuestionCardSkeleton />
        </div>
      ) : filteredQuestions.length > 0 ? (
        <div className="space-y-4">
          {filteredQuestions.map((q) => (
            <QuestionCard key={q.question_id} question={q} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No questions in this category"
          description="Try switching subjects or practicing the complete shift set."
          actionText="Show All Questions"
          onAction={() => setSelectedSubject('All')}
        />
      )}
    </div>
  );
};

export default PaperDetailPage;
