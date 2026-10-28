import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  LayoutDashboard, 
  Search, 
  FileText, 
  BookOpen, 
  PenTool, 
  TrendingUp, 
  Sparkles, 
  AlertCircle, 
  Settings,
  Compass,
  Bookmark
} from 'lucide-react';

const navItems = [
  { name: 'Home', path: '/', icon: Home, exact: true },
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Browse PYQs', path: '/search', icon: Search },
  { name: 'Past Papers', path: '/papers', icon: FileText },
  { name: 'Chapters', path: '/chapters', icon: BookOpen },
  { name: 'Practice', path: '/practice', icon: PenTool, badge: 'Adaptive' },
  { name: 'Insights', path: '/insights', icon: Sparkles },
  { name: 'Analytics', path: '/analytics', icon: TrendingUp },
  { name: 'Mistakes', path: '/mistakes', icon: AlertCircle },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-qnx-text/30 z-30 md:hidden backdrop-blur-xs transition-opacity"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-30 w-64 bg-[#FCFAF5] border-r border-qnx-border flex flex-col justify-between py-5 px-3 transform transition-transform duration-200 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="space-y-6">
          {/* Section: Main Navigation */}
          <div className="space-y-1">
            <p className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-qnx-muted">
              Study Workspace
            </p>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.exact}
                  onClick={onClose}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group ${
                      isActive
                        ? 'bg-qnx-sage-soft text-qnx-olive border border-qnx-sage/30 shadow-paper-sm'
                        : 'text-qnx-text hover:bg-white hover:text-qnx-olive'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <div className="flex items-center gap-3">
                        <Icon
                          className={`w-4 h-4 transition-colors ${
                            isActive ? 'text-qnx-olive' : 'text-qnx-muted group-hover:text-qnx-olive'
                          }`}
                        />
                        <span>{item.name}</span>
                      </div>
                      {item.badge && (
                        <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-qnx-mustard-soft text-[#946E14] border border-qnx-mustard-soft">
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </NavLink>
              );
            })}
          </div>
        </div>

        {/* Bottom Quick Context Card */}
        <div className="pt-4 border-t border-qnx-border px-2">
          <div className="p-3.5 bg-qnx-sage-light rounded-xl border border-qnx-sage-soft">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-2 h-2 rounded-full bg-qnx-olive"></span>
              <p className="text-[11px] font-bold text-qnx-olive">JEE Main 2026 Shift Data</p>
            </div>
            <p className="text-[10px] text-qnx-muted leading-relaxed">
              Official shift papers extracted, embedded, and mapped to syllabus concepts.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
