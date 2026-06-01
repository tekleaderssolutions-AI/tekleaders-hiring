import React from 'react';
import { useParams } from 'react-router-dom';
import { Input, Button } from '@/components/ui';
import PipelineStageEditor from '@/components/jobs/PipelineStageEditor';
import { PIPELINE_STAGES } from '@/lib/constants';
export default function JobSettingsPage() {
  const { id } = useParams();
  return (
    <div style={{ padding:'var(--spacing-8)', maxWidth:700, margin:'0 auto' }}>
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Settings — Job #{id}</h1>
      <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-6)' }}>
        <div className="card" style={{ padding:'var(--spacing-6)' }}><h3 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-4)' }}>General</h3><Input label="Auto-close after (days)" placeholder="30" /><Input label="Notification email" placeholder="hiring@company.com" /></div>
        <div className="card" style={{ padding:'var(--spacing-6)' }}><PipelineStageEditor stages={PIPELINE_STAGES} /></div>
        <div style={{ display:'flex', justifyContent:'flex-end', gap:'var(--spacing-3)' }}><Button variant="danger">Archive Job</Button><Button variant="primary">Save Settings</Button></div>
      </div>
    </div>
  );
}
