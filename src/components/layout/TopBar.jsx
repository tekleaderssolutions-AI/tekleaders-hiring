import React, { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LogOut, Settings } from 'lucide-react';
import { Avatar, Button } from '@/components/ui';
import { useAuth } from '@/hooks/useAuth';

export default function TopBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
    navigate('/login');
  };

  const navLinks = [
    { label: 'Jobs', path: '/jobs' },
    { label: 'Candidates', path: '/candidates' },
    { label: 'Employees', path: '/people' },
    { label: 'Work calendar', path: '/calendar' },
    { label: 'Mail', path: '/mail' },
    { label: 'Files', path: '/files' },
    { label: 'Reports', path: '/reports' },
  ];

  return (
    <>
      <header style={{
        height: 60,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 var(--spacing-6)',
        borderBottom: '1px solid var(--color-border)',
        background: 'var(--color-surface)',
        position: 'sticky',
        top: 0,
        zIndex: 'var(--z-sticky)',
      }}>
        {/* Left section: Logo & Nav Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-8)', height: '100%' }}>
          <NavLink to="/dashboard" style={{ display: 'flex', alignItems: 'center', color: '#16a34a', textDecoration: 'none' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 12v.01M8 12v.01M12 12v.01M16 12v.01M20 12v.01" />
              <path d="M4 8c2.21 0 4 1.79 4 4s1.79 4 4 4 4-1.79 4-4 1.79-4 4-4" />
            </svg>
          </NavLink>

          <nav style={{ display: 'flex', height: '100%', gap: 'var(--spacing-6)' }}>
            {navLinks.map(link => (
              <NavLink
                key={link.label}
                to={link.path}
                className={({ isActive }) => `top-nav-link ${isActive ? 'active' : ''}`}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  height: '100%',
                  fontSize: '13px',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? 'var(--color-text)' : 'var(--color-text-muted)',
                  textDecoration: 'none',
                  borderBottom: isActive ? '2px solid var(--color-primary)' : '2px solid transparent',
                  transition: 'all 0.2s ease',
                })}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Right section: Avatar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
          {/* User Menu */}
          <div ref={menuRef} style={{ position: 'relative', marginLeft: 'var(--spacing-2)' }}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              style={{
                display: 'flex', alignItems: 'center',
                background: 'transparent', border: 'none', cursor: 'pointer',
                padding: 0, borderRadius: '50%'
              }}
            >
              <Avatar name={user?.first_name ? `${user.first_name} ${user.last_name}` : 'User'} size="sm" />
            </button>

            {showUserMenu && (
              <div className="topbar-dropdown" style={{ right: 0, marginTop: 'var(--spacing-2)' }}>
                <div className="topbar-dropdown-header">
                  <Avatar name={user?.first_name ? `${user.first_name} ${user.last_name}` : 'User'} size="md" />
                  <div>
                    <div className="topbar-dropdown-name">{user?.first_name ? `${user.first_name} ${user.last_name}` : 'Demo User'}</div>
                    <div className="topbar-dropdown-email">{user?.email || 'user@hirix.com'}</div>
                  </div>
                </div>
                <div className="topbar-dropdown-divider" />
                <button className="topbar-dropdown-item" onClick={() => { setShowUserMenu(false); navigate('/settings'); }}>
                  <Settings size={15} />
                  <span>Settings</span>
                </button>
                <button className="topbar-dropdown-item" onClick={handleLogout}>
                  <LogOut size={15} />
                  <span>Log out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

    </>
  );
}
