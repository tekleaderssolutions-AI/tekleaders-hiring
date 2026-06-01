import React from 'react';
import PipelineChart from '@/components/reports/PipelineChart';
export default function PipelineReportPage() {
  return <div className="reports-page"><h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Pipeline Report</h1><PipelineChart /></div>;
}
