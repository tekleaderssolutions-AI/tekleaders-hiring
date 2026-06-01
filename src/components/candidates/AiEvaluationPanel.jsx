import React from 'react';
import { Sparkles } from 'lucide-react';
import { ScoreRing } from '@/components/ui';
export default function AiEvaluationPanel({ evaluation = {} }) {
  return (
    <div className="card" style={{ padding:'var(--spacing-6)' }}>
      <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)', marginBottom:'var(--spacing-4)' }}><Sparkles size={18} style={{ color:'var(--color-primary)' }} /><h4 style={{ fontWeight:'var(--weight-semibold)' }}>AI Evaluation</h4></div>
      <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-6)', marginBottom:'var(--spacing-4)' }}>
        <ScoreRing score={evaluation.overallScore || 0} size={80} strokeWidth={5} />
        <div><div style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)' }}>{evaluation.overallScore || 0}%</div><div style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)' }}>Overall Match</div></div>
      </div>
      <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-2)' }}>
        {(evaluation.criteria || []).map((c) => (
          <div key={c.name} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'var(--spacing-2) 0', borderBottom:'1px solid var(--color-border-light)' }}>
            <span style={{ fontSize:'var(--text-sm)' }}>{c.name}</span>
            <span style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-semibold)', color:c.score >= 80 ? 'var(--color-success)' : c.score >= 50 ? 'var(--color-warning)' : 'var(--color-danger)' }}>{c.score}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
