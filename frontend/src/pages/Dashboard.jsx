import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  BookOpen, 
  Search, 
  TrendingUp, 
  Sparkles, 
  AlertCircle, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  FileText,
  Target,
  Layers,
  ChevronRight,
  Flame,
  Award
} from 'lucide-react';
import StatCard from '../components/common/StatCard';
import { getAnalyticsSummary, getWeaknesses } from '../services/analyticsService';
import { getRecommendations } from '../services/recommendationService';
import { listMistakes } from '../services/mistakeService';
import LatexRenderer from '../components/common/LatexRenderer';

export const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [weaknesses, setWeaknesses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [mistakesCount, setMistakesCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [sumRes, weakRes, recRes, mistRes] = await Promise.allSettled([
          getAnalyticsSummary(),
          getWeaknesses(1, 75.0),
          getRecommendations({ limit: 4 }),
          listMistakes({ limit: 1 }),
        ]);

        if (isMounted) {
          if (sumRes.status === 'fulfilled') setSummary(sumRes.value);
          if (weakRes.status === 'fulfilled') setWeaknesses(weakRes.value?.weaknesses || []);
          if (recRes.status === 'fulfilled') setRecommendations(recRes.value?.recommendations || []);
          if (mistRes.status === 'fulfilled') setMistakesCount(mistRes.value?.total || 0);
        }
      } catch (err) {
        console.error("Dashboard data fetch error:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchDashboardData();
    return () => { isMounted = false; };
  }, []);

  const totalAttempted = summary?.attempted || 0;
  const overallAccuracy = summary?.overall_accuracy || 0;
  const avgTime = summary?.average_time_seconds ? `${summary.average_time_seconds}s` : '--';

  return (
    <div className="space-y-8 animate-fade-up max-w-6xl mx-auto pb-12">
      {/* Welcome Banner */}
      <div className="bg-white border border-qnx-border rounded-2xl p-6 sm:p-8 shadow-paper-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-sage-soft text-qnx-olive text-xs font-bold border border-qnx-sage/30">
            <span>JEE Main 2026 Shift Intelligence</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-qnx-text">
            Welcome to your study dashboard.
          </h1>
          <p className="text-sm text-qnx-muted leading-relaxed">
            Practice authentic shift questions, detect recurring conceptual patterns, and track your syllabus progress.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Link
            to="/practice"
            className="px-5 py-2.5 bg-qnx-olive hover:bg-qnx-olive-dark text-[#F7F4EA] text-sm font-semibold rounded-xl shadow-paper transition-all hover:-translate-y-0.5 flex items-center gap-2"
          >
            <BookOpen className="w-4 h-4" />
            <span>Start Practice</span>
          </Link>
          <Link
            to="/search"
            className="px-4 py-2.5 bg-qnx-cream-paper hover:bg-qnx-cream border border-qnx-border text-qnx-text text-sm font-semibold rounded-xl transition-colors flex items-center gap-2"
          >
            <Search className="w-4 h-4" />
            <span>Search PYQs</span>
          </Link>
        </div>
      </div>

      {/* Semantic Key Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Overall Accuracy"
          value={`${overallAccuracy}%`}
          subtitle={totalAttempted > 0 ? `${summary?.correct || 0} correct / ${totalAttempted} attempted` : "No attempts yet"}
          variant="olive"
          icon={Target}
          trend={overallAccuracy >= 60 ? "🟢 Good Foundation" : "🟠 Needs Attention"}
        />
        <StatCard
          title="Questions Practiced"
          value={totalAttempted}
          subtitle={`${summary?.total_sessions || 0} test sessions recorded`}
          variant="sage"
          icon={Award}
          trend="Real PYQ Attempts"
        />
        <StatCard
          title="Avg Speed / Question"
          value={avgTime}
          subtitle="Target: under 120s per question"
          variant="blue"
          icon={Clock}
          trend="JEE Main Pace"
        />
        <StatCard
          title="Mistake Notebook"
          value={mistakesCount}
          subtitle="Bookmarked for review"
          variant="terracotta"
          icon={AlertCircle}
          trend={mistakesCount > 0 ? "Review Required" : "Zero Pending"}
        />
      </div>

      {/* Two Column Section: Weak Areas & Recommended Practice */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (7 cols): Recommended Diagnostic Questions */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-qnx-olive" />
              <h2 className="font-serif text-2xl font-bold text-qnx-text">Targeted Recommendations</h2>
            </div>
            <Link to="/search" className="text-xs font-bold text-qnx-olive hover:underline flex items-center gap-1">
              Browse All →
            </Link>
          </div>

          <div className="space-y-3">
            {recommendations.length > 0 ? (
              recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="bg-white border border-qnx-border rounded-xl p-5 shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-0.5 space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-qnx-sage-soft text-qnx-olive border border-qnx-sage/30">
                        {rec.subject}
                      </span>
                      <span className="text-xs font-medium text-qnx-muted">
                        {rec.chapter} • {rec.concept}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-qnx-mustard-soft text-[#946E14] border border-qnx-mustard-soft">
                      {rec.difficulty}
                    </span>
                  </div>

                  {rec.question && (
                    <div className="text-xs text-qnx-text line-clamp-2">
                      <LatexRenderer content={rec.question.content} inline={true} />
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-2 border-t border-qnx-border-light text-xs">
                    <p className="text-[11px] text-qnx-muted italic">
                      {rec.reason}
                    </p>
                    <Link
                      to={`/question/${rec.question_id}`}
                      className="text-xs font-bold text-qnx-olive hover:underline flex items-center gap-1 ml-2 shrink-0"
                    >
                      Solve →
                    </Link>
                  </div>
                </div>
              ))
            ) : (
              <div className="bg-white border border-qnx-border rounded-xl p-6 text-center shadow-paper-sm">
                <p className="text-xs text-qnx-muted">Complete a practice session to generate personalized recommendations.</p>
                <Link to="/practice" className="inline-block mt-3 px-4 py-2 bg-qnx-olive text-white text-xs font-semibold rounded-lg">
                  Start Practice Session
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (5 cols): Diagnosed Weak Areas */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-qnx-terracotta" />
              <h2 className="font-serif text-2xl font-bold text-qnx-text">Weak Area Diagnostics</h2>
            </div>
            <Link to="/analytics" className="text-xs font-bold text-qnx-olive hover:underline">
              Full Report →
            </Link>
          </div>

          <div className="bg-white border border-qnx-border rounded-xl p-5 shadow-paper-sm space-y-4">
            {weaknesses.length > 0 ? (
              <div className="space-y-3">
                {weaknesses.slice(0, 4).map((weak, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-qnx-terracotta-light/60 border border-qnx-terracotta-soft rounded-lg space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-qnx-text">{weak.concept}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-qnx-terracotta-soft text-qnx-terracotta">
                        {weak.accuracy_percentage}% Accuracy
                      </span>
                    </div>
                    <p className="text-[11px] text-qnx-muted">
                      {weak.subject} • {weak.chapter} ({weak.attempts} attempts)
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 space-y-2">
                <CheckCircle2 className="w-8 h-8 text-qnx-olive mx-auto" />
                <p className="font-serif text-base font-bold text-qnx-text">No critical weaknesses detected</p>
                <p className="text-xs text-qnx-muted">Keep practicing to discover conceptual gap diagnostics.</p>
              </div>
            )}

            <div className="pt-2 border-t border-qnx-border-light">
              <Link
                to="/mistakes"
                className="w-full py-2 bg-qnx-cream-paper hover:bg-qnx-cream border border-qnx-border text-qnx-text font-semibold text-xs rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <span>Open Mistake Notebook</span>
                <ChevronRight className="w-3.5 h-3.5 text-qnx-muted" />
              </Link>
            </div>
          </div>

          {/* Quick Subject Discovery Navigation */}
          <div className="bg-white border border-qnx-border rounded-xl p-5 shadow-paper-sm space-y-3">
            <h3 className="font-serif text-lg font-bold text-qnx-text">Explore by Subject</h3>
            <div className="grid grid-cols-3 gap-2">
              <Link
                to="/search?subject=Physics"
                className="p-3 bg-qnx-sage-light hover:bg-qnx-sage-soft border border-qnx-sage/30 rounded-lg text-center transition-colors"
              >
                <p className="text-xs font-bold text-qnx-olive">Physics</p>
                <p className="text-[10px] text-qnx-muted">Mechanics, EM</p>
              </Link>
              <Link
                to="/search?subject=Chemistry"
                className="p-3 bg-qnx-blue-light hover:bg-qnx-blue-soft border border-qnx-blue-soft rounded-lg text-center transition-colors"
              >
                <p className="text-xs font-bold text-[#38679E]">Chemistry</p>
                <p className="text-[10px] text-qnx-muted">Organic, Phys</p>
              </Link>
              <Link
                to="/search?subject=Mathematics"
                className="p-3 bg-qnx-terracotta-light hover:bg-qnx-terracotta-soft border border-qnx-terracotta-soft rounded-lg text-center transition-colors"
              >
                <p className="text-xs font-bold text-qnx-terracotta">Math</p>
                <p className="text-[10px] text-qnx-muted">Calculus, Alg</p>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
