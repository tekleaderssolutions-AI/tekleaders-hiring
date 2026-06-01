import React from 'react';
import ReviewCycleForm from '@/components/people/ReviewCycleForm';
export default function PerformancePage() {
  return <div style={{ padding:'var(--spacing-8)' }}><h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Performance Reviews</h1><ReviewCycleForm /></div>;
}
