import React from 'react';
import { Avatar, Badge, ScoreRing } from '@/components/ui';
export default function CandidateGrid({ candidates = [], onCardClick }) {
  return (
    <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(260px,1fr))', gap:'var(--spacing-4)' }}>
      {candidates.map((c) => (
        <div key={c.id} className="card" style={{ padding:'var(--spacing-5)', cursor:'pointer', textAlign:'center' }} onClick={() => onCardClick?.(c)}>
          <Avatar name={c.name} size="lg" className="mx-auto" style={{ margin:'0 auto var(--spacing-3)' }} />
          <div style={{ fontWeight:'var(--weight-semibold)', marginBottom: c.email ? 2 : 4 }}>{c.name}</div>
          {c.email && <div style={{ fontSize:'var(--text-xs)', color:'var(--color-primary)', marginBottom:4 }}>{c.email}</div>}
          <div style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)', marginBottom:'var(--spacing-3)' }}>{c.role}</div>
          <div style={{ display:'flex', justifyContent:'center', gap:'var(--spacing-3)', alignItems:'center' }}>
            <Badge variant="primary">{c.stage}</Badge>
            <ScoreRing score={c.aiScore || 0} size={32} strokeWidth={3} />
          </div>
        </div>
      ))}
    </div>
  );
}
