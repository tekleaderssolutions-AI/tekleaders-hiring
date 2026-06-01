import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink, Briefcase, Search } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';

function useJobs() {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: () => api.get('/jobs').then(r => r.data),
  });
}

const STATUS_CONFIG = {
  open:        { label: 'Open',        color: '#059669', bg: '#d1fae5' },
  closed:      { label: 'Closed',      color: '#6b7280', bg: '#f3f4f6' },
  on_hold:     { label: 'On Hold',     color: '#d97706', bg: '#fef3c7' },
  draft:       { label: 'Draft',       color: '#6b7280', bg: '#f9fafb' },
  in_progress: { label: 'In Progress', color: '#2563eb', bg: '#dbeafe' },
};

const PRIORITY_CONFIG = {
  urgent: { color: '#dc2626', bg: '#fee2e2' },
  high:   { color: '#ea580c', bg: '#ffedd5' },
  medium: { color: '#2563eb', bg: '#dbeafe' },
  low:    { color: '#6b7280', bg: '#f3f4f6' },
};

function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function JobsListPage() {
  const navigate = useNavigate();
  const { org } = useAuth();
  const companyName = org?.name || 'My Company';
  const { data: jobs = [], isLoading } = useJobs();
  const [search, setSearch] = useState('');

  const filtered = jobs.filter(j => {
    const q = search.toLowerCase();
    return (
      (j.current_title || '').toLowerCase().includes(q) ||
      (j.job_code || '').toLowerCase().includes(q) ||
      (j.assigned_employees || []).some(n => n.toLowerCase().includes(q))
    );
  });

  return (
    <div className="jobs-page">
      {/* Header */}
      <div className="jobs-header-minimal">
        <div className="jobs-company-title">
          {companyName}
          <span className="jobs-external-icon"><ExternalLink size={18} /></span>
        </div>
        <button className="btn-create-job" onClick={() => navigate('/jobs/new')}>
          Create a new job
        </button>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 80, color: '#9ca3af' }}>Loading jobs...</div>
      ) : jobs.length === 0 ? (
        /* Empty state */
        <div className="jobs-empty-state">
          <div style={{ marginBottom: 20, opacity: 0.25 }}>
            <Briefcase size={64} strokeWidth={1} color="#374151" />
          </div>
          <h2 className="jobs-empty-title">Find candidates for job openings at your company</h2>
          <p className="jobs-empty-desc">
            <span
              style={{ color: '#00756a', fontWeight: 600, cursor: 'pointer' }}
              onClick={() => navigate('/jobs/new')}
            >
              Create a job
            </span>{' '}
            to write your job post and source candidates that match the job's requirements.
          </p>
        </div>
      ) : (
        /* Job list */
        <div style={{ padding: '0 32px 40px' }}>
          {/* Search bar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20, maxWidth: 420 }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={15} color="#9ca3af" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search jobs..."
                style={{
                  width: '100%', padding: '8px 12px 8px 32px',
                  border: '1px solid #e5e7eb', borderRadius: 8,
                  fontSize: 13, outline: 'none', boxSizing: 'border-box',
                }}
              />
            </div>
          </div>

          <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                  {['Job Title', 'Assigned To', 'Priority', 'Status', 'Created', 'Actions'].map(h => (
                    <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((job, idx) => {
                  const statusKey = typeof job.status === 'string' ? job.status.toLowerCase().replace(' ', '_') : 'draft';
                  const priorityKey = typeof job.priority === 'string' ? job.priority.toLowerCase() : 'medium';
                  const status = STATUS_CONFIG[statusKey] || STATUS_CONFIG.draft;
                  const priority = PRIORITY_CONFIG[priorityKey] || PRIORITY_CONFIG.medium;
                  return (
                    <tr
                      key={job.id}
                      style={{ borderBottom: idx < filtered.length - 1 ? '1px solid #f3f4f6' : 'none', cursor: 'pointer' }}
                      onClick={() => navigate(`/jobs/${job.id}/assign`)}
                    >
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>{job.current_title || job.title || 'Untitled'}</div>
                        <div style={{ fontSize: 12, color: '#9ca3af' }}>{job.job_code}</div>
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 13, color: '#374151' }}>
                        {job.assigned_employees?.length > 0
                          ? job.assigned_employees.join(', ')
                          : <span style={{ color: '#9ca3af' }}>—</span>}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{ fontSize: 11, padding: '3px 8px', borderRadius: 20, background: priority.bg, color: priority.color, fontWeight: 700, textTransform: 'uppercase' }}>
                          {priorityKey}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 20, background: status.bg, color: status.color, fontWeight: 700, textTransform: 'uppercase' }}>
                          {status.label}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 13, color: '#6b7280' }}>{formatDate(job.created_at)}</td>
                      <td style={{ padding: '14px 16px' }}>
                        <button
                          onClick={e => { e.stopPropagation(); navigate(`/jobs/${job.id}/assign`); }}
                          style={{ background: '#f9fafb', color: '#374151', border: '1px solid #e5e7eb', borderRadius: 6, padding: '5px 12px', fontSize: 12, cursor: 'pointer' }}
                        >
                          Manage
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ padding: 40, textAlign: 'center', color: '#9ca3af', fontSize: 14 }}>
                      No jobs match "{search}"
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
