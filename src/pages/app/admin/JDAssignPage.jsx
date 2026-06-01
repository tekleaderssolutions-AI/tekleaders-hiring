import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, UserCheck, UserMinus, Users, AlertCircle, ChevronDown } from 'lucide-react';
import api from '@/lib/api';
import useAuthStore from '@/store/authStore';

function useJobProgress(jobId) {
  return useQuery({
    queryKey: ['job-progress', jobId],
    queryFn: () => api.get(`/admin/jobs/${jobId}/progress`).then(r => r.data),
    enabled: !!jobId,
  });
}

function useCompanyRecruiters() {
  return useQuery({
    queryKey: ['company-recruiters'],
    queryFn: () => api.get('/admin/dashboard').then(d => d.data.employee_metrics || []),
  });
}

function useAssignEmployees(jobId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (employee_ids) => api.post(`/admin/jobs/${jobId}/assign`, { employee_ids }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['job-progress', jobId] }),
  });
}

function useUnassignEmployee(jobId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (employeeId) => api.delete(`/admin/jobs/${jobId}/assign/${employeeId}`).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['job-progress', jobId] }),
  });
}

function useUpdateJobStatus(jobId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (status) => api.patch(`/admin/jobs/${jobId}/status`, { status }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['job-progress', jobId] }),
  });
}

function useJobSubmissions(jobId) {
  return useQuery({
    queryKey: ['job-submissions', jobId],
    queryFn: () => api.get(`/submissions/job/${jobId}`).then(r => r.data),
    enabled: !!jobId,
  });
}

const RANKING_STARS = { '1': '★', '2': '★★', '3': '★★★', '4': '★★★★', '5': '★★★★★', high: 'High', medium: 'Medium', low: 'Low' };
const STATUS_OPTIONS = ['open', 'on_hold', 'closed', 'draft'];
const STATUS_COLOR = { open: '#059669', on_hold: '#d97706', closed: '#6b7280', draft: '#9ca3af' };

export default function JDAssignPage() {
  const { id: jobId } = useParams();
  const navigate = useNavigate();
  const currentUser = useAuthStore(s => s.user);
  const isAdmin = currentUser?.role === 'admin';
  const [selectedEmpId, setSelectedEmpId] = useState('');
  const [activeTab, setActiveTab] = useState('assignments');

  const { data: progress, isLoading } = useJobProgress(jobId);
  const { data: recruiters = [] } = useCompanyRecruiters();
  const { data: submissions = [] } = useJobSubmissions(jobId);
  const assignEmployees = useAssignEmployees(jobId);
  const unassignEmployee = useUnassignEmployee(jobId);
  const updateStatus = useUpdateJobStatus(jobId);
  const [localStatus, setLocalStatus] = useState(null);
  const [statusSaved, setStatusSaved] = useState(false);

  useEffect(() => {
    if (progress?.status) setLocalStatus(progress.status);
  }, [progress?.status]);

  const displayStatus = localStatus ?? progress?.status ?? 'draft';

  const handleStatusChange = (newStatus) => {
    setLocalStatus(newStatus);
    setStatusSaved(false);
    updateStatus.mutate(newStatus, {
      onSuccess: () => setStatusSaved(true),
      onError: () => {
        setLocalStatus(progress?.status ?? 'draft');
        setStatusSaved(false);
      },
    });
    setTimeout(() => setStatusSaved(false), 2000);
  };

  const assignedIds = new Set((progress?.assigned_employees || []).map(e => e.id));
  const availableRecruiters = recruiters.filter(r => !assignedIds.has(r.id));

  const handleAssign = async () => {
    if (!selectedEmpId) return;
    await assignEmployees.mutateAsync([selectedEmpId]);
    setSelectedEmpId('');
  };

  if (isLoading) {
    return <div style={{ padding: 40, textAlign: 'center', color: '#6b7280' }}>Loading...</div>;
  }

  return (
    <div style={{ padding: '28px 36px', maxWidth: 1100 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <button onClick={() => navigate('/dashboard')} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, color: '#6b7280', fontSize: 14 }}>
          <ArrowLeft size={16} /> Back
        </button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111827', margin: 0 }}>{progress?.title || 'Job'}</h1>
          <p style={{ color: '#6b7280', fontSize: 14, marginTop: 4 }}>{progress?.job_code} {progress?.client_name ? `· ${progress.client_name}` : ''}</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <select
            value={displayStatus}
            onChange={e => handleStatusChange(e.target.value)}
            disabled={updateStatus.isPending}
            style={{
              padding: '8px 14px',
              border: `2px solid ${STATUS_COLOR[displayStatus] || '#e5e7eb'}`,
              borderRadius: 8, fontSize: 13, fontWeight: 600,
              color: STATUS_COLOR[displayStatus] || '#374151',
              background: '#fff', cursor: updateStatus.isPending ? 'wait' : 'pointer',
              opacity: updateStatus.isPending ? 0.7 : 1,
              transition: 'all 0.2s',
            }}
          >
            {STATUS_OPTIONS.map(s => (
              <option key={s} value={s}>{s.toUpperCase().replace('_', ' ')}</option>
            ))}
          </select>
          {statusSaved && (
            <span style={{ fontSize: 12, color: '#059669', fontWeight: 600 }}>✓ Saved</span>
          )}
          {updateStatus.isPending && (
            <span style={{ fontSize: 12, color: '#6b7280' }}>Saving…</span>
          )}
          {updateStatus.isError && (
            <span style={{ fontSize: 12, color: '#dc2626', fontWeight: 600 }}>
              {updateStatus.error?.response?.data?.detail
                ? `Error: ${updateStatus.error.response.data.detail}`
                : `HTTP ${updateStatus.error?.response?.status || '?'} — Failed to save`}
            </span>
          )}
        </div>
      </div>

      {/* Progress Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 28 }}>
        {[
          { label: 'Submitted', value: submissions.length },
          { label: 'Unique Candidates', value: new Set(submissions.map(s => s.candidate_email).filter(Boolean)).size },
          { label: 'Progress', value: `${progress?.progress_pct || 0}%` },
        ].map(stat => (
          <div key={stat.label} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: '16px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 800, color: '#00756a' }}>{stat.value}</div>
            <div style={{ fontSize: 12, color: '#6b7280', marginTop: 4 }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #e5e7eb', marginBottom: 24 }}>
        {[{ key: 'assignments', label: 'Recruiter Assignments' }, { key: 'candidates', label: `Candidates (${submissions.length})` }].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{ padding: '10px 20px', border: 'none', background: 'transparent', fontSize: 14, fontWeight: activeTab === tab.key ? 700 : 500, color: activeTab === tab.key ? '#00756a' : '#6b7280', borderBottom: activeTab === tab.key ? '2px solid #00756a' : '2px solid transparent', cursor: 'pointer', marginBottom: -1 }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Assignments Tab */}
      {activeTab === 'assignments' && (
        <div>
          {/* Assign recruiter — admin only */}
          {isAdmin && <div style={{ background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 10, padding: 20, marginBottom: 24, display: 'flex', gap: 12, alignItems: 'flex-end' }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 6 }}>Assign Recruiter</label>
              <select
                value={selectedEmpId}
                onChange={e => setSelectedEmpId(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: 14, background: '#fff' }}
              >
                <option value="">Select recruiter...</option>
                {availableRecruiters.map(r => (
                  <option key={r.id} value={r.id}>{r.name} ({r.email})</option>
                ))}
              </select>
            </div>
            <button
              onClick={handleAssign}
              disabled={!selectedEmpId || assignEmployees.isPending}
              style={{ background: '#00756a', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', fontSize: 14, fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap', opacity: !selectedEmpId ? 0.5 : 1 }}
            >
              <UserCheck size={15} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Assign
            </button>
          </div>}

          {/* Current Assignments */}
          {(progress?.assigned_employees || []).length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 10 }}>
              <Users size={32} style={{ opacity: 0.3, marginBottom: 8 }} />
              <div>No recruiters assigned yet</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {(progress?.assigned_employees || []).map(emp => (
                <div key={emp.id} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#00756a20', color: '#00756a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700 }}>
                      {emp.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>{emp.name}</div>
                      <div style={{ fontSize: 12, color: '#6b7280' }}>{emp.email}</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 20, fontWeight: 800, color: '#00756a' }}>{emp.submission_count}</div>
                      <div style={{ fontSize: 11, color: '#6b7280' }}>submitted</div>
                    </div>
                    {isAdmin && (
                      <button
                        onClick={() => unassignEmployee.mutate(emp.id)}
                        style={{ background: '#fee2e2', color: '#dc2626', border: 'none', borderRadius: 6, padding: '6px 12px', fontSize: 12, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}
                      >
                        <UserMinus size={13} /> Remove
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Candidates Tab */}
      {activeTab === 'candidates' && (
        <div>
          {submissions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 10 }}>
              No candidates submitted yet
            </div>
          ) : (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                    {['Candidate', 'Contact', 'Experience', 'Ranking', 'Submitted By', 'Date', 'Status'].map(h => (
                      <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {submissions.map((sub, idx) => (
                    <tr key={sub.id} style={{ borderBottom: idx < submissions.length - 1 ? '1px solid #f3f4f6' : 'none' }}>
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>{sub.candidate_name}</div>
                        {sub.current_company && <div style={{ fontSize: 12, color: '#9ca3af' }}>{sub.current_company}</div>}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ fontSize: 12, color: '#374151' }}>{sub.candidate_email}</div>
                        {sub.candidate_phone && <div style={{ fontSize: 12, color: '#9ca3af' }}>{sub.candidate_phone}</div>}
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 13, color: '#374151' }}>
                        {sub.experience_years ? `${sub.experience_years}y` : '—'}
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 13, color: '#f59e0b' }}>
                        {sub.ranking ? (RANKING_STARS[sub.ranking] || sub.ranking) : '—'}
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 13, color: '#374151' }}>{sub.submitted_by_name}</td>
                      <td style={{ padding: '14px 16px', fontSize: 12, color: '#6b7280' }}>
                        {sub.submitted_at ? new Date(sub.submitted_at).toLocaleDateString('en-IN') : '—'}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{
                          fontSize: 11, padding: '3px 8px', borderRadius: 20, fontWeight: 700, textTransform: 'uppercase',
                          background: sub.status === 'active' ? '#d1fae5' : '#f3f4f6',
                          color: sub.status === 'active' ? '#059669' : '#6b7280',
                        }}>
                          {sub.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
