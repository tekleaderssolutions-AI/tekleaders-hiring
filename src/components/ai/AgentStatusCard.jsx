import React from 'react';
import { Activity } from 'lucide-react';

export default function AgentStatusCard({ agent = {} }) {
  const statusColors = { active: 'var(--color-success)', idle: 'var(--color-text-hint)', error: 'var(--color-danger)' };
  return (
    <div className="card" style={{ padding:'var(--spacing-4)' }}>
      <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-3)', marginBottom:'var(--spacing-3)' }}>
        <div style={{ width:8, height:8, borderRadius:'50%', background:statusColors[agent.status] || statusColors.idle }} />
        <span style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-medium)' }}>{agent.name || 'Agent'}</span>
      </div>
      <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)', fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>
        <Activity size={12} />
        <span>{agent.task || 'Idle'}</span>
      </div>
    </div>
  );
}
