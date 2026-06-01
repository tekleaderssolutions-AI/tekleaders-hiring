import React from 'react';
import { Sparkles } from 'lucide-react';

export default function AiScoreBadge({ score, label = 'AI Match' }) {
  const color = score >= 80 ? 'var(--color-success)' : score >= 50 ? 'var(--color-warning)' : 'var(--color-danger)';
  return (
    <div style={{ display:'inline-flex', alignItems:'center', gap:6, padding:'4px 10px', borderRadius:'var(--radius-full)', background:`${color}15`, fontSize:'var(--text-xs)', fontWeight:'var(--weight-semibold)' }}>
      <Sparkles size={12} style={{ color }} />
      <span style={{ color }}>{score}% {label}</span>
    </div>
  );
}
