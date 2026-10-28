import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Search, 
  Calendar, 
  Clock, 
  BookOpen, 
  ArrowRight, 
  CheckCircle2, 
  Filter,
  Layers,
  Sparkles
} from 'lucide-react';
import apiClient from '../services/apiClient';
import { ALL_PAPERS } from '../data/papersData';
import { CardSkeleton } from '../components/common/LoadingSkeleton';
import EmptyState from '../components/common/EmptyState';

export const PapersPage = () => {
  const [papers, setPapers] = useState(ALL_PAPERS);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedYear, setSelectedYear] = useState('All');
  const [selectedShift, setSelectedShift] = useState('All');
  const [selectedSession, setSelectedSession] = useState('All');

  useEffect(() => {
    let isMounted = true;
    const fetchPapers = async () => {
      try {
        const response = await apiClient.get('/papers', { params: { limit: 100 } });
        if (isMounted && response.data && response.data.length > 0) {
          setPapers(response.data);
        }
      } catch (err) {
        // Graceful fallback to verified canonical list of all 27 papers
        console.warn("Using offline / canonical papers list:", err);
      }
    };

    fetchPapers();
    return () => { isMounted = false; };
  }, []);

  const filteredPapers = papers.filter(p => {
    const paperYear = String(p.year || '');
    const matchesYear = selectedYear === 'All' || paperYear === selectedYear;
    const matchesSearch = (p.paper_id || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (p.date || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (p.shift || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesShift = selectedShift === 'All' || (p.shift || '').toLowerCase().includes(selectedShift.toLowerCase());
    const matchesSession = selectedSession === 'All' || (p.session || '').toLowerCase() === selectedSession.toLowerCase();
    return matchesYear && matchesSearch && matchesShift && matchesSession;
  });

  const yearCounts = {
    All: papers.length,
    '2026': papers.filter(p => p.year === 2026).length,
    '2025': papers.filter(p => p.year === 2025).length,
    '2024': papers.filter(p => p.year === 2024).length,
  };

  return (
    <div className="space-y-8 animate-fade-up max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-sage-soft text-qnx-olive text-xs font-bold border border-qnx-sage/30">
          <FileText className="w-3.5 h-3.5" />
          <span>Authentic Exam Papers</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2">
          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-qnx-text">
            Browse Shift-wise Previous Year Papers
          </h1>
          <span className="text-xs font-semibold text-qnx-olive bg-qnx-sage-soft px-3 py-1 rounded-full border border-qnx-sage/30 self-start sm:self-auto">
            {filteredPapers.length} of {papers.length} Papers Available
          </span>
        </div>
        <p className="text-sm text-qnx-muted max-w-2xl leading-relaxed">
          Explore complete shift question sets extracted directly from official NTA JEE Main question papers across 2024, 2025, and 2026.
        </p>
      </div>

      {/* Year Selection Tabs */}
      <div className="flex items-center gap-2 border-b border-qnx-border pb-3">
        {['All', '2026', '2025', '2024'].map((year) => {
          const isSelected = selectedYear === year;
          const label = year === 'All' ? 'All Years' : `JEE Main ${year}`;
          const count = yearCounts[year] || 0;
          return (
            <button
              key={year}
              onClick={() => setSelectedYear(year)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                isSelected
                  ? 'bg-qnx-olive text-white shadow-paper-sm'
                  : 'bg-white border border-qnx-border text-qnx-text hover:bg-qnx-cream-paper'
              }`}
            >
              <span>{label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                isSelected ? 'bg-white/25 text-white' : 'bg-qnx-cream-paper text-qnx-muted border border-qnx-border'
              }`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white border border-qnx-border rounded-xl p-4 shadow-paper-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-qnx-muted" />
          <input
            type="text"
            placeholder="Search date, shift or paper ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-qnx-cream-paper border border-qnx-border rounded-lg text-xs text-qnx-text placeholder:text-qnx-muted focus:outline-none focus:border-qnx-olive"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <select
            value={selectedSession}
            onChange={(e) => setSelectedSession(e.target.value)}
            className="px-3 py-2 bg-qnx-cream-paper border border-qnx-border rounded-lg text-xs font-semibold text-qnx-text focus:outline-none focus:border-qnx-olive"
          >
            <option value="All">All Sessions</option>
            <option value="January">January Session</option>
            <option value="April">April Session</option>
          </select>

          <select
            value={selectedShift}
            onChange={(e) => setSelectedShift(e.target.value)}
            className="px-3 py-2 bg-qnx-cream-paper border border-qnx-border rounded-lg text-xs font-semibold text-qnx-text focus:outline-none focus:border-qnx-olive"
          >
            <option value="All">All Shifts</option>
            <option value="Shift 1">Shift 1 (Morning)</option>
            <option value="Shift 2">Shift 2 (Evening)</option>
          </select>
        </div>
      </div>

      {/* Papers Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : filteredPapers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPapers.map((paper) => (
            <div
              key={paper.paper_id}
              className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-1 space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-qnx-sage-soft text-qnx-olive border border-qnx-sage/30">
                    {paper.exam} {paper.year}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-qnx-cream text-qnx-muted border border-qnx-border">
                    {paper.status}
                  </span>
                </div>

                <h3 className="font-serif text-xl font-bold text-qnx-text">
                  {paper.date} • {paper.shift}
                </h3>

                <div className="space-y-1.5 text-xs text-qnx-muted pt-1">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-3.5 h-3.5 text-qnx-sage" />
                    <span>Session: <strong>{paper.session}</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-3.5 h-3.5 text-qnx-sage" />
                    <span>Questions: <strong>{paper.total_questions || 90} Questions (PCM)</strong></span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-qnx-border-light flex items-center justify-between gap-2">
                <Link
                  to={`/papers/${paper.paper_id}`}
                  className="px-3 py-1.5 bg-qnx-cream-paper hover:bg-qnx-cream border border-qnx-border text-qnx-text font-semibold text-xs rounded-lg transition-colors"
                >
                  View Paper
                </Link>

                <Link
                  to={`/practice?paper_id=${paper.paper_id}`}
                  className="px-3.5 py-1.5 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-xs rounded-lg shadow-paper-sm transition-all hover:-translate-y-0.5 flex items-center gap-1.5"
                >
                  <span>Practice Paper</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No papers match your filter"
          description="Try selecting a different session or shift."
          actionText="Reset Filters"
          onAction={() => {
            setSearchQuery('');
            setSelectedShift('All');
            setSelectedSession('All');
          }}
        />
      )}
    </div>
  );
};

export default PapersPage;
