import React from 'react';
import { Avatar } from '@/components/ui';
import AiScoreBadge from '@/components/ai/AiScoreBadge';

export default function KanbanCard({ candidate = {}, onClick }) {
  return (
    <div className="kanban-card" onClick={onClick}>
      <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)', marginBottom:'var(--spacing-2)' }}>
        <Avatar name={candidate.name} size="sm" />
        <div>
          <div className="kanban-card-name">{candidate.name || 'Unknown'}</div>
          <div className="kanban-card-meta">{candidate.role || 'Candidate'}</div>
        </div>
      </div>
      {candidate.aiScore != null && <AiScoreBadge score={candidate.aiScore} />}
    </div>
  );
}
