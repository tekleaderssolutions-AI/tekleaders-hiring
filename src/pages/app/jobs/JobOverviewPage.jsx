import React from 'react';
import { useParams } from 'react-router-dom';
import { Badge } from '@/components/ui';
import StatCard from '@/components/reports/StatCard';
import { Users, Clock, Target } from 'lucide-react';
export default function JobOverviewPage() {
  const { id } = useParams();
  return (
    <div style={{ padding:'var(--spacing-8)' }}>
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-2)' }}>Senior Frontend Engineer</h1>
      <div style={{ display:'flex', gap:'var(--spacing-3)', marginBottom:'var(--spacing-8)' }}><Badge variant="success" dot>Active</Badge><span style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)' }}>Job #{id}</span></div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'var(--spacing-4)' }}>
        <StatCard label="Applicants" value="42" change={8} icon={Users} />
        <StatCard label="Days Open" value="12" icon={Clock} />
        <StatCard label="Fill Rate" value="85%" change={3} icon={Target} />
      </div>
    </div>
  );
}
