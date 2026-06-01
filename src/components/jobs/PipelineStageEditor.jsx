import React from 'react';
export default function PipelineStageEditor({ stages = [], onChange }) {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-3)' }}>
      <h4 style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-semibold)' }}>Pipeline Stages</h4>
      {stages.map((stage, i) => (
        <div key={stage.id} className="card" style={{ padding:'var(--spacing-3)', display:'flex', alignItems:'center', gap:'var(--spacing-3)' }}>
          <div style={{ width:12, height:12, borderRadius:'50%', background:stage.color }} />
          <span style={{ flex:1, fontSize:'var(--text-sm)' }}>{stage.label}</span>
          <span style={{ fontSize:'var(--text-xs)', color:'var(--color-text-hint)' }}>#{i+1}</span>
        </div>
      ))}
    </div>
  );
}
