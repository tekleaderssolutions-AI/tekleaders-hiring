import React from 'react';
import { Badge, Button } from '@/components/ui';
export default function BillingPage() {
  return (
    <div className="settings-page"><div className="settings-content">
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-8)' }}>Billing</h1>
      <div className="card" style={{ padding:'var(--spacing-6)', marginBottom:'var(--spacing-6)' }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <div><h3 style={{ fontWeight:'var(--weight-semibold)' }}>Professional Plan</h3><p style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)', marginTop:4 }}>$149/month • Billed monthly</p></div>
          <Badge variant="success">Active</Badge>
        </div>
      </div>
      <div className="card" style={{ padding:'var(--spacing-6)' }}>
        <h3 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-4)' }}>Usage This Month</h3>
        <div style={{ display:'flex', justifyContent:'space-between', padding:'var(--spacing-2) 0', borderBottom:'1px solid var(--color-border-light)', fontSize:'var(--text-sm)' }}><span style={{ color:'var(--color-text-muted)' }}>AI Screenings</span><span>847 / Unlimited</span></div>
        <div style={{ display:'flex', justifyContent:'space-between', padding:'var(--spacing-2) 0', borderBottom:'1px solid var(--color-border-light)', fontSize:'var(--text-sm)' }}><span style={{ color:'var(--color-text-muted)' }}>Active Jobs</span><span>24 / Unlimited</span></div>
        <div style={{ display:'flex', justifyContent:'space-between', padding:'var(--spacing-2) 0', fontSize:'var(--text-sm)' }}><span style={{ color:'var(--color-text-muted)' }}>Team Members</span><span>8 / 25</span></div>
      </div>
      <div style={{ marginTop:'var(--spacing-6)', display:'flex', gap:'var(--spacing-3)' }}><Button variant="primary">Upgrade Plan</Button><Button variant="ghost">Cancel Subscription</Button></div>
    </div></div>
  );
}
