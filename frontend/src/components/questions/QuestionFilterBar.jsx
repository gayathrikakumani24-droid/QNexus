import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';

export const QuestionFilterBar = ({
  filters,
  onFilterChange,
  onResetFilters,
  totalResults
}) => {
  const subjects = ['All', 'Physics', 'Chemistry', 'Mathematics'];
  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];
  const sessions = ['All', 'January', 'April'];
  const shifts = ['All', 'Shift 1', 'Shift 2'];
  const years = ['All', 2026, 2025, 2024];

  return (
    <div className="bg-white border border-qnx-border rounded-xl p-4 sm:p-5 shadow-paper-sm space-y-4">
      {/* Top Row: Subject Tabs & Reset Action */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-qnx-border-light pb-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-qnx-muted mr-1">
            Subject:
          </span>
          {subjects.map((sub) => (
            <button
              key={sub}
              onClick={() => onFilterChange('subject', sub)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                (filters.subject || 'All') === sub
                  ? 'bg-qnx-olive text-white shadow-paper-sm'
                  : 'bg-qnx-cream-paper border border-qnx-border text-qnx-text hover:bg-qnx-cream'
              }`}
            >
              {sub}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          {totalResults !== undefined && (
            <span className="text-xs font-semibold text-qnx-muted">
              {totalResults} Questions Found
            </span>
          )}
          <button
            onClick={onResetFilters}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs text-qnx-muted hover:text-qnx-terracotta hover:bg-qnx-terracotta-soft/50 rounded-lg transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Second Row: Detailed Faceted Dropdown Selects */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 text-xs">
        {/* Difficulty */}
        <div>
          <label className="block text-[10px] font-bold uppercase tracking-wider text-qnx-muted mb-1">
            Difficulty
          </label>
          <select
            value={filters.difficulty || 'All'}
            onChange={(e) => onFilterChange('difficulty', e.target.value)}
            className="w-full px-2.5 py-1.5 bg-qnx-cream-paper border border-qnx-border rounded-lg font-medium text-qnx-text focus:outline-none focus:border-qnx-olive"
          >
            {difficulties.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        {/* Year */}
        <div>
          <label className="block text-[10px] font-bold uppercase tracking-wider text-qnx-muted mb-1">
            Year
          </label>
          <select
            value={filters.year || 'All'}
            onChange={(e) => onFilterChange('year', e.target.value)}
            className="w-full px-2.5 py-1.5 bg-qnx-cream-paper border border-qnx-border rounded-lg font-medium text-qnx-text focus:outline-none focus:border-qnx-olive"
          >
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        {/* Session */}
        <div>
          <label className="block text-[10px] font-bold uppercase tracking-wider text-qnx-muted mb-1">
            Session
          </label>
          <select
            value={filters.session || 'All'}
            onChange={(e) => onFilterChange('session', e.target.value)}
            className="w-full px-2.5 py-1.5 bg-qnx-cream-paper border border-qnx-border rounded-lg font-medium text-qnx-text focus:outline-none focus:border-qnx-olive"
          >
            {sessions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Shift */}
        <div>
          <label className="block text-[10px] font-bold uppercase tracking-wider text-qnx-muted mb-1">
            Shift
          </label>
          <select
            value={filters.shift || 'All'}
            onChange={(e) => onFilterChange('shift', e.target.value)}
            className="w-full px-2.5 py-1.5 bg-qnx-cream-paper border border-qnx-border rounded-lg font-medium text-qnx-text focus:outline-none focus:border-qnx-olive"
          >
            {shifts.map((sh) => (
              <option key={sh} value={sh}>{sh}</option>
            ))}
          </select>
        </div>

        {/* Chapter / Concept Custom Input */}
        <div className="col-span-2 sm:col-span-4 lg:col-span-1">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-qnx-muted mb-1">
            Chapter/Concept
          </label>
          <input
            type="text"
            placeholder="e.g. Torque, Integrals..."
            value={filters.chapter || ''}
            onChange={(e) => onFilterChange('chapter', e.target.value)}
            className="w-full px-2.5 py-1.5 bg-qnx-cream-paper border border-qnx-border rounded-lg text-xs text-qnx-text placeholder:text-qnx-muted focus:outline-none focus:border-qnx-olive"
          />
        </div>
      </div>
    </div>
  );
};

export default QuestionFilterBar;
