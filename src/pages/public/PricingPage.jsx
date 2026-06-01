import React from 'react';
import PricingTable from '@/components/landing/PricingTable';
export default function PricingPage() {
  return (
    <div style={{ paddingTop:80 }}>
      <div style={{ textAlign:'center', padding:'var(--spacing-16) var(--spacing-6) 0' }}>
        <h1 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-4xl)', fontWeight:'var(--weight-bold)' }}>Choose your plan</h1>
        <p style={{ color:'var(--color-text-muted)', marginTop:'var(--spacing-3)' }}>Start free, scale as you grow.</p>
      </div>
      <PricingTable />
    </div>
  );
}
