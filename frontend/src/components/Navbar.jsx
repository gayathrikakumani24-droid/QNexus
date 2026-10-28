import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Search, 
  BookOpen, 
  Sparkles, 
  Activity, 
  CheckCircle2, 
  XCircle, 
  Menu, 
  X,
  Compass,
  Bookmark,
  TrendingUp,
  Settings
} from 'lucide-react';
import { checkBackendHealth } from '../services/apiClient';

export const Navbar = ({ toggleSidebar, isSidebarOpen }) => {
  const [healthStatus, setHealthStatus] = useState('checking');
  const [selectedExam, setSelectedExam] = useState('JEE Main');
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const res = await checkBackendHealth();
        if (isMounted) {
          setHealthStatus(res?.status === 'ok' ? 'online' : 'offline');
        }
      } catch (err) {
        if (isMounted) {
          setHealthStatus('offline');
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleQuickSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-[#FCFAF5]/95 backdrop-blur-md border-b border-qnx-border px-4 sm:px-6 py-3 transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Left Brand & Mobile Toggle */}
        <div className="flex items-center gap-3 sm:gap-4">
          <button
            onClick={toggleSidebar}
            className="md:hidden p-2 text-qnx-text hover:bg-qnx-sage-soft rounded-lg transition-colors"
            aria-label="Toggle Navigation Menu"
          >
            {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-qnx-olive text-[#F7F4EA] flex items-center justify-center font-serif font-bold text-xl shadow-paper-sm group-hover:bg-qnx-olive-dark transition-colors">
              Q
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-serif text-2xl font-bold tracking-tight text-qnx-olive group-hover:text-qnx-olive-dark transition-colors">
                  Qnexus
                </span>
                <span className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-semibold bg-qnx-sage-soft text-qnx-olive rounded border border-qnx-sage/30 uppercase tracking-wider">
                  PYQ Intelligence
                </span>
              </div>
              <p className="hidden md:block text-[11px] text-qnx-muted -mt-0.5 font-medium">
                Past Papers. Deeper Learning.
              </p>
            </div>
          </Link>
        </div>

        {/* Center Quick Search Bar */}
        <form onSubmit={handleQuickSearch} className="hidden lg:flex items-center flex-1 max-w-md mx-4">
          <div className="relative w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-qnx-muted" />
            <input
              type="text"
              placeholder="Search concepts, questions, laws, formulae..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-12 py-2 bg-white border border-qnx-border rounded-xl text-xs text-qnx-text placeholder:text-qnx-muted focus:outline-none focus:border-qnx-olive focus:ring-1 focus:ring-qnx-olive shadow-paper-sm transition-all"
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-0.5 bg-qnx-sage-soft hover:bg-qnx-sage text-qnx-olive text-[11px] font-medium rounded transition-colors"
            >
              ↵
            </button>
          </div>
        </form>

        {/* Right Controls: Exam Switcher & System Health */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Exam Selector */}
          <div className="relative">
            <select
              value={selectedExam}
              onChange={(e) => setSelectedExam(e.target.value)}
              className="px-3 py-1.5 bg-white border border-qnx-border rounded-lg text-xs font-semibold text-qnx-text focus:outline-none focus:border-qnx-olive shadow-paper-sm cursor-pointer"
            >
              <option value="JEE Main">JEE Main</option>
              <option value="JEE Advanced" disabled>JEE Adv (Coming Soon)</option>
              <option value="NEET" disabled>NEET (Coming Soon)</option>
            </select>
          </div>

          {/* Health Status Indicator */}
          <div
            className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
              healthStatus === 'online'
                ? 'bg-qnx-sage-soft text-qnx-olive border-qnx-sage/40'
                : 'bg-qnx-terracotta-soft text-qnx-terracotta border-qnx-terracotta-soft'
            }`}
            title={`Backend Service: ${healthStatus}`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                healthStatus === 'online' ? 'bg-qnx-olive animate-pulse' : 'bg-qnx-terracotta'
              }`}
            ></span>
            <span className="capitalize">{healthStatus === 'online' ? 'Live Index' : 'Connecting'}</span>
          </div>

          {/* Quick Practice CTA */}
          <Link
            to="/practice"
            className="px-3.5 py-1.5 bg-qnx-olive hover:bg-qnx-olive-dark text-[#F7F4EA] text-xs font-semibold rounded-lg shadow-paper-sm transition-all hover:-translate-y-0.5 flex items-center gap-1.5"
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Practice</span>
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
