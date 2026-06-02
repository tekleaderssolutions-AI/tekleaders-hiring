import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { Building2, Users, Shield, Plug, Key, Bot, CreditCard } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

const NAV_ITEMS = [
  { to: '/settings',              label: 'Company',       icon: Building2, end: true },
  { to: '/settings/team',         label: 'Team',          icon: Users },
  { to: '/settings/security',     label: 'Security',      icon: Shield },
  { to: '/settings/integrations', label: 'Integrations',  icon: Plug },
  { to: '/settings/api-keys',     label: 'API Keys',      icon: Key },
  { to: '/settings/ai-automation',label: 'AI Automation', icon: Bot },
  { to: '/settings/billing',      label: 'Billing',       icon: CreditCard },
];

export default function SettingsLayout() {
  return (
    <div className="settings-page">
      <nav className="settings-nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              'settings-nav-item' + (isActive ? ' active' : '')
            }
            style={{ textDecoration: 'none' }}
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  );
}
