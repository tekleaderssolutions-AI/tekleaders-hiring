import React from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
export default function RequirementsChecklist({ requirements = [] }) {
  return (
    <div className="card" style={{ padding:'var(--spacing-5)' }}>
      <h4 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-4)' }}>Requirements</h4>
      {requirements.map((req, i) => (
        <div key={i} style={{ display:'flex', alignItems:'center', gap:'var(--spacing-3)', padding:'var(--spacing-2) 0', borderBottom:'1px solid var(--color-border-light)' }}>
          {req.met ? <CheckCircle size={16} style={{ color:'var(--color-success)' }} /> : <XCircle size={16} style={{ color:'var(--color-danger)' }} />}
          <span style={{ fontSize:'var(--text-sm)', color: req.met ? 'var(--color-text)' : 'var(--color-text-muted)' }}>{req.label}</span>
        </div>
      ))}
    </div>
  );
}
