import React from 'react';
import { useParams } from 'react-router-dom';
import { Input, Button } from '@/components/ui';
export default function JobApplicationFormPage() {
  const { id } = useParams();
  return (
    <div style={{ padding:'var(--spacing-8)', maxWidth:700, margin:'0 auto' }}>
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Application Form — Job #{id}</h1>
      <div className="card" style={{ padding:'var(--spacing-8)' }}>
        <p style={{ color:'var(--color-text-muted)', marginBottom:'var(--spacing-6)' }}>Configure the fields applicants will fill out.</p>
        <Input label="Custom Question 1" placeholder="e.g. Why do you want to join us?" />
        <Input label="Custom Question 2" placeholder="e.g. Describe your experience with..." />
        <Button variant="primary" style={{ marginTop:'var(--spacing-4)' }}>Save Form</Button>
      </div>
    </div>
  );
}
