import React from 'react';
import { Brain } from 'lucide-react';

export default function ReasoningTrace({ steps = [] }) {
  return (
    <div style={{ padding:'var(--spacing-4)', background:'var(--color-bg-secondary)', borderRadius:'var(--radius-lg)', border:'1px solid var(--color-border)' }}>
      <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)', marginBottom:'var(--spacing-3)', fontSize:'var(--text-xs)', color:'var(--color-text-muted)', fontWeight:'var(--weight-semibold)', textTransform:'uppercase' }}>
        <Brain size={14} /><span>Reasoning Trace</span>
      </div>
      {steps.map((step, i) => (
        <div key={i} style={{ display:'flex', gap:'var(--spacing-3)', paddingLeft:'var(--spacing-2)', marginBottom:'var(--spacing-2)' }}>
          <div style={{ width:2, background:'var(--gradient-primary)', borderRadius:2, flexShrink:0 }} />
          <p style={{ fontSize:'var(--text-xs)', color:'var(--color-text-secondary)', lineHeight:'var(--leading-relaxed)' }}>{step}</p>
        </div>
      ))}
    </div>
  );
}
