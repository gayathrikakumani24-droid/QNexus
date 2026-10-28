import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  BookOpen, 
  Layers, 
  Search, 
  ArrowRight, 
  Sparkles, 
  Flame, 
  CheckCircle2,
  TrendingUp,
  FileText
} from 'lucide-react';
import { getSyllabusHierarchy } from '../services/knowledgeService';
import { DEFAULT_SYLLABUS_HIERARCHY } from '../data/syllabusHierarchy';
import { CardSkeleton } from '../components/common/LoadingSkeleton';
import EmptyState from '../components/common/EmptyState';

export const ChaptersPage = () => {
  const { subject: routeSubject } = useParams();
  const [hierarchy, setHierarchy] = useState(DEFAULT_SYLLABUS_HIERARCHY);
  const [loading, setLoading] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState(routeSubject || 'Physics');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    let isMounted = true;
    const fetchHierarchy = async () => {
      try {
        const res = await getSyllabusHierarchy();
        if (isMounted) {
          const rawHierarchy = res?.hierarchy || [];
          if (rawHierarchy.length > 0) {
            setHierarchy(rawHierarchy);
          }
        }
      } catch (err) {
        console.warn("Using offline syllabus hierarchy:", err);
      }
    };

    fetchHierarchy();
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
    if (routeSubject) {
      const match = ['Physics', 'Chemistry', 'Mathematics'].find(
        s => s.toLowerCase() === routeSubject.toLowerCase()
      );
      if (match) setSelectedSubject(match);
    }
  }, [routeSubject]);

  const activeSubjectNode = hierarchy.find(h => h.subject.toLowerCase() === selectedSubject.toLowerCase()) || hierarchy[0];
  const chaptersList = activeSubjectNode?.chapters || [];
  const totalConcepts = chaptersList.reduce((acc, ch) => acc + (ch.concepts?.length || 0), 0);

  const filteredChapters = chaptersList.filter(ch =>
    ch.chapter.toLowerCase().includes(searchQuery.toLowerCase()) ||
    ch.concepts.some(c => c.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-8 animate-fade-up max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-sage-soft text-qnx-olive text-xs font-bold border border-qnx-sage/30">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Complete Syllabus Taxonomy</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2">
          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-qnx-text">
            Chapter & Concept Discovery
          </h1>
          <span className="text-xs font-semibold text-qnx-olive bg-qnx-sage-soft px-3 py-1 rounded-full border border-qnx-sage/30 self-start sm:self-auto">
            {chaptersList.length} Chapters • {totalConcepts} Tested Concepts
          </span>
        </div>
        <p className="text-sm text-qnx-muted max-w-2xl leading-relaxed">
          Navigate the entire JEE Main syllabus hierarchy. Explore topic frequencies, core concepts, and tested PYQs by subject.
        </p>
      </div>

      {/* Subject Selector Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-qnx-border pb-4">
        <div className="flex items-center gap-3">
          {['Physics', 'Chemistry', 'Mathematics'].map((subj) => {
            const count = hierarchy.find(h => h.subject.toLowerCase() === subj.toLowerCase())?.chapters?.length || 0;
            const isSelected = selectedSubject.toLowerCase() === subj.toLowerCase();
            return (
              <button
                key={subj}
                onClick={() => setSelectedSubject(subj)}
                className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${
                  isSelected
                    ? 'bg-qnx-olive text-white shadow-paper-sm'
                    : 'bg-white border border-qnx-border text-qnx-text hover:bg-qnx-cream-paper'
                }`}
              >
                <span>{subj}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${
                  isSelected ? 'bg-white/20 text-white' : 'bg-qnx-cream-paper text-qnx-muted border border-qnx-border'
                }`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-qnx-muted" />
          <input
            type="text"
            placeholder="Search chapter or concept..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white border border-qnx-border rounded-lg text-xs text-qnx-text placeholder:text-qnx-muted focus:outline-none focus:border-qnx-olive shadow-paper-sm"
          />
        </div>
      </div>

      {/* Chapters Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : filteredChapters.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredChapters.map((ch, idx) => (
            <div
              key={idx}
              className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-1 space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-qnx-sage-soft text-qnx-olive border border-qnx-sage/30">
                    {selectedSubject}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-qnx-mustard-soft text-[#946E14] border border-qnx-mustard-soft">
                    {ch.concepts.length} Concepts
                  </span>
                </div>

                <h3 className="font-serif text-xl font-bold text-qnx-text">
                  {ch.chapter}
                </h3>

                {/* Concepts list */}
                <div className="space-y-1.5 pt-1">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-qnx-muted">Tested Concepts</p>
                  <div className="flex flex-wrap gap-1.5">
                    {ch.concepts.map((conc, cIdx) => (
                      <Link
                        key={cIdx}
                        to={`/practice?subject=${selectedSubject}&chapter=${encodeURIComponent(ch.chapter)}&concept=${encodeURIComponent(conc)}`}
                        title={`Practice ${conc} questions`}
                        className="px-2 py-0.5 bg-qnx-cream-paper hover:bg-qnx-sage-soft hover:text-qnx-olive hover:border-qnx-sage border border-qnx-border text-qnx-text text-[11px] rounded transition-colors flex items-center gap-1"
                      >
                        <span>{conc}</span>
                        <span className="text-[9px] text-qnx-olive font-bold">▶</span>
                      </Link>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-qnx-border-light flex items-center justify-between">
                <Link
                  to={`/search?subject=${selectedSubject}&chapter=${encodeURIComponent(ch.chapter)}`}
                  className="text-xs font-bold text-qnx-olive hover:underline flex items-center gap-1"
                >
                  Explore PYQs →
                </Link>

                <Link
                  to={`/practice?subject=${selectedSubject}&chapter=${encodeURIComponent(ch.chapter)}`}
                  className="px-3 py-1.5 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-xs rounded-lg shadow-paper-sm transition-all hover:-translate-y-0.5"
                >
                  Practice Chapter
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No chapters match your search"
          description="Try searching for another topic or switch to a different subject."
          actionText="Clear Search"
          onAction={() => setSearchQuery('')}
        />
      )}
    </div>
  );
};

export default ChaptersPage;
