import React from 'react';
import { useParams } from 'react-router-dom';
import { Input, Select, Button } from '@/components/ui';
import { JOB_TYPES } from '@/lib/constants';
export default function JobEditPage() {
  const { id } = useParams();
  return (
    <div style={{ padding:'var(--spacing-8)', maxWidth:800, margin:'0 auto' }}>
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Edit Job #{id}</h1>
      <div className="card" style={{ padding:'var(--spacing-8)' }}>
        <Input label="Job Title" placeholder="Senior Frontend Engineer" />
        <Select label="Job Type" options={JOB_TYPES} />
        <Input label="Location" placeholder="Remote" />
        <div className="form-group"><label className="form-label">Description</label><textarea className="form-input" rows={6} placeholder="Job description..." style={{ resize:'vertical' }} /></div>
        <div style={{ display:'flex', justifyContent:'flex-end', gap:'var(--spacing-3)', marginTop:'var(--spacing-6)' }}>
          <Button variant="secondary">Cancel</Button><Button variant="primary">Save Changes</Button>
        </div>
      </div>
    </div>
  );
}
