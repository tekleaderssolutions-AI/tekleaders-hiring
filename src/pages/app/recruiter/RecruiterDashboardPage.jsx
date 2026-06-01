import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Clock, CheckCircle, ChevronRight, Users, Upload, X, Copy, Check, FileText, MapPin } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';

function useEmployeeDashboard() {
  return useQuery({
    queryKey: ['employee-dashboard'],
    queryFn: () => api.get('/employee/dashboard').then(r => r.data),
    staleTime: 0,
    refetchInterval: 15000,
    refetchOnWindowFocus: true,
  });
}

function useMyNotifications() {
  return useQuery({
    queryKey: ['my-notifications'],
    queryFn: () => api.get('/employee/notifications').then(r => r.data),
  });
}

function useJdDetails(jobId) {
  return useQuery({
    queryKey: ['jd-detail', jobId],
    queryFn: () => api.get(`/jobs/${jobId}`).then(r => r.data),
    enabled: !!jobId,
    staleTime: 60000,
  });
}

function JDDetailModal({ jobId, onClose }) {
  const { data: jd, isLoading } = useJdDetails(jobId);
  const [copied, setCopied] = useState(null);

  const naukriKeywords = useMemo(() => {
    if (!jd) return [];
    const title = jd.current_title || '';
    const must = (jd.must_have_skills || []).slice(0, 6);
    const kws = (jd.keywords || []).slice(0, 3);
    const all = [title, ...must, ...kws].filter(Boolean);
    return [...new Set(all)].slice(0, 10);
  }, [jd]);

  const copyKeyword = (kw) => {
    navigator.clipboard.writeText(kw).then(() => {
      setCopied(kw);
      setTimeout(() => setCopied(null), 1500);
    });
  };

  const copyAll = () => {
    navigator.clipboard.writeText(naukriKeywords.join(', ')).then(() => {
      setCopied('__all__');
      setTimeout(() => setCopied(null), 1500);
    });
  };

  return (
    <div
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div style={{ background: '#fff', borderRadius: 16, width: '100%', maxWidth: 680, maxHeight: '85vh', display: 'flex', flexDirection: 'column', boxShadow: '0 20px 60px rgba(0,0,0,0.2)' }}>
        {/* Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <FileText size={18} color="#00756a" />
              <span style={{ fontSize: 18, fontWeight: 700, color: '#111827' }}>{jd?.current_title || 'Job Description'}</span>
            </div>
            <div style={{ fontSize: 13, color: '#6b7280' }}>
              {jd?.job_code}{jd?.job_code && jd?.experience_level ? ' · ' : ''}{jd?.experience_level}
              {jd?.location ? ` · ${jd.location}` : ''}
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 4, borderRadius: 6 }}>
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div style={{ overflowY: 'auto', flex: 1, padding: '20px 24px' }}>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>Loading JD details...</div>
          ) : !jd ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>Job details not found</div>
          ) : (
            <>
              {/* Meta chips */}
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
                {jd.experience_min > 0 && (
                  <span style={{ fontSize: 12, padding: '4px 10px', background: '#f0fdf9', color: '#00756a', border: '1px solid #a7f3d0', borderRadius: 20 }}>
                    {jd.experience_min}{jd.experience_max ? `–${jd.experience_max}` : '+'} yrs exp
                  </span>
                )}
                {jd.employment_type && (
                  <span style={{ fontSize: 12, padding: '4px 10px', background: '#f3f4f6', color: '#374151', borderRadius: 20 }}>{jd.employment_type}</span>
                )}
                {jd.location && (
                  <span style={{ fontSize: 12, padding: '4px 10px', background: '#f3f4f6', color: '#374151', borderRadius: 20, display: 'flex', alignItems: 'center', gap: 4 }}>
                    <MapPin size={11} /> {jd.location}
                  </span>
                )}
              </div>

              {/* Description */}
              {jd.description && (
                <div style={{ marginBottom: 20 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>Job Description</div>
                  <div style={{ fontSize: 13, color: '#374151', lineHeight: 1.7, whiteSpace: 'pre-wrap', background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 8, padding: '14px 16px', maxHeight: 200, overflowY: 'auto' }}>
                    {jd.description}
                  </div>
                </div>
              )}

              {/* Must-have skills */}
              {(jd.must_have_skills || []).length > 0 && (
                <div style={{ marginBottom: 20 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>Required Skills</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {jd.must_have_skills.map(s => (
                      <span key={s} style={{ fontSize: 12, padding: '4px 10px', background: '#d1fae5', color: '#065f46', borderRadius: 20, fontWeight: 500 }}>{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Nice-to-have */}
              {(jd.nice_to_have_skills || []).length > 0 && (
                <div style={{ marginBottom: 20 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>Nice to Have</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {jd.nice_to_have_skills.map(s => (
                      <span key={s} style={{ fontSize: 12, padding: '4px 10px', background: '#dbeafe', color: '#1d4ed8', borderRadius: 20 }}>{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Naukri keywords */}
              {naukriKeywords.length > 0 && (
                <div style={{ background: '#fef9ec', border: '1px solid #fcd34d', borderRadius: 10, padding: '14px 16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: '#92400e' }}>
                      Suggested Naukri Search Keywords
                    </div>
                    <button
                      onClick={copyAll}
                      style={{ display: 'flex', alignItems: 'center', gap: 5, background: '#f59e0b', color: '#fff', border: 'none', borderRadius: 6, padding: '5px 12px', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
                    >
                      {copied === '__all__' ? <Check size={12} /> : <Copy size={12} />}
                      {copied === '__all__' ? 'Copied!' : 'Copy All'}
                    </button>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {naukriKeywords.map(kw => (
                      <button
                        key={kw}
                        onClick={() => copyKeyword(kw)}
                        title="Click to copy"
                        style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, padding: '4px 10px', background: copied === kw ? '#059669' : '#fff', color: copied === kw ? '#fff' : '#92400e', border: `1px solid ${copied === kw ? '#059669' : '#fcd34d'}`, borderRadius: 20, cursor: 'pointer', fontWeight: 500, transition: 'all 0.2s' }}
                      >
                        {copied === kw ? <Check size={10} /> : <Copy size={10} />} {kw}
                      </button>
                    ))}
                  </div>
                  <div style={{ fontSize: 11, color: '#b45309', marginTop: 8 }}>
                    Click any keyword to copy · Use these in Naukri / LinkedIn job search
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

const STATUS_COLOR = {
  open:     { label: 'Open',     color: '#059669', bg: '#d1fae5' },
  draft:    { label: 'Pending',  color: '#d97706', bg: '#fef3c7' },
  on_hold:  { label: 'On Hold',  color: '#d97706', bg: '#fef3c7' },
  closed:   { label: 'Closed',   color: '#6b7280', bg: '#f3f4f6' },
};

const PRIORITY_COLOR = {
  urgent: '#dc2626', high: '#ea580c', medium: '#2563eb', low: '#6b7280',
};

export default function RecruiterDashboardPage() {
  const { user } = useAuth();
  const { data, isLoading } = useEmployeeDashboard();
  const { data: notifData } = useMyNotifications();
  const navigate = useNavigate();
  const [viewingJdId, setViewingJdId] = useState(null);
  const { assigned_jds = [], summary = {}, my_submissions = 0 } = data || {};
  const notifications = notifData?.notifications || [];
  const unread_count = notifData?.unread_count || 0;
  const firstName = user?.first_name || 'Recruiter';

  return (
    <div style={{ padding: '28px 36px' }}>
      {viewingJdId && <JDDetailModal jobId={viewingJdId} onClose={() => setViewingJdId(null)} />}

      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: '#111827', margin: 0 }}>Hello {firstName}!</h1>
        <p style={{ color: '#6b7280', marginTop: 4, fontSize: 14 }}>Here are your active job assignments</p>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 28 }}>
        {[
          { label: 'Total Assigned', value: summary.total || 0, icon: Briefcase, color: '#00756a' },
          { label: 'Active JDs', value: summary.active || 0, icon: CheckCircle, color: '#059669' },
          { label: 'Pending JDs', value: summary.pending || 0, icon: Clock, color: '#d97706' },
          { label: 'My Submissions', value: my_submissions || 0, icon: Users, color: '#2563eb' },
        ].map(card => (
          <div key={card.label} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: '18px 20px', display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ width: 44, height: 44, borderRadius: 10, background: card.color + '15', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <card.icon size={20} color={card.color} />
            </div>
            <div>
              <div style={{ fontSize: 26, fontWeight: 800, color: '#111827', lineHeight: 1 }}>{card.value}</div>
              <div style={{ fontSize: 12, color: '#6b7280', marginTop: 3 }}>{card.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 24 }}>
        {/* JD Cards */}
        <div>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 14 }}>Assigned JDs</h2>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>Loading...</div>
          ) : assigned_jds.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 48, border: '2px dashed #e5e7eb', borderRadius: 12, color: '#9ca3af' }}>
              <Briefcase size={36} style={{ opacity: 0.3, marginBottom: 10 }} />
              <div style={{ fontSize: 15, fontWeight: 600 }}>No JDs found</div>
              <div style={{ fontSize: 13, marginTop: 4 }}>Ask your admin to create job descriptions for this company</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {assigned_jds.map(jd => {
                const status = STATUS_COLOR[jd.status] || STATUS_COLOR.draft;
                return (
                  <div
                    key={jd.job_id}
                    onClick={() => navigate(`/recruiter/jobs/${jd.job_id}/submit?tab=workflow`)}
                    style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: '20px 24px', cursor: 'pointer', transition: 'border-color 0.15s, box-shadow 0.15s' }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = '#00756a'; e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,117,106,0.1)'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = '#e5e7eb'; e.currentTarget.style.boxShadow = 'none'; }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                          {jd.priority && (
                            <span style={{ width: 8, height: 8, borderRadius: '50%', background: PRIORITY_COLOR[jd.priority] || '#6b7280', flexShrink: 0 }} />
                          )}
                          <span style={{ fontSize: 15, fontWeight: 700, color: '#00756a' }}>
                            {jd.title || 'Untitled'}
                          </span>
                          {jd.is_assigned && (
                            <span style={{ fontSize: 10, padding: '2px 7px', borderRadius: 20, background: '#d1fae5', color: '#065f46', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.3 }}>
                              Assigned
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: 12, color: '#9ca3af' }}>{jd.job_code} {jd.client_name ? `· ${jd.client_name}` : ''}</div>
                      </div>
                      <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 20, background: status.bg, color: status.color, fontWeight: 700, textTransform: 'uppercase' }}>
                        {status.label}
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', gap: 16 }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          <span style={{ fontSize: 11, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 0.5, fontWeight: 600 }}>Submitted</span>
                          <span style={{ fontSize: 18, fontWeight: 800, color: '#111827', lineHeight: 1 }}>{jd.my_submissions}</span>
                        </div>
                        <div style={{ width: 1, background: '#e5e7eb', margin: '2px 0' }} />
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          <span style={{ fontSize: 11, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 0.5, fontWeight: 600 }}>Shortlisted</span>
                          <span style={{ fontSize: 18, fontWeight: 800, color: jd.shortlisted > 0 ? '#059669' : '#111827', lineHeight: 1 }}>{jd.shortlisted ?? 0}</span>
                        </div>
                      </div>
                      <button
                        onClick={e => { e.stopPropagation(); navigate(`/recruiter/jobs/${jd.job_id}/submit`); }}
                        style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#00756a', color: '#fff', border: 'none', borderRadius: 7, padding: '7px 16px', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
                      >
                        <Upload size={14} /> Submit Candidate
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Notifications Panel */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: '#111827', margin: 0 }}>Notifications</h2>
              {unread_count > 0 && (
                <span style={{ background: '#dc2626', color: '#fff', borderRadius: 20, padding: '2px 8px', fontSize: 11, fontWeight: 700 }}>{unread_count} new</span>
              )}
            </div>
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
              {notifications.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 32, color: '#9ca3af', fontSize: 13 }}>No notifications</div>
              ) : (
                notifications.slice(0, 8).map((n, idx) => (
                  <div key={n.id} style={{ padding: '14px 16px', borderBottom: idx < Math.min(notifications.length, 8) - 1 ? '1px solid #f3f4f6' : 'none', background: !n.is_read ? '#f0fdf9' : '#fff' }}>
                    <div style={{ fontSize: 13, fontWeight: !n.is_read ? 700 : 500, color: '#111827', marginBottom: 2 }}>{n.title}</div>
                    <div style={{ fontSize: 12, color: '#6b7280' }}>{n.body}</div>
                    <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 4 }}>
                      {n.created_at ? new Date(n.created_at).toLocaleDateString('en-IN') : ''}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* My Progress */}
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 14 }}>My Progress</h2>
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: '20px 20px' }}>
              {assigned_jds.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '16px 0', color: '#9ca3af', fontSize: 13 }}>No JDs assigned yet</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {assigned_jds.map(jd => {
                    return (
                      <div key={jd.job_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 13, fontWeight: 600, color: '#111827' }}>{jd.title || 'Untitled'}</span>
                        <span style={{ fontSize: 16, fontWeight: 800, color: '#00756a' }}>{jd.my_submissions}</span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Overall total */}
              {assigned_jds.length > 0 && (
                <div style={{ marginTop: 18, paddingTop: 14, borderTop: '1px solid #f3f4f6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 13, color: '#6b7280' }}>Total submissions</span>
                  <span style={{ fontSize: 18, fontWeight: 800, color: '#00756a' }}>{my_submissions}</span>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 14 }}>Quick Actions</h2>
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
              {[
                { label: 'Submit a Candidate', desc: 'Add candidate to an assigned JD', onClick: () => assigned_jds[0] && navigate(`/recruiter/jobs/${assigned_jds[0].job_id}/submit`), color: '#00756a' },
                { label: 'View My Submissions', desc: 'Review candidates you submitted', onClick: () => navigate('/candidates'), color: '#2563eb' },
              ].map((action, idx) => (
                <button
                  key={action.label}
                  onClick={action.onClick}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px', background: 'none', border: 'none', borderBottom: idx === 0 ? '1px solid #f3f4f6' : 'none', cursor: 'pointer', textAlign: 'left' }}
                >
                  <div style={{ width: 36, height: 36, borderRadius: 8, background: action.color + '15', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <ChevronRight size={16} color={action.color} />
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#111827' }}>{action.label}</div>
                    <div style={{ fontSize: 12, color: '#9ca3af' }}>{action.desc}</div>
                  </div>
                  <ChevronRight size={14} color="#d1d5db" style={{ marginLeft: 'auto' }} />
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
