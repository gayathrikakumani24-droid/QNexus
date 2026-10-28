import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import SearchPage from './pages/SearchPage';
import QuestionDetailPage from './pages/QuestionDetailPage';
import PapersPage from './pages/PapersPage';
import PaperDetailPage from './pages/PaperDetailPage';
import ChaptersPage from './pages/ChaptersPage';
import PracticePage from './pages/PracticePage';
import InsightsPage from './pages/InsightsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import MistakesPage from './pages/MistakesPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);
  const closeSidebar = () => setIsSidebarOpen(false);

  return (
    <div className="min-h-screen bg-[#F7F4EA] text-[#202820] flex flex-col font-sans selection:bg-[#E5EBDD] selection:text-[#40513B]">
      {/* Top Navigation */}
      <Navbar toggleSidebar={toggleSidebar} isSidebarOpen={isSidebarOpen} />

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto w-full">
          <Routes>
            {/* Landing Page */}
            <Route path="/" element={<LandingPage />} />

            {/* Dashboard */}
            <Route path="/dashboard" element={<Dashboard />} />

            {/* Question Discovery & Search */}
            <Route path="/search" element={<SearchPage />} />
            <Route path="/questions" element={<SearchPage />} />
            <Route path="/question/:id" element={<QuestionDetailPage />} />
            <Route path="/questions/:id" element={<QuestionDetailPage />} />

            {/* Past Papers */}
            <Route path="/papers" element={<PapersPage />} />
            <Route path="/papers/:id" element={<PaperDetailPage />} />

            {/* Chapters */}
            <Route path="/chapters" element={<ChaptersPage />} />
            <Route path="/chapters/:subject" element={<ChaptersPage />} />

            {/* Practice Mode */}
            <Route path="/practice" element={<PracticePage />} />

            {/* PYQ Intelligence & Trends */}
            <Route path="/insights" element={<InsightsPage />} />

            {/* Progress & Analytics */}
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/progress" element={<AnalyticsPage />} />

            {/* Mistakes & Bookmarks */}
            <Route path="/mistakes" element={<MistakesPage />} />
            <Route path="/bookmarks" element={<MistakesPage />} />

            {/* Settings */}
            <Route path="/settings" element={<SettingsPage />} />

            {/* 404 Fallback */}
            <Route path="*" element={<LandingPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
