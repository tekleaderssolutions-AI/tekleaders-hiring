import React from 'react';
import StatCard from '@/components/reports/StatCard';
import { Bot, Zap, CheckCircle } from 'lucide-react';
export default function AIPerformancePage() {
  return (
    <div className="reports-page">
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>AI Performance</h1>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'var(--spacing-4)', marginBottom:'var(--spacing-6)' }}>
        <StatCard label="Screenings" value="2,847" change={18} icon={Bot} />
        <StatCard label="Accuracy" value="94%" change={2} icon={CheckCircle} />
        <StatCard label="Avg Time" value="2.3s" change={-8} icon={Zap} />
      </div>
      <div className="card" style={{ padding:'var(--spacing-6)' }}><p style={{ color:'var(--color-text-muted)' }}>AI performance charts and detailed analytics will be rendered here.</p></div>
    </div>
  );
}
