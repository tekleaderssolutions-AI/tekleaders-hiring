import React from 'react';
import { useParams } from 'react-router-dom';
import { Button, Input, FileUpload } from '@/components/ui';
export default function JobApplyPage() {
  const { id } = useParams();
  return (
    <div style={{ maxWidth:600, margin:'0 auto', padding:'calc(80px + var(--spacing-12)) var(--spacing-6)' }}>
      <h1 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Apply for Position #{id}</h1>
      <div className="card" style={{ padding:'var(--spacing-8)' }}>
        <Input label="Full Name" placeholder="John Doe" />
        <Input label="Email" type="email" placeholder="john@example.com" />
        <Input label="Phone" type="tel" placeholder="+1 (555) 000-0000" />
        <Input label="LinkedIn URL" placeholder="https://linkedin.com/in/..." />
        <FileUpload label="Resume" accept=".pdf,.doc,.docx" />
        <div style={{ marginTop:'var(--spacing-6)' }}><Button variant="primary" style={{ width:'100%' }}>Submit Application</Button></div>
      </div>
    </div>
  );
}
