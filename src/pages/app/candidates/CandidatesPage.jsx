import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Users } from 'lucide-react';
import api from '@/lib/api';

function useCandidates() {
  return useQuery({
    queryKey: ['candidates'],
    queryFn: () => api.get('/candidates').then(r => r.data),
  });
}

const ROLE_AVATAR_COLORS = ['#00756a', '#2563eb', '#7c3aed', '#d97706', '#dc2626'];

function initials(name = '') {
  return name.split(' ').map(n => n[0] || '').join('').toUpperCase().slice(0, 2);
}

function avatarColor(name = '') {
  let h = 0;
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h);
  return ROLE_AVATAR_COLORS[Math.abs(h) % ROLE_AVATAR_COLORS.length];
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function CandidatesPage() {
  const navigate = useNavigate();
  const { data: candidates = [], isLoading } = useCandidates();

  return (
    <div className="candidates-page">
      <div className="candidates-header">
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--weight-bold)' }}>Candidates</h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)', marginTop: 4 }}>Global candidate database</p>
        </div>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#9ca3af' }}>Loading...</div>
      ) : candidates.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 80, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 12, marginTop: 24 }}>
          <Users size={36} style={{ opacity: 0.3, marginBottom: 12 }} />
          <div style={{ fontSize: 15 }}>No candidates yet</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>Upload resumes from the Candidates upload page</div>
        </div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Role / Title</th>
                <th>JD / Job</th>
                <th>Added By</th>
                <th>Date Added</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => {
                const color = avatarColor(c.name);
                return (
                  <tr
                    key={c.id}
                    onClick={() => navigate(`/candidates/${c.id}`)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{ width: 36, height: 36, borderRadius: '50%', background: color + '20', color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700, flexShrink: 0 }}>
                          {initials(c.name)}
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 14, color: '#111827' }}>{c.name}</div>
                          <div style={{ fontSize: 12, color: '#9ca3af' }}>{c.email}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ fontSize: 13, color: '#374151' }}>{c.resume_title || '—'}</td>
                    <td>
                      {c.jobs && c.jobs.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                          {c.jobs.map(j => (
                            <span
                              key={j.job_id}
                              title={j.title}
                              style={{
                                fontSize: 11, fontWeight: 600, padding: '3px 8px',
                                borderRadius: 20, background: '#e0f2fe', color: '#0369a1',
                                whiteSpace: 'nowrap', maxWidth: 160,
                                overflow: 'hidden', textOverflow: 'ellipsis', display: 'inline-block',
                              }}
                            >
                              {j.job_code ? `${j.job_code} · ${j.title}` : j.title}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span style={{ fontSize: 12, color: '#d1d5db' }}>—</span>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                        <div style={{ width: 26, height: 26, borderRadius: '50%', background: '#00756a20', color: '#00756a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, flexShrink: 0 }}>
                          {initials(c.added_by)}
                        </div>
                        <span style={{ fontSize: 13, color: '#374151', fontWeight: 500 }}>{c.added_by}</span>
                      </div>
                    </td>
                    <td style={{ fontSize: 13, color: '#6b7280' }}>{formatDate(c.created_at)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
