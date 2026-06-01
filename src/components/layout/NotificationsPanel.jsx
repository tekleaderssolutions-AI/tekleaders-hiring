import React from 'react';
import { X, Bell, CheckCircle, AlertTriangle, User } from 'lucide-react';

const mockNotifications = [
  { id: 1, type: 'success', title: 'Screening Complete', message: 'AI finished screening 12 candidates for Senior Engineer', time: '2m ago' },
  { id: 2, type: 'warning', title: 'Review Required', message: 'Candidate John D. flagged for manual review', time: '15m ago' },
  { id: 3, type: 'info', title: 'New Application', message: 'Sarah M. applied for Product Designer', time: '1h ago' },
  { id: 4, type: 'info', title: 'Interview Scheduled', message: 'Interview with Alex K. tomorrow at 2pm', time: '2h ago' },
];

const typeIcons = { success: CheckCircle, warning: AlertTriangle, info: User };

export default function NotificationsPanel({ onClose }) {
  return (
    <div style={{
      position: 'fixed', top: 'var(--topbar-height)', right: 0, width: 380, height: 'calc(100vh - var(--topbar-height))',
      background: 'var(--color-surface)', borderLeft: '1px solid var(--color-border)',
      boxShadow: 'var(--shadow-xl)', zIndex: 'var(--z-overlay)', animation: 'slideInRight 0.2s ease',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'var(--spacing-4) var(--spacing-6)', borderBottom:'1px solid var(--color-border)' }}>
        <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)' }}>
          <Bell size={18} />
          <h3 style={{ fontSize:'var(--text-base)', fontWeight:'var(--weight-semibold)' }}>Notifications</h3>
        </div>
        <button onClick={onClose} style={{ color:'var(--color-text-muted)' }}><X size={18} /></button>
      </div>
      <div style={{ flex:1, overflowY:'auto' }}>
        {mockNotifications.map((n) => {
          const Icon = typeIcons[n.type] || Bell;
          return (
            <div key={n.id} style={{
              display:'flex', gap:'var(--spacing-3)', padding:'var(--spacing-4) var(--spacing-6)',
              borderBottom:'1px solid var(--color-border-light)', cursor:'pointer',
              transition:'background var(--transition-fast)',
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-surface-hover)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <div style={{ width:32, height:32, borderRadius:'var(--radius-md)', background:'var(--glass-bg-light)', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                <Icon size={16} />
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-medium)' }}>{n.title}</div>
                <div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)', marginTop:2 }}>{n.message}</div>
                <div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-hint)', marginTop:4 }}>{n.time}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
