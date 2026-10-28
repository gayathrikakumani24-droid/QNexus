import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Search, 
  BookOpen, 
  TrendingUp, 
  AlertCircle, 
  Sparkles, 
  CheckCircle2, 
  Layers, 
  Target, 
  Zap,
  BarChart3,
  Award,
  Compass,
  FileText
} from 'lucide-react';

export const LandingPage = () => {
  return (
    <div className="space-y-20 py-4 max-w-6xl mx-auto">
      {/* SECTION 1: HERO */}
      <section className="relative pt-6 pb-12 overflow-hidden text-center md:text-left">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Left Column: Headlines & CTAs */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-qnx-sage-soft border border-qnx-sage/30 text-qnx-olive text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Past Papers. Deeper Learning.</span>
            </div>

            <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-qnx-text font-bold tracking-tight leading-[1.15]">
              Your Past Papers Have Patterns.{' '}
              <span className="text-qnx-olive italic">Qnexus Helps You Find Them.</span>
            </h1>

            <p className="text-qnx-muted text-base sm:text-lg leading-relaxed max-w-xl">
              Turn previous-year questions into your preparation advantage. Discover chapter frequency, repeated concepts, and authentic exam trends without solving blindly.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 pt-2">
              <Link
                to="/search"
                className="px-6 py-3.5 bg-qnx-olive hover:bg-qnx-olive-dark text-[#F7F4EA] font-semibold text-sm rounded-xl shadow-paper hover:shadow-paper-lift transition-all hover:-translate-y-0.5 flex items-center gap-2"
              >
                <span>Explore PYQs</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <a
                href="#how-it-works"
                className="px-5 py-3.5 bg-white hover:bg-qnx-cream-paper border border-qnx-border text-qnx-text font-semibold text-sm rounded-xl shadow-paper-sm transition-colors flex items-center gap-2"
              >
                <span>How Qnexus Works</span>
              </a>
            </div>

            {/* Micro Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-qnx-border">
              <div>
                <p className="font-serif text-2xl font-bold text-qnx-olive">10,000+</p>
                <p className="text-xs text-qnx-muted">PYQ Questions</p>
              </div>
              <div>
                <p className="font-serif text-2xl font-bold text-qnx-text">Multi-Shift</p>
                <p className="text-xs text-qnx-muted">Coverage</p>
              </div>
              <div>
                <p className="font-serif text-2xl font-bold text-[#946E14]">Chapter-wise</p>
                <p className="text-xs text-qnx-muted">Discovery</p>
              </div>
              <div>
                <p className="font-serif text-2xl font-bold text-[#38679E]">AI Insights</p>
                <p className="text-xs text-qnx-muted">Pedagogical</p>
              </div>
            </div>
          </div>

          {/* Right Column: Floating Educational Study Notebook Mockup */}
          <div className="lg:col-span-5 relative flex justify-center">
            <div className="w-full max-w-md bg-white border border-qnx-border rounded-2xl p-6 shadow-paper-lg space-y-4 animate-float">
              {/* Card Header */}
              <div className="flex items-center justify-between border-b border-qnx-border-light pb-3">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-qnx-sage"></span>
                  <span className="text-xs font-bold uppercase tracking-wider text-qnx-muted">JEE Main 2026 • Shift 1</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-qnx-mustard-soft text-[#946E14] border border-qnx-mustard-soft">
                  🟡 High Frequency
                </span>
              </div>

              {/* Sample Question Mockup */}
              <div className="space-y-2 text-left">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-qnx-sage-soft text-qnx-olive text-xs font-bold">Physics</span>
                  <span className="text-xs text-qnx-muted">Rotational Motion</span>
                </div>
                <p className="text-sm font-medium text-qnx-text leading-relaxed">
                  A solid sphere and a hollow cylinder of equal mass roll down an inclined plane without slipping. What is the ratio of their angular velocities?
                </p>
              </div>

              {/* Insight Badge */}
              <div className="p-3 bg-qnx-blue-light border border-qnx-blue-soft rounded-xl text-left">
                <p className="text-[11px] font-bold text-[#38679E] flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" /> PYQ Pattern Detected
                </p>
                <p className="text-[11px] text-qnx-muted mt-0.5">
                  Similar torque & energy conservation concepts tested in 4 separate shifts.
                </p>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center justify-between pt-2">
                <span className="text-xs font-semibold text-qnx-olive">Accuracy: 78% (Overall)</span>
                <Link to="/search?q=rotational+motion" className="text-xs font-bold text-qnx-olive hover:underline flex items-center gap-1">
                  Solve Similar →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2: WHY QNEXUS? */}
      <section className="space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <p className="text-xs font-bold uppercase tracking-widest text-qnx-olive">Authentic Exam Intelligence</p>
          <h2 className="font-serif text-3xl sm:text-4xl text-qnx-text font-bold">
            Why Prepare With Qnexus?
          </h2>
          <p className="text-qnx-muted text-sm leading-relaxed">
            Standard question banks give you thousands of unorganized problems. Qnexus structures every question into a connected learning hierarchy.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Explore */}
          <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-1 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-qnx-sage-soft text-qnx-olive flex items-center justify-center">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-xl font-bold text-qnx-text">Explore</h3>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Find authentic questions by chapter, topic, shift, and difficulty with hybrid semantic search.
            </p>
          </div>

          {/* Card 2: Practice */}
          <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-1 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-qnx-olive text-[#F7F4EA] flex items-center justify-center">
              <BookOpen className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-xl font-bold text-qnx-text">Practice</h3>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Solve timed mock sessions with official +4/-1 JEE Main marking and instant performance scoring.
            </p>
          </div>

          {/* Card 3: Understand */}
          <div className="bg-white border border-qnx-mustard-soft rounded-card p-6 shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-1 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-qnx-mustard-soft text-[#946E14] flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-xl font-bold text-qnx-text">Understand</h3>
            <p className="text-xs text-qnx-muted leading-relaxed">
              See patterns, frequency trends, and pedagogical step-by-step solutions with KaTeX mathematical formatting.
            </p>
          </div>

          {/* Card 4: Improve */}
          <div className="bg-white border border-qnx-terracotta-soft rounded-card p-6 shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-1 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-qnx-terracotta-soft text-qnx-terracotta flex items-center justify-center">
              <Target className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-xl font-bold text-qnx-text">Improve</h3>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Identify rule-based conceptual weaknesses and maintain an active Mistake Notebook for spaced review.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 3: HOW IT WORKS */}
      <section id="how-it-works" className="space-y-8 bg-[#FCFAF5] border border-qnx-border rounded-2xl p-8 sm:p-12 shadow-paper-sm">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <p className="text-xs font-bold uppercase tracking-widest text-qnx-olive">The Learning Journey</p>
          <h2 className="font-serif text-3xl sm:text-4xl text-qnx-text font-bold">
            How Qnexus Works
          </h2>
          <p className="text-qnx-muted text-sm leading-relaxed">
            From raw exam papers to targeted mastery in 5 structured steps.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 pt-4">
          {[
            { step: '01', title: 'Select Exam', desc: 'Choose your target paper, session, and shift.' },
            { step: '02', title: 'Choose Chapter', desc: 'Focus on high-weightage Physics, Chemistry, or Math.' },
            { step: '03', title: 'Discover PYQs', desc: 'Browse semantically tagged, authentic questions.' },
            { step: '04', title: 'Practice', desc: 'Attempt in test mode with timer and score feedback.' },
            { step: '05', title: 'Analyze Patterns', desc: 'Diagnose weak concepts and review mistakes.' },
          ].map((item, idx) => (
            <div key={idx} className="bg-white border border-qnx-border rounded-xl p-5 shadow-paper-sm space-y-2 text-left">
              <span className="font-serif text-2xl font-bold text-qnx-olive block">{item.step}</span>
              <p className="font-serif text-lg font-bold text-qnx-text">{item.title}</p>
              <p className="text-xs text-qnx-muted leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 4: INTELLIGENCE BEHIND QNEXUS */}
      <section className="space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <p className="text-xs font-bold uppercase tracking-widest text-qnx-olive">Core Technology</p>
          <h2 className="font-serif text-3xl sm:text-4xl text-qnx-text font-bold">
            The Intelligence Behind Qnexus
          </h2>
          <p className="text-qnx-muted text-sm leading-relaxed">
            We use dense vector retrieval and structured knowledge hierarchies to bring clarity to past papers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm space-y-3">
            <div className="w-9 h-9 rounded-lg bg-qnx-sage-soft text-qnx-olive flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-xl font-bold text-qnx-text">Semantic Vector Retrieval</h3>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Find questions testing identical physics or calculus principles even when worded completely differently.
            </p>
          </div>

          <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm space-y-3">
            <div className="w-9 h-9 rounded-lg bg-qnx-mustard-soft text-[#946E14] flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-xl font-bold text-qnx-text">Pattern & Frequency Detection</h3>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Identify recurring concepts like rotational dynamics, definite integrals, and coordination chemistry across shifts.
            </p>
          </div>

          <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm space-y-3">
            <div className="w-9 h-9 rounded-lg bg-qnx-blue-soft text-[#38679E] flex items-center justify-center">
              <Award className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-xl font-bold text-qnx-text">Explainable Recommendations</h3>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Every recommendation is grounded in your actual accuracy diagnostics rather than arbitrary predictions.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 5: EXAM EXPLORER */}
      <section className="space-y-6">
        <div className="flex items-end justify-between">
          <div className="space-y-1">
            <p className="text-xs font-bold uppercase tracking-widest text-qnx-olive">Supported Syllabi</p>
            <h2 className="font-serif text-3xl text-qnx-text font-bold">Exam Explorer</h2>
          </div>
          <Link to="/papers" className="text-xs font-bold text-qnx-olive hover:underline flex items-center gap-1">
            View All Papers →
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Active: JEE Main */}
          <div className="bg-white border-2 border-qnx-olive rounded-card p-6 shadow-paper space-y-3 relative">
            <span className="absolute top-4 right-4 px-2 py-0.5 rounded-full text-[10px] font-bold bg-qnx-sage-soft text-qnx-olive border border-qnx-sage/40">
              Active
            </span>
            <p className="font-serif text-2xl font-bold text-qnx-text">JEE Main</p>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Complete shift papers, physics, chemistry, and mathematics with +4/-1 marking.
            </p>
            <Link
              to="/papers"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-qnx-olive hover:underline pt-2"
            >
              Browse 2026 Shift Papers →
            </Link>
          </div>

          {/* Extensible: JEE Advanced */}
          <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm space-y-3 opacity-80">
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-qnx-cream text-qnx-muted border border-qnx-border">
              Coming Soon
            </span>
            <p className="font-serif text-xl font-bold text-qnx-text">JEE Advanced</p>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Multi-correct, integer-type, and matrix-match deep analytical problems.
            </p>
          </div>

          {/* Extensible: NEET */}
          <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm space-y-3 opacity-80">
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-qnx-cream text-qnx-muted border border-qnx-border">
              Coming Soon
            </span>
            <p className="font-serif text-xl font-bold text-qnx-text">NEET</p>
            <p className="text-xs text-qnx-muted leading-relaxed">
              Physics, Chemistry, and Biology chapter-wise authentic PYQ intelligence.
            </p>
          </div>

          {/* Extensible: State CETs */}
          <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm space-y-3 opacity-80">
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-qnx-cream text-qnx-muted border border-qnx-border">
              Coming Soon
            </span>
            <p className="font-serif text-xl font-bold text-qnx-text">State CETs</p>
            <p className="text-xs text-qnx-muted leading-relaxed">
              EAMCET, MHT-CET, and regional engineering entrance examinations.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 6: PYQ INTELLIGENCE HIGHLIGHTS */}
      <section className="bg-white border border-qnx-border rounded-2xl p-8 shadow-paper-sm space-y-6">
        <div className="space-y-1">
          <p className="text-xs font-bold uppercase tracking-widest text-[#946E14]">Pattern Highlights</p>
          <h2 className="font-serif text-2xl sm:text-3xl text-qnx-text font-bold">
            Real Examples of PYQ Intelligence
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="p-4 bg-qnx-mustard-light border border-qnx-mustard-soft rounded-xl space-y-2">
            <span className="text-[11px] font-bold text-[#946E14] uppercase tracking-wide">
              🟡 Repeated Concept Alert
            </span>
            <p className="text-xs font-semibold text-qnx-text">
              "Moment of Inertia of composite bodies appeared in 4 out of 6 recent shifts."
            </p>
            <p className="text-[11px] text-qnx-muted">
              Mastering the parallel-axis theorem offers immediate multi-shift yield.
            </p>
          </div>

          <div className="p-4 bg-qnx-blue-light border border-qnx-blue-soft rounded-xl space-y-2">
            <span className="text-[11px] font-bold text-[#38679E] uppercase tracking-wide">
              🔵 Shift Variation Insight
            </span>
            <p className="text-xs font-semibold text-qnx-text">
              "Definite integral property \(\int_0^a f(x)dx\) was tested in every single shift."
            </p>
            <p className="text-[11px] text-qnx-muted">
              Varied between trigonometric and exponential integrands across morning/evening shifts.
            </p>
          </div>

          <div className="p-4 bg-qnx-sage-light border border-qnx-sage-soft rounded-xl space-y-2">
            <span className="text-[11px] font-bold text-qnx-olive uppercase tracking-wide">
              🟢 High Yield Chapter
            </span>
            <p className="text-xs font-semibold text-qnx-text">
              "Thermodynamics & Heat account for 8.5% of total physics paper weightage."
            </p>
            <p className="text-[11px] text-qnx-muted">
              Isothermal and adiabatic work formulas dominate numerical sections.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 7: FINAL CTA */}
      <section className="text-center py-12 px-6 bg-qnx-olive rounded-2xl text-[#F7F4EA] shadow-paper-lg space-y-6">
        <div className="max-w-2xl mx-auto space-y-3">
          <h2 className="font-serif text-3xl sm:text-4xl font-bold text-white leading-tight">
            Stop solving PYQs randomly. Start learning from the patterns.
          </h2>
          <p className="text-qnx-sage-soft text-sm sm:text-base leading-relaxed">
            Join thousands of JEE Main aspirants preparing strategically with authentic shift data and concept-level insights.
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/search"
            className="px-8 py-3.5 bg-white hover:bg-qnx-cream text-qnx-olive font-bold text-sm rounded-xl shadow-paper hover:shadow-paper-lift transition-all hover:-translate-y-0.5"
          >
            Start Exploring →
          </Link>
          <Link
            to="/dashboard"
            className="px-6 py-3.5 bg-qnx-olive-dark hover:bg-qnx-olive text-white border border-qnx-sage/30 font-semibold text-sm rounded-xl transition-colors"
          >
            Open Dashboard
          </Link>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
