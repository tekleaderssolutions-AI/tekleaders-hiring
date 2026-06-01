import React, { useState, useEffect, useRef } from 'react';
import { Search, X, ArrowRight } from 'lucide-react';

const suggestions = [
  { label: 'Go to Dashboard', action: '/dashboard' },
  { label: 'View all jobs', action: '/jobs' },
  { label: 'View candidates', action: '/candidates' },
  { label: 'Open AI Copilot', action: '/copilot' },
  { label: 'Settings', action: '/settings' },
];

export default function CommandPalette({ onClose }) {
  const [query, setQuery] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const filtered = suggestions.filter((s) => s.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="modal-overlay" onClick={onClose} style={{ alignItems: 'flex-start', paddingTop: '15vh' }}>
      <div onClick={(e) => e.stopPropagation()} style={{
        width: '100%', maxWidth: 560, background: 'var(--color-surface)', border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-2xl)', boxShadow: 'var(--shadow-xl)', overflow: 'hidden',
        animation: 'scaleIn 0.15s ease',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', padding: 'var(--spacing-4)', gap: 'var(--spacing-3)', borderBottom: '1px solid var(--color-border)' }}>
          <Search size={20} style={{ color: 'var(--color-text-muted)' }} />
          <input ref={inputRef} value={query} onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or search..." style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              color: 'var(--color-text)', fontSize: 'var(--text-base)',
            }}
          />
          <button onClick={onClose} style={{ color: 'var(--color-text-muted)' }}><X size={18} /></button>
        </div>
        <div style={{ maxHeight: 300, overflowY: 'auto', padding: 'var(--spacing-2)' }}>
          {filtered.map((item) => (
            <a key={item.label} href={item.action} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: 'var(--spacing-3) var(--spacing-4)', borderRadius: 'var(--radius-lg)',
              color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', textDecoration: 'none',
              transition: 'background var(--transition-fast)',
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-surface-hover)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <span>{item.label}</span>
              <ArrowRight size={14} />
            </a>
          ))}
          {filtered.length === 0 && (
            <div style={{ padding: 'var(--spacing-8)', textAlign: 'center', color: 'var(--color-text-hint)', fontSize: 'var(--text-sm)' }}>
              No results found
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
