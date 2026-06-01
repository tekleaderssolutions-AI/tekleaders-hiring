import React from 'react';
import OrgChartComponent from '@/components/people/OrgChart';
export default function OrgChartPage() {
  return <div style={{ padding:'var(--spacing-8)' }}><h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Organization Chart</h1><OrgChartComponent /></div>;
}
