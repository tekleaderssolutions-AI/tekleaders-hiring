import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Users, TrendingUp, CheckCircle, PauseCircle, BarChart2, ChevronRight, UserPlus, Building2, X, ChevronDown } from 'lucide-react';
import api from '@/lib/api';

function useAdminDashboard() {
  return useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => api.get('/admin/dashboard').then(r => r.data),
    refetchInterval: 30000,
  });
}

const STATUS_CONFIG = {
  open:     { label: 'Open',     color: '#059669', bg: '#d1fae5' },
  closed:   { label: 'Closed',   color: '#6b7280', bg: '#f3f4f6' },
  on_hold:  { label: 'On Hold',  color: '#d97706', bg: '#fef3c7' },
  draft:    { label: 'Draft',    color: '#6b7280', bg: '#f9fafb' },
  in_progress: { label: 'In Progress', color: '#2563eb', bg: '#dbeafe' },
};

const PRIORITY_CONFIG = {
  urgent: { color: '#dc2626', bg: '#fee2e2' },
  high:   { color: '#ea580c', bg: '#ffedd5' },
  medium: { color: '#2563eb', bg: '#dbeafe' },
  low:    { color: '#6b7280', bg: '#f3f4f6' },
};

function MetricCard({ icon: Icon, label, value, color = '#00756a', sub }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: '20px 24px', display: 'flex', alignItems: 'center', gap: 16 }}>
      <div style={{ width: 48, height: 48, borderRadius: 12, background: color + '15', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        <Icon size={22} color={color} />
      </div>
      <div>
        <div style={{ fontSize: 28, fontWeight: 800, color: '#111827', lineHeight: 1 }}>{value}</div>
        <div style={{ fontSize: 13, color: '#6b7280', marginTop: 4 }}>{label}</div>
        {sub && <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 2 }}>{sub}</div>}
      </div>
    </div>
  );
}

function useClients() {
  return useQuery({
    queryKey: ['clients'],
    queryFn: () => api.get('/clients').then(r => r.data),
  });
}

function useCreateClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/clients', data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['clients'] });
      qc.invalidateQueries({ queryKey: ['admin-dashboard'] });
    },
  });
}

function useAssignClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ jobId, clientId }) => api.patch(`/jobs/${jobId}`, { client_id: clientId }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-dashboard'] }),
  });
}

function useUpdatePriority() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ jobId, priority }) => api.patch(`/jobs/${jobId}`, { priority }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-dashboard'] }),
  });
}

export default function AdminDashboardPage() {
  const { data, isLoading } = useAdminDashboard();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('jds');
  const [showClientModal, setShowClientModal] = useState(false);
  const [clientName, setClientName] = useState('');
  const createClient = useCreateClient();
  const assignClient = useAssignClient();
  const updatePriority = useUpdatePriority();
  const { data: clients = [] } = useClients();

  const handleCreateClient = async () => {
    if (!clientName.trim()) return;
    await createClient.mutateAsync({ name: clientName.trim() });
    setClientName('');
    setShowClientModal(false);
  };

  if (isLoading) {
    return (
      <div style={{ padding: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <div style={{ color: '#6b7280', fontSize: 15 }}>Loading dashboard...</div>
      </div>
    );
  }

  const { jd_metrics = {}, candidate_metrics = {}, employee_metrics = [], recent_jobs = [] } = data || {};

  return (
    <div style={{ padding: '28px 36px' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: '#111827', margin: 0 }}>Admin Dashboard</h1>
        <p style={{ color: '#6b7280', marginTop: 4, fontSize: 14 }}>Recruitment activity overview</p>
      </div>

      {/* Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        <MetricCard icon={Briefcase} label="Total JDs" value={jd_metrics.total || 0} color="#00756a" />
        <MetricCard icon={CheckCircle} label="Active JDs" value={jd_metrics.active || 0} color="#059669" />
        <MetricCard icon={Users} label="Candidates Submitted" value={candidate_metrics.total_submitted || 0} color="#2563eb" sub={`${candidate_metrics.unique_candidates || 0} unique`} />
        <MetricCard icon={BarChart2} label="Recruiters" value={employee_metrics.length || 0} color="#7c3aed" />
      </div>

      {/* JD Status Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14, marginBottom: 32 }}>
        {[
          { label: 'Open', value: jd_metrics.active || 0, icon: TrendingUp, color: '#059669' },
          { label: 'On Hold', value: jd_metrics.on_hold || 0, icon: PauseCircle, color: '#d97706' },
          { label: 'Closed', value: jd_metrics.closed || 0, icon: CheckCircle, color: '#6b7280' },
        ].map(item => (
          <div key={item.label} style={{ background: item.color + '08', border: `1px solid ${item.color}30`, borderRadius: 10, padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <item.icon size={18} color={item.color} />
            <span style={{ fontSize: 14, color: '#374151' }}>{item.label}</span>
            <span style={{ fontSize: 20, fontWeight: 700, color: item.color, marginLeft: 'auto' }}>{item.value}</span>
          </div>
        ))}
      </div>

      {/* Tab Navigation */}
      <div style={{ display: 'flex', borderBottom: '1px solid #e5e7eb', marginBottom: 24, gap: 0 }}>
        {[
          { key: 'jds', label: 'JD Tracking' },
          { key: 'employees', label: 'Recruiter Performance' },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: 'transparent',
              fontSize: 14,
              fontWeight: activeTab === tab.key ? 700 : 500,
              color: activeTab === tab.key ? '#00756a' : '#6b7280',
              borderBottom: activeTab === tab.key ? '2px solid #00756a' : '2px solid transparent',
              cursor: 'pointer',
              marginBottom: -1,
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Create Client Modal */}
      {showClientModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#fff', borderRadius: 14, padding: 28, width: 380, boxShadow: '0 20px 60px rgba(0,0,0,0.18)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Building2 size={18} color="#00756a" />
                <span style={{ fontSize: 16, fontWeight: 700, color: '#111827' }}>Create Client</span>
              </div>
              <button onClick={() => { setShowClientModal(false); setClientName(''); }} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af' }}>
                <X size={18} />
              </button>
            </div>
            <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 6 }}>Client Name *</label>
            <input
              autoFocus
              value={clientName}
              onChange={e => setClientName(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleCreateClient()}
              placeholder="e.g. Accenture, TCS, Wipro"
              style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: 14, boxSizing: 'border-box', outline: 'none' }}
            />
            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button
                onClick={handleCreateClient}
                disabled={createClient.isPending || !clientName.trim()}
                style={{ flex: 1, background: '#00756a', color: '#fff', border: 'none', borderRadius: 8, padding: '9px 0', fontSize: 14, fontWeight: 600, cursor: 'pointer', opacity: !clientName.trim() ? 0.5 : 1 }}
              >
                {createClient.isPending ? 'Creating...' : 'Create Client'}
              </button>
              <button
                onClick={() => { setShowClientModal(false); setClientName(''); }}
                style={{ flex: 1, background: '#f9fafb', color: '#374151', border: '1px solid #e5e7eb', borderRadius: 8, padding: '9px 0', fontSize: 14, cursor: 'pointer' }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* JD Tracking Tab */}
      {activeTab === 'jds' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginBottom: 14 }}>
            <button
              onClick={() => setShowClientModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#fff', color: '#374151', border: '1px solid #e5e7eb', borderRadius: 8, padding: '8px 16px', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
            >
              <Building2 size={14} /> Create Client
            </button>
            <button
              onClick={() => navigate('/jobs/new')}
              style={{ background: '#00756a', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
            >
              + New JD
            </button>
          </div>
          {recent_jobs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>No JDs yet. Create one to get started.</div>
          ) : (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                    {['Client', 'JD Title', 'Priority', 'Assigned To', 'Submitted', 'Target', 'Status', 'Actions'].map(h => (
                      <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recent_jobs.map((job, idx) => {
                    const status = STATUS_CONFIG[job.status] || STATUS_CONFIG.draft;
                    const priority = PRIORITY_CONFIG[job.priority] || PRIORITY_CONFIG.medium;
                    const pct = job.target_count ? Math.min(100, Math.round((job.submissions / job.target_count) * 100)) : 0;
                    return (
                      <tr key={job.id} style={{ borderBottom: idx < recent_jobs.length - 1 ? '1px solid #f3f4f6' : 'none' }}>
                        <td style={{ padding: '10px 16px' }}>
                          <select
                            value={job.client_id || ''}
                            onChange={e => assignClient.mutate({ jobId: job.id, clientId: e.target.value || null })}
                            style={{ fontSize: 13, color: job.client_name ? '#111827' : '#9ca3af', border: '1px solid #e5e7eb', borderRadius: 6, padding: '5px 8px', background: '#fff', cursor: 'pointer', maxWidth: 140 }}
                          >
                            <option value="">— None —</option>
                            {clients.map(c => (
                              <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                          </select>
                        </td>
                        <td style={{ padding: '14px 16px' }}>
                          <div style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>{job.title || 'Untitled'}</div>
                          <div style={{ fontSize: 12, color: '#9ca3af' }}>{job.job_code}</div>
                        </td>
                        <td style={{ padding: '10px 16px' }}>
                          <select
                            value={job.priority || 'medium'}
                            onChange={e => updatePriority.mutate({ jobId: job.id, priority: e.target.value })}
                            style={{
                              fontSize: 11,
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              padding: '4px 8px',
                              borderRadius: 20,
                              border: `1px solid ${priority.color}50`,
                              background: priority.bg,
                              color: priority.color,
                              cursor: 'pointer',
                              outline: 'none',
                            }}
                          >
                            <option value="urgent">Urgent</option>
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                          </select>
                        </td>
                        <td style={{ padding: '14px 16px', fontSize: 13, color: '#374151' }}>
                          {job.assigned_employees?.length > 0
                            ? job.assigned_employees.join(', ')
                            : <span style={{ color: '#9ca3af' }}>—</span>}
                        </td>
                        <td style={{ padding: '14px 16px' }}>
                          <div style={{ fontSize: 14, fontWeight: 700, color: '#111827' }}>{job.submissions}</div>
                          <div style={{ height: 4, background: '#e5e7eb', borderRadius: 4, marginTop: 4, width: 60 }}>
                            <div style={{ height: '100%', background: '#00756a', borderRadius: 4, width: `${pct}%` }} />
                          </div>
                        </td>
                        <td style={{ padding: '14px 16px', fontSize: 13, color: '#374151' }}>{job.target_count || 1}</td>
                        <td style={{ padding: '14px 16px' }}>
                          <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 20, background: status.bg, color: status.color, fontWeight: 700, textTransform: 'uppercase' }}>
                            {status.label}
                          </span>
                        </td>
                        <td style={{ padding: '14px 16px' }}>
                          <button
                            onClick={() => navigate(`/jobs/${job.id}/assign`)}
                            style={{ background: '#f9fafb', color: '#374151', border: '1px solid #e5e7eb', borderRadius: 6, padding: '5px 12px', fontSize: 12, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}
                          >
                            Manage <ChevronRight size={12} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Recruiter Performance Tab */}
      {activeTab === 'employees' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 14 }}>
            <button
              onClick={() => navigate('/team')}
              style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#00756a', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
            >
              <UserPlus size={15} /> Add Employee
            </button>
          </div>
          {employee_metrics.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 60, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 12 }}>
              <Users size={32} style={{ opacity: 0.3, marginBottom: 10 }} />
              <div style={{ fontSize: 15 }}>No recruiters yet</div>
              <div style={{ fontSize: 13, marginTop: 4 }}>Add team members to start assigning JDs</div>
            </div>
          ) : (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                    {['Recruiter', 'Email', 'Assigned JDs', 'Candidates Submitted'].map(h => (
                      <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {employee_metrics.map((emp, idx) => (
                    <tr key={emp.id} style={{ borderBottom: idx < employee_metrics.length - 1 ? '1px solid #f3f4f6' : 'none' }}>
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#00756a20', color: '#00756a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700 }}>
                            {emp.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                          </div>
                          <span style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>{emp.name}</span>
                        </div>
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 13, color: '#6b7280' }}>{emp.email}</td>
                      <td style={{ padding: '14px 16px', fontSize: 14, fontWeight: 700, color: '#374151' }}>{emp.assigned_jds}</td>
                      <td style={{ padding: '14px 16px', fontSize: 14, fontWeight: 700, color: '#374151' }}>{emp.submissions}</td>
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
