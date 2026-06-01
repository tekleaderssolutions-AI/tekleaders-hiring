import React from 'react';
import { Avatar, Badge, ScoreRing } from '@/components/ui';
export default function CandidateTable({ candidates = [], onRowClick }) {
  return (
    <div className="table-container">
      <table className="table">
        <thead><tr><th>Candidate</th><th>Applied For</th><th>Stage</th><th>AI Score</th><th>Applied</th></tr></thead>
        <tbody>
          {candidates.map((c) => (
            <tr key={c.id} onClick={() => onRowClick?.(c)} style={{ cursor:'pointer' }}>
              <td><div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-3)' }}><Avatar name={c.name} size="sm" /><div><div style={{ fontWeight:'var(--weight-medium)' }}>{c.name}</div><div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>{c.email}</div></div></div></td>
              <td style={{ fontSize:'var(--text-sm)' }}>{c.jobTitle}</td>
              <td><Badge variant={c.stage === 'hired' ? 'success' : 'primary'}>{c.stage}</Badge></td>
              <td><ScoreRing score={c.aiScore || 0} size={36} strokeWidth={3} /></td>
              <td style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)' }}>{c.appliedDate}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
