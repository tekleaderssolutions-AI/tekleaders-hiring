import React from 'react';
import { Search, Filter } from 'lucide-react';
import { Button, Select } from '@/components/ui';
import { JOB_TYPES, JOB_STATUSES, DEPARTMENTS } from '@/lib/constants';

export default function JobFilters({ filters = {}, onChange }) {
  const update = (key, value) => onChange?.({ ...filters, [key]: value });
  return (
    <div className="jobs-filters">
      <div style={{ position:'relative', flex:1, minWidth:200 }}>
        <Search size={16} style={{ position:'absolute', left:12, top:'50%', transform:'translateY(-50%)', color:'var(--color-text-hint)' }} />
        <input className="form-input" placeholder="Search jobs..." value={filters.search || ''} onChange={(e) => update('search', e.target.value)} style={{ paddingLeft:36 }} />
      </div>
      <select className="form-input" style={{ width:'auto' }} value={filters.status || ''} onChange={(e) => update('status', e.target.value)}>
        <option value="">All Statuses</option>
        {JOB_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
      </select>
      <select className="form-input" style={{ width:'auto' }} value={filters.department || ''} onChange={(e) => update('department', e.target.value)}>
        <option value="">All Departments</option>
        {DEPARTMENTS.map((d) => <option key={d} value={d}>{d}</option>)}
      </select>
    </div>
  );
}
