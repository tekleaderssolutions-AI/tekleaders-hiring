import React from 'react';
export default function CustomReportPage() {
  return (
    <div className="reports-page">
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Custom Report Builder</h1>
      <div className="card" style={{ padding:'var(--spacing-8)', textAlign:'center' }}><p style={{ color:'var(--color-text-muted)' }}>Drag-and-drop report builder will be rendered here.</p></div>
    </div>
  );
}
