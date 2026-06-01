import React from 'react';
import KanbanCard from './KanbanCard';
import { PIPELINE_STAGES } from '@/lib/constants';

export default function KanbanBoard({ candidates = [], onCardClick }) {
  const grouped = PIPELINE_STAGES.reduce((acc, stage) => {
    acc[stage.id] = candidates.filter((c) => c.stage === stage.id);
    return acc;
  }, {});

  return (
    <div className="kanban">
      {PIPELINE_STAGES.filter((s) => s.id !== 'rejected').map((stage) => (
        <div key={stage.id} className="kanban-column">
          <div className="kanban-column-header">
            <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)' }}>
              <div style={{ width:8, height:8, borderRadius:'50%', background:stage.color }} />
              <span className="kanban-column-title">{stage.label}</span>
            </div>
            <span className="kanban-column-count">{grouped[stage.id]?.length || 0}</span>
          </div>
          <div className="kanban-cards">
            {(grouped[stage.id] || []).map((candidate) => (
              <KanbanCard key={candidate.id} candidate={candidate} onClick={() => onCardClick?.(candidate)} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
