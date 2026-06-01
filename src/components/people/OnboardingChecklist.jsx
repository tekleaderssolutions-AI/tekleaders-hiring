import React from 'react';
import { CheckCircle, Circle } from 'lucide-react';
export default function OnboardingChecklist({ items = [] }) {
  return (
    <div className="card" style={{ padding:'var(--spacing-5)' }}>
      <h4 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-4)' }}>Onboarding Tasks</h4>
      {items.map((item, i) => (
        <div key={i} style={{ display:'flex', alignItems:'center', gap:'var(--spacing-3)', padding:'var(--spacing-2) 0' }}>
          {item.done ? <CheckCircle size={16} style={{ color:'var(--color-success)' }} /> : <Circle size={16} style={{ color:'var(--color-text-hint)' }} />}
          <span style={{ fontSize:'var(--text-sm)', textDecoration:item.done ? 'line-through' : 'none', color:item.done ? 'var(--color-text-muted)' : 'var(--color-text)' }}>{item.label}</span>
        </div>
      ))}
    </div>
  );
}
