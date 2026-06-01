import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, FolderOpen, User, Mail, Phone, Briefcase, Search } from 'lucide-react';
import api from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';

function useJDs() {
  return useQuery({
    queryKey: ['jobs-files'],
    queryFn: () => api.get('/jobs').then(r => r.data),
  });
}

function useMyResumes() {
  return useQuery({
    queryKey: ['my-resumes'],
    queryFn: () => api.get('/candidates').then(r => r.data),
    staleTime: 0,
  });
}

function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function AdminFilesPage() {
  const { data: jobs = [], isLoading } = useJDs();

  return (
    <div style={{ padding: 'var(--spacing-8)' }}>
      <div style={{ marginBottom: 'var(--spacing-6)' }}>
        <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--weight-bold)' }}>Files</h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: 13, marginTop: 4 }}>Job descriptions uploaded by your team</p>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#9ca3af' }}>Loading...</div>
      ) : jobs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 80, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 12 }}>
          <FolderOpen size={36} style={{ opacity: 0.3, marginBottom: 12 }} />
          <div style={{ fontSize: 15 }}>No files yet</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>JDs created from the Jobs page will appear here</div>
        </div>
      ) : (
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Name</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job, idx) => (
                <tr key={job.id} style={{ borderBottom: idx < jobs.length - 1 ? '1px solid #f3f4f6' : 'none' }}>
                  <td style={{ padding: '13px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <FileText size={16} color="#00756a" style={{ flexShrink: 0 }} />
                      <span style={{ fontSize: 14, color: '#111827' }}>{job.current_title || 'Untitled JD'}</span>
                    </div>
                  </td>
                  <td style={{ padding: '13px 16px', fontSize: 13, color: '#6b7280' }}>{formatDate(job.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function RecruiterFilesPage() {
  const { data: resumes = [], isLoading } = useMyResumes();
  const [search, setSearch] = useState('');

  const filtered = resumes.filter(r => {
    const q = search.toLowerCase();
    return (
      r.name?.toLowerCase().includes(q) ||
      r.email?.toLowerCase().includes(q) ||
      r.resume_title?.toLowerCase().includes(q) ||
      (r.skills || []).some(s => s.toLowerCase().includes(q))
    );
  });

  return (
    <div style={{ padding: '28px 36px' }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111827', margin: 0 }}>My Uploaded Resumes</h1>
        <p style={{ color: '#6b7280', fontSize: 14, marginTop: 4 }}>Candidates you have submitted across all JDs</p>
      </div>

      {/* Stats bar */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: '#00756a15', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <FileText size={18} color="#00756a" />
          </div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 800, color: '#111827', lineHeight: 1 }}>{resumes.length}</div>
            <div style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>Total Resumes</div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div style={{ position: 'relative', marginBottom: 20, maxWidth: 360 }}>
        <Search size={15} color="#9ca3af" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by name, email, skill…"
          style={{ width: '100%', paddingLeft: 36, paddingRight: 12, height: 38, border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 13, outline: 'none', background: '#fff', boxSizing: 'border-box' }}
        />
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#9ca3af' }}>Loading...</div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 80, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 12 }}>
          <FolderOpen size={36} style={{ opacity: 0.3, marginBottom: 12 }} />
          <div style={{ fontSize: 15, fontWeight: 600 }}>No resumes yet</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>Resumes you upload via Submit Candidate will appear here</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {filtered.map(r => (
            <div key={r.id} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: '16px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                <div style={{ display: 'flex', gap: 14, flex: 1 }}>
                  {/* Avatar */}
                  <div style={{ width: 42, height: 42, borderRadius: '50%', background: '#00756a15', color: '#00756a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, fontWeight: 700, flexShrink: 0 }}>
                    {(r.name || '?').charAt(0).toUpperCase()}
                  </div>

                  {/* Info */}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 4 }}>
                      <span style={{ fontSize: 15, fontWeight: 700, color: '#111827' }}>{r.name || 'Unknown'}</span>
                      {r.resume_title && (
                        <span style={{ fontSize: 12, padding: '2px 8px', background: '#f0fdf9', color: '#00756a', borderRadius: 20, border: '1px solid #a7f3d0', fontWeight: 500 }}>
                          {r.resume_title}
                        </span>
                      )}
                      {r.experience_years > 0 && (
                        <span style={{ fontSize: 12, color: '#6b7280' }}>
                          <Briefcase size={11} style={{ display: 'inline', marginRight: 3 }} />
                          {Number(r.experience_years) % 1 === 0
                            ? `${r.experience_years}y`
                            : `${Math.floor(r.experience_years)}y ${Math.round((r.experience_years % 1) * 12)}m`} exp
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                      {r.email && (
                        <span style={{ fontSize: 12, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Mail size={11} /> {r.email}
                        </span>
                      )}
                      {r.phone && (
                        <span style={{ fontSize: 12, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Phone size={11} /> {r.phone}
                        </span>
                      )}
                    </div>

                    {(r.skills || []).length > 0 && (
                      <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginTop: 8 }}>
                        {(r.skills || []).slice(0, 6).map(s => (
                          <span key={s} style={{ fontSize: 11, padding: '2px 7px', background: '#f3f4f6', color: '#374151', borderRadius: 4 }}>{s}</span>
                        ))}
                        {r.skills.length > 6 && (
                          <span style={{ fontSize: 11, color: '#9ca3af' }}>+{r.skills.length - 6} more</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Date */}
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontSize: 11, color: '#9ca3af' }}>Uploaded</div>
                  <div style={{ fontSize: 12, color: '#374151', fontWeight: 500 }}>{formatDate(r.created_at)}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function FilesPage() {
  const { user } = useAuth();
  if (user?.role === 'recruiter') return <RecruiterFilesPage />;
  return <AdminFilesPage />;
}
