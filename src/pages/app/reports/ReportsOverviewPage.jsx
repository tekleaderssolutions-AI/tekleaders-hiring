import React from 'react';
import { BarChart2 } from 'lucide-react';

export default function ReportsOverviewPage() {
  return (
    <div className="reports-page">
      <div className="reports-header">
        <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--weight-bold)' }}>Reports Overview</h1>
      </div>

      <div style={{ textAlign: 'center', padding: 80, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 12, marginTop: 8 }}>
        <BarChart2 size={36} style={{ opacity: 0.3, marginBottom: 12 }} />
        <div style={{ fontSize: 15 }}>No report data yet</div>
        <div style={{ fontSize: 13, marginTop: 4 }}>Reports will populate as your team adds jobs, candidates, and submissions</div>
      </div>
    </div>
  );
}
