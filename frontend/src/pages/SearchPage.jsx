import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  Search, 
  Sparkles, 
  Filter, 
  RotateCcw, 
  BookOpen, 
  Bookmark,
  Layers,
  ArrowRight
} from 'lucide-react';
import { searchQuestions } from '../services/searchService';
import { saveMistake } from '../services/mistakeService';
import QuestionCard from '../components/questions/QuestionCard';
import QuestionFilterBar from '../components/questions/QuestionFilterBar';
import SearchBar from '../components/questions/SearchBar';
import { QuestionCardSkeleton } from '../components/common/LoadingSkeleton';
import EmptyState from '../components/common/EmptyState';
import ExplanationModal from '../components/ai/ExplanationModal';
import HintDrawer from '../components/ai/HintDrawer';

export const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const initialSubject = searchParams.get('subject') || 'All';
  const initialChapter = searchParams.get('chapter') || '';
  const initialConcept = searchParams.get('concept') || '';

  const [query, setQuery] = useState(initialQuery);
  const [filters, setFilters] = useState({
    subject: initialSubject,
    chapter: initialChapter || initialConcept,
    difficulty: 'All',
    year: 'All',
    session: 'All',
    shift: 'All',
    top_k: 100,
  });

  const [results, setResults] = useState([]);
  const [totalFound, setTotalFound] = useState(0);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchError, setSearchError] = useState(null);

  // AI Modal States
  const [explainingQuestion, setExplainingQuestion] = useState(null);
  const [hintingQuestion, setHintingQuestion] = useState(null);

  const executeSearch = useCallback(async (searchQueryText = query, currentFilters = filters) => {
    try {
      setLoading(true);
      setHasSearched(true);
      setSearchError(null);

      const params = {
        query: searchQueryText || 'JEE Main Questions',
        subject: currentFilters.subject,
        chapter: currentFilters.chapter,
        concept: currentFilters.concept,
        difficulty: currentFilters.difficulty,
        year: currentFilters.year,
        session: currentFilters.session,
        shift: currentFilters.shift,
        top_k: currentFilters.top_k || 100,
      };

      const response = await searchQuestions(params);
      setResults(response.results || []);
      setTotalFound(response.total_found || 0);

      // Sync URL
      const newParams = new URLSearchParams();
      if (searchQueryText) newParams.set('q', searchQueryText);
      if (currentFilters.subject && currentFilters.subject !== 'All') newParams.set('subject', currentFilters.subject);
      if (currentFilters.chapter) newParams.set('chapter', currentFilters.chapter);
      setSearchParams(newParams, { replace: true });

    } catch (err) {
      console.error("Search execution failed:", err);
      setResults([]);
      setTotalFound(0);
      setSearchError(err.message || "Failed to load questions. Please check connection.");
    } finally {
      setLoading(false);
    }
  }, [query, filters, setSearchParams]);

  useEffect(() => {
    executeSearch(initialQuery, {
      ...filters,
      subject: initialSubject,
      chapter: initialChapter || initialConcept,
    });
  }, []);

  const handleFilterChange = (key, value) => {
    const updated = { ...filters, [key]: value };
    setFilters(updated);
    executeSearch(query, updated);
  };

  const handleResetFilters = () => {
    const reset = {
      subject: 'All',
      chapter: '',
      difficulty: 'All',
      year: 'All',
      session: 'All',
      shift: 'All',
      top_k: 100,
    };
    setFilters(reset);
    setQuery('');
    setSearchError(null);
    executeSearch('', reset);
  };

  const handleToggleBookmark = async (q) => {
    try {
      await saveMistake({
        questionId: q.question_id,
        userNotes: 'Bookmarked from Question Explorer for review.',
        mistakeTag: 'Conceptual Gap',
      });
      alert(`Question ${q.question_id} saved to Mistake Notebook.`);
    } catch (err) {
      console.error("Bookmark error:", err);
    }
  };

  return (
    <div className="space-y-6 animate-fade-up max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-sage-soft text-qnx-olive text-xs font-bold border border-qnx-sage/30">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Semantic Question Discovery</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-qnx-text">
          Browse & Search Authentic PYQs
        </h1>
        <p className="text-sm text-qnx-muted max-w-2xl leading-relaxed">
          Search questions by conceptual phrasing, formula keywords, or chapter topics. Surfaces all relevant matching questions across all official shifts.
        </p>
      </div>

      {/* Search Bar */}
      <SearchBar
        value={query}
        onChange={setQuery}
        onSearch={(text) => executeSearch(text, filters)}
        loading={loading}
      />

      {/* Filters Bar */}
      <QuestionFilterBar
        filters={filters}
        onFilterChange={handleFilterChange}
        onResetFilters={handleResetFilters}
        totalResults={totalFound}
      />

      {/* Error Alert */}
      {searchError && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center justify-between">
          <span>Search notice: {searchError}</span>
          <button
            onClick={() => executeSearch(query, filters)}
            className="px-3 py-1 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Results Count Info */}
      {!loading && results.length > 0 && (
        <div className="flex items-center justify-between text-xs text-qnx-muted px-1">
          <span>Showing all <strong>{results.length}</strong> matching questions (ranked by relevance)</span>
        </div>
      )}

      {/* Results List */}
      {loading ? (
        <div className="space-y-4">
          <QuestionCardSkeleton />
          <QuestionCardSkeleton />
          <QuestionCardSkeleton />
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-4">
          {results.map((item) => (
            <QuestionCard
              key={item.question.question_id}
              question={item.question}
              similarityScore={item.similarity_score}
              onToggleBookmark={handleToggleBookmark}
              onExplain={(q) => setExplainingQuestion(q)}
              onHint={(q) => setHintingQuestion(q)}
            />
          ))}
        </div>
      ) : hasSearched && !searchError ? (
        <EmptyState
          title="No matching questions found"
          description="Try broadening your query keywords or clearing specific subject/shift filters."
          actionText="Clear All Filters"
          onAction={handleResetFilters}
        />
      ) : null}

      {/* AI Explanation Modal */}
      {explainingQuestion && (
        <ExplanationModal
          question={explainingQuestion}
          onClose={() => setExplainingQuestion(null)}
        />
      )}

      {/* AI Hint Drawer */}
      {hintingQuestion && (
        <HintDrawer
          question={hintingQuestion}
          onClose={() => setHintingQuestion(null)}
        />
      )}
    </div>
  );
};

export default SearchPage;
