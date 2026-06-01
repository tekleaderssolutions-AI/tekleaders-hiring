import React from 'react';
import { Sparkles } from 'lucide-react';
export default function AiInsightCard({ title, insight }) {
  return (
    <div className="card" style={{ padding:'var(--spacing-5)', borderLeft:'3px solid var(--color-primary)' }}>
      <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)', marginBottom:'var(--spacing-2)' }}>
        <Sparkles size={14} style={{ color:'var(--color-primary)' }} />
        <span style={{ fontSize:'var(--text-xs)', fontWeight:'var(--weight-semibold)', color:'var(--color-primary)' }}>AI Insight</span>
      </div>
      <h4 style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-2)' }}>{title}</h4>
      <p style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)', lineHeight:'var(--leading-relaxed)' }}>{insight}</p>
    </div>
  );
}
