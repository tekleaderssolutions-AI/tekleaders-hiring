import React from 'react';
import { useParams } from 'react-router-dom';
import { Avatar, Badge } from '@/components/ui';
export default function EmployeeProfilePage() {
  const { id } = useParams();
  return (
    <div style={{ padding:'var(--spacing-8)', maxWidth:800, margin:'0 auto' }}>
      <div style={{ display:'flex', gap:'var(--spacing-6)', marginBottom:'var(--spacing-8)' }}>
        <Avatar name="John Smith" size="xl" />
        <div><h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)' }}>John Smith</h1><p style={{ color:'var(--color-text-muted)' }}>Engineering Manager • Engineering</p><Badge variant="success" style={{ marginTop:8 }}>Active</Badge></div>
      </div>
      <div className="card" style={{ padding:'var(--spacing-6)' }}><h3 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-4)' }}>Details</h3><p style={{ color:'var(--color-text-muted)', fontSize:'var(--text-sm)' }}>Employee profile details for #{id}</p></div>
    </div>
  );
}
