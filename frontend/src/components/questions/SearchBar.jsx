import React from 'react';
import { Search, Sparkles, X } from 'lucide-react';

export const SearchBar = ({
  value,
  onChange,
  onSearch,
  placeholder = "Search JEE Main questions with semantic keywords (e.g. 'torque rolling without slipping')...",
  loading = false
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) onSearch(value);
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <div className="relative flex items-center">
        <Search className="absolute left-4 w-5 h-5 text-qnx-muted" />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full pl-12 pr-28 py-3.5 bg-white border border-qnx-border rounded-2xl text-sm text-qnx-text placeholder:text-qnx-muted focus:outline-none focus:border-qnx-olive focus:ring-2 focus:ring-qnx-sage-soft shadow-paper transition-all"
        />

        {value && (
          <button
            type="button"
            onClick={() => onChange('')}
            className="absolute right-24 p-1 text-qnx-muted hover:text-qnx-text rounded-full"
            title="Clear"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <button
          type="submit"
          disabled={loading}
          className="absolute right-2 px-4 py-2 bg-qnx-olive hover:bg-qnx-olive-dark disabled:opacity-60 text-[#F7F4EA] font-semibold text-xs rounded-xl shadow-paper-sm transition-all hover:-translate-y-0.5 flex items-center gap-1.5"
        >
          {loading ? (
            <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5" />
              <span>Search</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default SearchBar;
