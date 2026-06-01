import React from 'react';
import { useParams } from 'react-router-dom';
import HiringFunnel from '@/components/reports/HiringFunnel';
export default function JobReportsPage() {
  const { id } = useParams();
  return (
    <div style={{ padding:'var(--spacing-8)' }}>
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Reports — Job #{id}</h1>
      <div className="card" style={{ padding:'var(--spacing-6)' }}>
        <h3 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-4)' }}>Funnel Analysis</h3>
        <HiringFunnel data={[{label:'Applied',value:42},{label:'Screened',value:28},{label:'Interview',value:12},{label:'Offer',value:3},{label:'Hired',value:1}]} />
      </div>
    </div>
  );
}
