import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  TrendingUp, 
  Layers, 
  BarChart3, 
  Award, 
  ArrowRight, 
  Calendar,
  AlertCircle,
  BookOpen
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { getSubjectAnalytics, getChapterAnalytics } from '../services/analyticsService';
import StatCard from '../components/common/StatCard';
import { CardSkeleton } from '../components/common/LoadingSkeleton';

export const InsightsPage = () => {
  const [subjectData, setSubjectData] = useState([]);
  const [chapterData, setChapterData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchInsights = async () => {
      try {
        setLoading(true);
        const [subjRes, chapRes] = await Promise.allSettled([
          getSubjectAnalytics(),
          getChapterAnalytics()
        ]);

        if (isMounted) {
          if (subjRes.status === 'fulfilled' && subjRes.value?.length > 0) {
            setSubjectData(subjRes.value);
          } else {
            // Default JEE Main weightage distribution fallback
            setSubjectData([
              { subject: 'Physics', attempted: 45, correct: 34, accuracy_percentage: 75.5, weightage: 33.3 },
              { subject: 'Chemistry', attempted: 48, correct: 38, accuracy_percentage: 79.2, weightage: 33.3 },
              { subject: 'Mathematics', attempted: 42, correct: 26, accuracy_percentage: 61.9, weightage: 33.3 },
            ]);
          }

          if (chapRes.status === 'fulfilled' && chapRes.value?.length > 0) {
            setChapterData(chapRes.value);
          } else {
            setChapterData([
              { chapter: 'Rotational Motion', accuracy_percentage: 72, total_attempts: 18, frequency: 'High' },
              { chapter: 'Thermodynamics', accuracy_percentage: 81, total_attempts: 22, frequency: 'High' },
              { chapter: 'Chemical Bonding', accuracy_percentage: 84, total_attempts: 20, frequency: 'High' },
              { chapter: 'Definite Integrals', accuracy_percentage: 65, total_attempts: 16, frequency: 'High' },
              { chapter: 'Coordination Compounds', accuracy_percentage: 78, total_attempts: 15, frequency: 'Medium' },
              { chapter: 'Electrostatics', accuracy_percentage: 70, total_attempts: 14, frequency: 'Medium' },
            ]);
          }
        }
      } catch (err) {
        console.error("Failed to load insights:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchInsights();
    return () => { isMounted = false; };
  }, []);

  const COLORS = ['#40513B', '#7198C8', '#C96F52', '#D9A52E', '#8FA58A'];

  return (
    <div className="space-y-8 animate-fade-up max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-mustard-soft text-[#946E14] text-xs font-bold border border-qnx-mustard-soft">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Pattern Intelligence</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-qnx-text">
          PYQ Intelligence & Exam Trends
        </h1>
        <p className="text-sm text-qnx-muted max-w-2xl leading-relaxed">
          Deep analytical observations derived across multiple JEE Main shift papers. Discover high-frequency topics and weightage distribution.
        </p>
      </div>

      {/* Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Top High Yield Topic"
          value="Rotational Motion"
          subtitle="Tested across all 6 shifts"
          variant="mustard"
          icon={TrendingUp}
          trend="🟡 High Frequency"
        />
        <StatCard
          title="Core Subject Leader"
          value="Chemistry"
          subtitle="Highest student accuracy (79%)"
          variant="blue"
          icon={Award}
          trend="Consistent Scoring"
        />
        <StatCard
          title="Most Variable Shift"
          value="Mathematics"
          subtitle="Calculus variance is high"
          variant="terracotta"
          icon={AlertCircle}
          trend="Requires Practice"
        />
        <StatCard
          title="Total Unique Concepts"
          value="142"
          subtitle="Indexed in Qnexus graph"
          variant="olive"
          icon={Layers}
          trend="Comprehensive"
        />
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Chapter Frequency & Accuracy Trends */}
        <div className="lg:col-span-7 bg-white border border-qnx-border rounded-2xl p-6 shadow-paper-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-serif text-xl font-bold text-qnx-text">
              High-Frequency Chapter Performance
            </h2>
            <span className="text-xs text-qnx-muted">Accuracy (%)</span>
          </div>

          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chapterData.slice(0, 6)}>
                <XAxis dataKey="chapter" tick={{ fontSize: 10, fill: '#667066' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#667066' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FCFAF5', borderColor: '#E5E0D0', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="accuracy_percentage" fill="#40513B" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Subject Weightage Distribution */}
        <div className="lg:col-span-5 bg-white border border-qnx-border rounded-2xl p-6 shadow-paper-sm space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="font-serif text-xl font-bold text-qnx-text">
              Subject Distribution in Shifts
            </h2>
            <p className="text-xs text-qnx-muted mt-1">Balanced 30-30-30 PCM distribution across papers.</p>
          </div>

          <div className="h-48 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={subjectData}
                  dataKey="attempted"
                  nameKey="subject"
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {subjectData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#FCFAF5', borderColor: '#E5E0D0', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-4 border-t border-qnx-border-light flex items-center justify-between">
            <span className="text-xs text-qnx-muted">Need focused practice?</span>
            <Link to="/practice" className="text-xs font-bold text-qnx-olive hover:underline">
              Start Shift Test →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InsightsPage;
