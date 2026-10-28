import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  BookOpen, 
  CheckCircle2, 
  Save, 
  RotateCcw, 
  Activity,
  Shield,
  Bell,
  Cpu
} from 'lucide-react';

export const SettingsPage = () => {
  const [targetExam, setTargetExam] = useState('JEE Main');
  const [timerWarning, setTimerWarning] = useState(true);
  const [autoExplain, setAutoExplain] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-8 animate-fade-up max-w-4xl mx-auto pb-12">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-qnx-sage-soft text-qnx-olive text-xs font-bold border border-qnx-sage/30">
          <SettingsIcon className="w-3.5 h-3.5" />
          <span>Configuration</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-qnx-text">
          Study & Platform Settings
        </h1>
        <p className="text-sm text-qnx-muted leading-relaxed">
          Customize your practice mode parameters, target examination syllabus, and learning preferences.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Card 1: Target Exam */}
        <div className="bg-white border border-qnx-border rounded-2xl p-6 shadow-paper-sm space-y-4">
          <h2 className="font-serif text-xl font-bold text-qnx-text">Target Examination</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {['JEE Main', 'JEE Advanced (Beta)', 'NEET (Coming Soon)'].map((exam) => (
              <button
                key={exam}
                type="button"
                onClick={() => !exam.includes('Coming') && setTargetExam(exam)}
                className={`p-4 rounded-xl border text-left transition-all ${
                  targetExam === exam
                    ? 'border-qnx-olive bg-qnx-sage-soft text-qnx-olive font-bold shadow-paper-sm'
                    : 'border-qnx-border bg-qnx-cream-paper text-qnx-text hover:bg-qnx-cream'
                } ${exam.includes('Coming') ? 'opacity-60 cursor-not-allowed' : ''}`}
              >
                <p className="text-sm">{exam}</p>
                <p className="text-[11px] text-qnx-muted mt-1">
                  {exam.includes('Main') ? 'PCM +4/-1 Marking' : 'Syllabus in sync'}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Card 2: Practice Mode Preferences */}
        <div className="bg-white border border-qnx-border rounded-2xl p-6 shadow-paper-sm space-y-4">
          <h2 className="font-serif text-xl font-bold text-qnx-text">Practice Workspace Preferences</h2>
          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 bg-qnx-cream-paper border border-qnx-border rounded-xl cursor-pointer">
              <div>
                <p className="text-xs font-bold text-qnx-text">Time Warning Notification</p>
                <p className="text-[11px] text-qnx-muted">Alert when less than 5 minutes remain in timed session</p>
              </div>
              <input
                type="checkbox"
                checked={timerWarning}
                onChange={(e) => setTimerWarning(e.target.checked)}
                className="w-4 h-4 text-qnx-olive rounded border-qnx-border focus:ring-qnx-olive"
              />
            </label>

            <label className="flex items-center justify-between p-3 bg-qnx-cream-paper border border-qnx-border rounded-xl cursor-pointer">
              <div>
                <p className="text-xs font-bold text-qnx-text">Auto-Suggest Similar PYQs on Incorrect Answer</p>
                <p className="text-[11px] text-qnx-muted">Automatically fetch related questions from Qdrant vector index</p>
              </div>
              <input
                type="checkbox"
                checked={autoExplain}
                onChange={(e) => setAutoExplain(e.target.checked)}
                className="w-4 h-4 text-qnx-olive rounded border-qnx-border focus:ring-qnx-olive"
              />
            </label>
          </div>
        </div>

        {/* Card 3: Backend & Data Architecture Info */}
        <div className="bg-white border border-qnx-border rounded-2xl p-6 shadow-paper-sm space-y-3">
          <h2 className="font-serif text-xl font-bold text-qnx-text flex items-center gap-2">
            <Cpu className="w-4 h-4 text-qnx-olive" />
            <span>Architecture & Storage Engine</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 bg-qnx-sage-light border border-qnx-sage-soft rounded-lg">
              <strong className="text-qnx-olive block mb-1">Source of Truth</strong>
              <span className="text-qnx-muted">MongoDB Collections (`papers`, `questions`, `practice_sessions`, `attempts`, `mistakes`)</span>
            </div>
            <div className="p-3 bg-qnx-blue-light border border-qnx-blue-soft rounded-lg">
              <strong className="text-[#38679E] block mb-1">Vector Index</strong>
              <span className="text-qnx-muted">Qdrant Engine (384-d normalized embeddings)</span>
            </div>
            <div className="p-3 bg-qnx-mustard-light border border-qnx-mustard-soft rounded-lg">
              <strong className="text-[#946E14] block mb-1">AI Tutoring</strong>
              <span className="text-qnx-muted">Groq Cloud LLM (llama-3.3-70b-versatile)</span>
            </div>
          </div>
        </div>

        {/* Save CTA */}
        <div className="flex items-center justify-between pt-2">
          {savedSuccess && (
            <div className="flex items-center gap-1.5 text-xs text-qnx-olive font-bold animate-fade-in">
              <CheckCircle2 className="w-4 h-4" />
              <span>Settings saved successfully.</span>
            </div>
          )}
          <button
            type="submit"
            className="ml-auto px-6 py-2.5 bg-qnx-olive hover:bg-qnx-olive-dark text-white font-semibold text-xs rounded-xl shadow-paper-sm transition-all hover:-translate-y-0.5 flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Preferences</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default SettingsPage;
