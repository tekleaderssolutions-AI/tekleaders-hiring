import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Briefcase, Users, Bot, UserCircle,
  Calendar, BarChart3, FolderOpen, Inbox, Settings,
  ChevronLeft, ChevronRight, Sparkles, Building2, UserCheck, UsersRound,
} from 'lucide-react';
import useUiStore from '@/store/uiStore';
import { useAuth } from '@/hooks/useAuth';

function buildNavSections(role) {
  if (role === 'admin') {
    return [
      {
        title: 'Admin',
        links: [
          { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
          { to: '/clients', icon: Building2, label: 'Clients' },
          { to: '/jobs', icon: Briefcase, label: 'Jobs' },
          { to: '/candidates', icon: Users, label: 'Candidates' },
          { to: '/team', icon: UsersRound, label: 'Team' },
          { to: '/copilot', icon: Bot, label: 'AI Copilot' },
        ],
      },
      {
        title: 'Organization',
        links: [
          { to: '/people', icon: UserCircle, label: 'People' },
          { to: '/calendar', icon: Calendar, label: 'Calendar' },
          { to: '/reports', icon: BarChart3, label: 'Reports' },
        ],
      },
      {
        title: 'Workspace',
        links: [
          { to: '/files', icon: FolderOpen, label: 'Files' },
          { to: '/inbox', icon: Inbox, label: 'Inbox' },
          { to: '/settings', icon: Settings, label: 'Settings' },
        ],
      },
    ];
  }

  // Recruiter / Employee
  return [
    {
      title: 'Main',
      links: [
        { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/jobs', icon: Briefcase, label: 'My Jobs' },
        { to: '/candidates', icon: Users, label: 'Candidates' },
        { to: '/copilot', icon: Bot, label: 'AI Copilot' },
      ],
    },
    {
      title: 'Workspace',
      links: [
        { to: '/inbox', icon: Inbox, label: 'Inbox' },
        { to: '/settings', icon: Settings, label: 'Settings' },
      ],
    },
  ];
}

export default function Sidebar() {
  const { sidebarCollapsed, collapseSidebar } = useUiStore();
  const location = useLocation();
  const { user } = useAuth();
  const role = user?.role || 'recruiter';
  const navSections = buildNavSections(role);

  return (
    <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-logo">
        <Sparkles size={28} style={{ color: 'var(--color-primary-light)' }} />
        <h1>Hirix</h1>
      </div>

      <nav className="sidebar-nav">
        {navSections.map((section) => (
          <div key={section.title} className="sidebar-section">
            <div className="sidebar-section-title">{section.title}</div>
            {section.links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive || location.pathname.startsWith(link.to) ? 'active' : ''}`
                }
              >
                <link.icon size={20} />
                <span>{link.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="sidebar-link" onClick={collapseSidebar} style={{ width: '100%' }}>
          {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          <span>{sidebarCollapsed ? '' : 'Collapse'}</span>
        </button>
      </div>
    </aside>
  );
}
