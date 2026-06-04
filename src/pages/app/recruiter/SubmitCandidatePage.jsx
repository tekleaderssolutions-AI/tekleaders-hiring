import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import {
  ArrowLeft, Upload, FileText, X, CheckCircle, Loader2, Users,
  Phone, ClipboardCheck, MessageSquare, Star, UserCheck, Briefcase,
  Zap, BarChart2, CheckCircle2, AlertCircle, Mail
} from 'lucide-react';
import api from '@/lib/api';
import { useUploadCandidates, useBulkProgress } from '@/hooks/useCandidates';

function useJobDetails(jobId) {
  return useQuery({
    queryKey: ['job-details', jobId],
    queryFn: () => api.get(`/jobs/${jobId}`).then(r => r.data),
    enabled: !!jobId,
  });
}

function useMySubmissions(jobId) {
  return useQuery({
    queryKey: ['job-submissions', jobId],
    queryFn: () => api.get(`/submissions/job/${jobId}`).then(r => r.data),
    enabled: !!jobId,
  });
}

const PIPELINE_STAGES = [
  { id: 'ai_scan',    label: 'AI Scan',      Icon: Zap },
  { id: 'status',     label: 'Status',        Icon: BarChart2 },
  { id: 'assessment', label: 'Assessment',   Icon: ClipboardCheck },
  { id: 'interview',  label: 'Interview',    Icon: MessageSquare },
  { id: 'offer',      label: 'Offer',        Icon: Star },
  { id: 'hired',      label: 'Hired',        Icon: UserCheck },
];

const SCORE_CONFIG = (score) => {
  if (score >= 80) return { color: '#059669', bg: '#d1fae5', label: 'Strong' };
  if (score >= 65) return { color: '#2563eb', bg: '#dbeafe', label: 'Good' };
  if (score >= 45) return { color: '#d97706', bg: '#fef3c7', label: 'Partial' };
  return { color: '#dc2626', bg: '#fee2e2', label: 'Weak' };
};

const TOP_K_OPTIONS = [
  { value: 3,     label: 'Top 3' },
  { value: 5,     label: 'Top 5' },
  { value: 10,    label: 'Top 10' },
  { value: 'all', label: 'All' },
];

const SCORE_COMPONENTS = [
  { key: 'skills',          label: 'Skill Match',    color: '#7c3aed' },
  { key: 'experience',      label: 'Experience',     color: '#2563eb' },
  { key: 'semantic',        label: 'Semantic Fit',   color: '#0891b2' },
  { key: 'evidence_score',  label: 'Evidence',       color: '#059669' },
  { key: 'impact',          label: 'Impact',         color: '#d97706' },
  { key: 'domain_match',    label: 'Domain Match',   color: '#dc2626' },
  { key: 'seniority',       label: 'Seniority Fit',  color: '#7c3aed' },
];

function CandidateDetailPanel({ m }) {
  const bd = m.scoring_breakdown || {};
  const brief = m.candidate_brief || {};
  const exp = bd.experience || {};
  const stability = bd.stability || {};
  const progression = bd.progression || {};
  const depthMap = bd.skills?.skill_depth || {};

  return (
    <div style={{ marginTop: 16, borderTop: '1px solid #e5e7eb', paddingTop: 16, display: 'flex', flexDirection: 'column', gap: 18 }}>

      {/* AI Summary */}
      {m.match_summary && (
        <div style={{ padding: '12px 16px', background: '#f0fdf9', border: '1px solid #a7f3d0', borderRadius: 8 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: '#065f46', marginBottom: 5, textTransform: 'uppercase', letterSpacing: 0.6 }}>AI Assessment</div>
          <div style={{ fontSize: 13, color: '#065f46', lineHeight: 1.75 }}>{m.match_summary}</div>
        </div>
      )}

      {/* Experience Snapshot */}
      {(exp.years != null || exp.domain_years != null) && (
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>Experience</div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {exp.years != null && (
              <div style={{ padding: '10px 16px', background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 8, textAlign: 'center', minWidth: 72 }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#111827', lineHeight: 1 }}>{Number(exp.years).toFixed(0)}</div>
                <div style={{ fontSize: 10, color: '#6b7280', marginTop: 3 }}>Total yrs</div>
              </div>
            )}
            {exp.domain_years != null && (
              <div style={{ padding: '10px 16px', background: '#f0fdf9', border: '1px solid #a7f3d0', borderRadius: 8, textAlign: 'center', minWidth: 72 }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#00756a', lineHeight: 1 }}>{Number(exp.domain_years).toFixed(0)}</div>
                <div style={{ fontSize: 10, color: '#6b7280', marginTop: 3 }}>Domain yrs</div>
              </div>
            )}
            {exp.relevance_ratio != null && (
              <div style={{ padding: '10px 16px', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 8, textAlign: 'center', minWidth: 72 }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#2563eb', lineHeight: 1 }}>{Math.round(exp.relevance_ratio * 100)}%</div>
                <div style={{ fontSize: 10, color: '#6b7280', marginTop: 3 }}>Domain fit</div>
              </div>
            )}
            {(m.scoring_breakdown?.seniority?.level) && (
              <div style={{ padding: '10px 16px', background: '#faf5ff', border: '1px solid #ddd6fe', borderRadius: 8, textAlign: 'center', minWidth: 72 }}>
                <div style={{ fontSize: 13, fontWeight: 800, color: '#7c3aed', textTransform: 'capitalize', lineHeight: 1.2 }}>{m.scoring_breakdown.seniority.level}</div>
                <div style={{ fontSize: 10, color: '#6b7280', marginTop: 3 }}>Seniority</div>
              </div>
            )}
            {stability.avg_tenure != null && (
              <div style={{ padding: '10px 16px', background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: 8, textAlign: 'center', minWidth: 72 }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#c2410c', lineHeight: 1 }}>{Number(stability.avg_tenure).toFixed(1)}y</div>
                <div style={{ fontSize: 10, color: '#6b7280', marginTop: 3 }}>Avg tenure</div>
              </div>
            )}
            {progression.trend && (
              <div style={{ padding: '10px 16px', background: progression.trend === 'ascending' ? '#f0fdf9' : '#fefce8', border: `1px solid ${progression.trend === 'ascending' ? '#a7f3d0' : '#fde68a'}`, borderRadius: 8, textAlign: 'center', minWidth: 72 }}>
                <div style={{ fontSize: 13, fontWeight: 800, color: progression.trend === 'ascending' ? '#059669' : '#d97706', lineHeight: 1.2 }}>
                  {progression.trend === 'ascending' ? '↑ Rising' : progression.trend === 'descending' ? '↓ Declining' : '→ Flat'}
                </div>
                <div style={{ fontSize: 10, color: '#6b7280', marginTop: 3 }}>Career trend</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Why Shortlisted */}
      {(brief.reasons || []).length > 0 && (
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>
            Why Shortlisted
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {(brief.reasons || []).slice(0, 4).map((r, i) => (
              <div key={i} style={{ display: 'flex', gap: 10, fontSize: 13, color: '#1a3a2a', lineHeight: 1.7, padding: '8px 12px', background: '#f0fdf9', borderRadius: 7, borderLeft: '3px solid #00756a' }}>
                <span style={{ color: '#00756a', flexShrink: 0, fontWeight: 800 }}>{i + 1}.</span>
                <span>{r}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Strengths */}
      {(brief.strengths || []).length > 0 && (
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>
            Key Strengths
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {(brief.strengths || []).slice(0, 4).map((s, i) => (
              <div key={i} style={{ display: 'flex', gap: 10, fontSize: 13, color: '#1e3a5f', lineHeight: 1.7, padding: '8px 12px', background: '#eff6ff', borderRadius: 7, borderLeft: '3px solid #2563eb' }}>
                <span style={{ color: '#2563eb', flexShrink: 0, fontWeight: 800 }}>{i + 1}.</span>
                <span>{s}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Skill Analysis */}
      {((bd.skills?.matched || []).length > 0 || (bd.skills?.missing || []).length > 0) && (
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>
            Skill Analysis
            <span style={{ fontSize: 10, fontWeight: 400, color: '#6b7280', marginLeft: 6, textTransform: 'none' }}>
              {(bd.skills?.matched || []).length} matched · {(bd.skills?.missing || []).length} missing
            </span>
          </div>
          {(bd.skills?.matched || []).length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <div style={{ fontSize: 10, color: '#059669', fontWeight: 700, marginBottom: 5, textTransform: 'uppercase', letterSpacing: 0.4 }}>Matched</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {(bd.skills.matched || []).map(s => {
                  const depth = depthMap[s] || 0;
                  return (
                    <span key={s} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, color: '#059669', background: '#d1fae5', padding: '3px 9px', borderRadius: 5, fontWeight: 600 }}>
                      <CheckCircle2 size={10} />
                      {s}
                      {depth >= 2 && <span style={{ fontSize: 9, fontWeight: 700, color: '#065f46', background: '#a7f3d0', padding: '0 4px', borderRadius: 3 }}>×{depth}</span>}
                    </span>
                  );
                })}
              </div>
            </div>
          )}
          {(bd.skills?.missing || []).length > 0 && (
            <div>
              <div style={{ fontSize: 10, color: '#dc2626', fontWeight: 700, marginBottom: 5, textTransform: 'uppercase', letterSpacing: 0.4 }}>Missing</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {(bd.skills.missing || []).map(s => (
                  <span key={s} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, color: '#dc2626', background: '#fee2e2', padding: '3px 9px', borderRadius: 5, fontWeight: 600 }}>
                    <AlertCircle size={10} /> {s}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Gaps & Risks */}
      {(brief.gaps || []).length > 0 && (
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#dc2626', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>
            Gaps & Risks
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {(brief.gaps || []).slice(0, 4).map((g, i) => (
              <div key={i} style={{ display: 'flex', gap: 10, fontSize: 13, color: '#7f1d1d', lineHeight: 1.7, padding: '8px 12px', background: '#fef2f2', borderRadius: 7, borderLeft: '3px solid #dc2626' }}>
                <span style={{ flexShrink: 0, fontWeight: 800, color: '#dc2626' }}>{i + 1}.</span>
                <span>{g}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Review Flags */}
      {(m.review_flags || []).length > 0 && (
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#d97706', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>Review Flags</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
            {(m.review_flags || []).map((f, i) => (
              <div key={i} style={{ fontSize: 12, color: '#92400e', background: '#fef3c7', border: '1px solid #fde68a', padding: '7px 12px', borderRadius: 6, lineHeight: 1.6 }}>
                ⚑ {f}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function seniority_level(m) {
  return m.scoring_breakdown?.seniority?.level || null;
}

const STATUS_META = {
  pending:            { label: 'Invite Sent',        color: '#6b7280', bg: '#f3f4f6' },
  interested:         { label: 'Accepted Invite',    color: '#2563eb', bg: '#dbeafe' },
  not_interested:     { label: 'Declined',           color: '#dc2626', bg: '#fee2e2' },
  slot_pending:       { label: 'Picking Slot',       color: '#d97706', bg: '#fef3c7' },
  scheduled:          { label: 'Interview Scheduled',color: '#00756a', bg: '#d1fae5' },
  completed:          { label: 'Interview Done',     color: '#7c3aed', bg: '#f5f3ff' },
  selected:           { label: 'Selected',           color: '#059669', bg: '#dcfce7' },
  recruiter_rejected: { label: 'Rejected',           color: '#dc2626', bg: '#fee2e2' },
};

const fmtSlot = (iso) => {
  if (!iso) return '';
  return new Date(iso).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: true });
};

function WorkflowTab({ submissions, jobId, jobTitle, job }) {
  const DRAFT_KEY = `ai_scan_draft_${jobId}`;
  const qc = useQueryClient();

  const [init] = useState(() => {
    try {
      const raw = localStorage.getItem(`ai_scan_draft_${jobId}`);
      if (raw) {
        const d = JSON.parse(raw);
        return { results: d.results || null, meta: d.savedAt ? { savedAt: d.savedAt, topK: d.topK } : null, topK: d.topK || 10 };
      }
    } catch {}
    return { results: null, meta: null, topK: 10 };
  });

  const [activeStage, setActiveStage] = useState('ai_scan');
  const [scanResults, setScanResults] = useState(init.results);
  const [draftMeta, setDraftMeta] = useState(init.meta);
  const [scanning, setScanning] = useState(false);
  const [scanError, setScanError] = useState(null);
  const [topK, setTopK] = useState(init.topK);
  const [customKInput, setCustomKInput] = useState('');
  const [selectedCandidates, setSelectedCandidates] = useState(new Set());
  const [expandedInvId, setExpandedInvId] = useState(null);
  const [invFilter, setInvFilter] = useState('all');

  const { data: invData, refetch: refetchInvitations } = useQuery({
    queryKey: ['job-invitations', jobId],
    queryFn: () => api.get('/gmail/invitations', { params: { job_id: jobId } }).then(r => r.data),
    enabled: !!jobId,
    staleTime: 30_000,
  });
  const invitations = invData?.invitations || [];

  const updateInvStatus = useMutation({
    mutationFn: ({ id, status }) => api.patch(`/gmail/invitations/${id}/status`, { status }),
    onSuccess: () => refetchInvitations(),
  });

  const getEffectiveK = () => topK === 'custom' ? (parseInt(customKInput) || 10) : topK;

  const saveDraft = (results, k) => {
    try {
      localStorage.setItem(DRAFT_KEY, JSON.stringify({ results, topK: k, savedAt: new Date().toISOString() }));
    } catch {}
  };

  const clearDraft = () => {
    localStorage.removeItem(DRAFT_KEY);
    setScanResults(null);
    setDraftMeta(null);
    setSelectedCandidates(new Set());
  };

  const runScan = async () => {
    setScanning(true);
    setScanError(null);
    try {
      const k = getEffectiveK();
      const res = await api.get(`/matching/fetch-and-align/${jobId}`, { params: { top_k: k } });
      setScanResults(res.data);
      const meta = { savedAt: new Date().toISOString(), topK: k };
      setDraftMeta(meta);
      saveDraft(res.data, k);
      setSelectedCandidates(new Set());
    } catch (e) {
      setScanError(e?.response?.data?.detail || 'AI scan failed. Please try again.');
    } finally {
      setScanning(false);
    }
  };

  const toggleCandidate = (resumeId) => {
    setSelectedCandidates(prev => {
      const next = new Set(prev);
      if (next.has(resumeId)) next.delete(resumeId);
      else next.add(resumeId);
      return next;
    });
  };

  const allSelected = (scanResults?.matches?.length || 0) > 0 &&
    scanResults.matches.every(m => selectedCandidates.has(m.resume_id));

  const toggleAll = () => {
    if (allSelected) setSelectedCandidates(new Set());
    else setSelectedCandidates(new Set((scanResults?.matches || []).map(m => m.resume_id)));
  };

  const selectedMatches = (scanResults?.matches || []).filter(m => selectedCandidates.has(m.resume_id));

  // ── Gmail integration ────────────────────────────────────────────────────────
  const [sendingMail, setSendingMail] = useState(false);
  const [mailResult, setMailResult] = useState(null);
  const [showScheduler, setShowScheduler] = useState(false);
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('');
  const [scheduleDuration, setScheduleDuration] = useState(45);
  const [addMeet, setAddMeet] = useState(true);

  const handleSendMail = async () => {
    if (selectedMatches.length === 0) return;
    setSendingMail(true);
    setMailResult(null);
    try {
      // Collect matched skills from scan results as JD required skills
      const allMatchedSkills = [];
      if (scanResults?.matches?.length) {
        const skillSet = new Set();
        scanResults.matches.forEach(m => (m.skills?.matched || []).forEach(s => skillSet.add(s)));
        allMatchedSkills.push(...skillSet);
      }
      const body = {
        job_title: jobTitle,
        job_id: jobId,
        candidates: selectedMatches.map(m => ({ first_name: m.first_name || '', last_name: m.last_name || '', email: m.email })),
        jd_details: {
          description: job?.description || null,
          required_skills: allMatchedSkills.slice(0, 10),
          experience_years: null,
          location: null,
        },
      };
      const res = await api.post('/gmail/send-invite', body);
      setMailResult({ sent: res.data.sent?.length || 0, failed: res.data.failed?.length || 0 });
      qc.invalidateQueries({ queryKey: ['employee-dashboard'] });
    } catch (e) {
      setMailResult({ error: e?.response?.data?.detail || 'Failed to send emails' });
    } finally {
      setSendingMail(false);
    }
  };

  // Fetch busy slots when scheduler opens and a date is picked
  const { data: busyData } = useQuery({
    queryKey: ['calendar-busy', scheduleDate],
    queryFn: () => api.get(`/gmail/calendar/busy?date=${scheduleDate}`).then(r => r.data),
    enabled: showScheduler && !!scheduleDate,
    staleTime: 120_000,
  });
  const busySlots = busyData?.busy || [];

  const fmtDraftDate = (iso) => {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) +
      ' at ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
  };

  return (
    <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 14, overflow: 'hidden' }}>
      {/* Stage tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #e5e7eb', background: '#f9fafb', overflowX: 'auto' }}>
        {PIPELINE_STAGES.map((stage, idx) => {
          const isActive = stage.id === activeStage;
          const count = stage.id === 'ai_scan' && scanResults?.matches ? scanResults.matches.length
            : stage.id === 'status' ? invitations.length : 0;
          return (
            <button
              key={stage.id}
              onClick={() => setActiveStage(stage.id)}
              style={{
                flex: 1,
                minWidth: 110,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 6,
                padding: '18px 12px',
                border: 'none',
                background: isActive ? '#fff' : 'transparent',
                borderBottom: isActive ? '2px solid #00756a' : '2px solid transparent',
                borderRight: idx < PIPELINE_STAGES.length - 1 ? '1px solid #f3f4f6' : 'none',
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              <stage.Icon size={20} color={isActive ? '#00756a' : '#9ca3af'} strokeWidth={1.5} />
              <span style={{ fontSize: 12, fontWeight: isActive ? 700 : 500, color: isActive ? '#111827' : '#9ca3af', whiteSpace: 'nowrap' }}>
                {stage.label}
              </span>
              {count > 0 && (
                <span style={{ fontSize: 11, fontWeight: 700, background: isActive ? '#00756a' : '#e5e7eb', color: isActive ? '#fff' : '#6b7280', borderRadius: 20, padding: '1px 7px' }}>
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Stage content */}
      <div style={{ padding: 24, minHeight: 300 }}>
        {activeStage === 'ai_scan' ? (
          scanning ? (
            <div style={{ textAlign: 'center', padding: '48px 0' }}>
              <Loader2 size={40} color="#00756a" style={{ marginBottom: 16, animation: 'spin 1s linear infinite' }} />
              <div style={{ fontSize: 15, fontWeight: 600, color: '#065f46' }}>AI is ranking resumes against the JD…</div>
              <div style={{ fontSize: 13, color: '#9ca3af', marginTop: 6 }}>Analysing skills, experience, and fit</div>
              <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
          ) : scanResults ? (
            <div>
              {/* Draft banner */}
              {draftMeta && (
                <div style={{ background: '#fefce8', border: '1px solid #fde68a', borderRadius: 8, padding: '10px 16px', marginBottom: 14, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 13, color: '#92400e' }}>
                    Draft saved {fmtDraftDate(draftMeta.savedAt)} · Top {draftMeta.topK}
                  </span>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button onClick={clearDraft} style={{ background: 'none', border: '1px solid #fcd34d', color: '#92400e', borderRadius: 6, padding: '4px 12px', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>
                      Clear draft
                    </button>
                    <button onClick={runScan} style={{ background: 'none', border: '1px solid #00756a', color: '#00756a', borderRadius: 6, padding: '4px 12px', fontSize: 12, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Zap size={12} /> Re-run scan
                    </button>
                  </div>
                </div>
              )}

              {/* Stats bar */}
              <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
                {/* Select all */}
                <label style={{ display: 'flex', alignItems: 'center', gap: 7, cursor: 'pointer', fontSize: 13, fontWeight: 600, color: '#374151', padding: '10px 14px', background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 8, userSelect: 'none' }}>
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={toggleAll}
                    style={{ width: 15, height: 15, accentColor: '#00756a', cursor: 'pointer' }}
                  />
                  {allSelected ? 'Deselect all' : 'Select all'}
                </label>

                {[
                  { label: 'Total scanned', value: scanResults.stats.total },
                  { label: 'Matched', value: scanResults.stats.matched, color: '#059669' },
                  { label: 'Below threshold', value: scanResults.stats.filtered, color: '#dc2626' },
                ].map(s => (
                  <div key={s.label} style={{ background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 8, padding: '10px 16px', display: 'flex', gap: 8, alignItems: 'center' }}>
                    <span style={{ fontSize: 20, fontWeight: 800, color: s.color || '#111827' }}>{s.value}</span>
                    <span style={{ fontSize: 12, color: '#6b7280' }}>{s.label}</span>
                  </div>
                ))}

                {!draftMeta && (
                  <button
                    onClick={runScan}
                    style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6, background: 'transparent', border: '1px solid #00756a', color: '#00756a', borderRadius: 8, padding: '8px 16px', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
                  >
                    <Zap size={14} /> Re-scan
                  </button>
                )}
              </div>

              {/* Ranked candidates — always full detail */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {(scanResults.matches || []).map((m, rank) => {
                  const cfg = SCORE_CONFIG(m.composite_score);
                  const isSelected = selectedCandidates.has(m.resume_id);
                  return (
                    <div
                      key={m.resume_id}
                      style={{
                        border: `1.5px solid ${isSelected ? '#00756a' : rank === 0 ? '#a7f3d0' : rank < 3 ? '#d1fae5' : '#e5e7eb'}`,
                        borderRadius: 12, padding: '18px 22px',
                        background: isSelected ? '#f0fdf9' : rank === 0 ? '#fafffe' : '#fff',
                        transition: 'border-color 0.15s, background 0.15s',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
                        {/* Checkbox */}
                        <div style={{ paddingTop: 8 }}>
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleCandidate(m.resume_id)}
                            style={{ width: 16, height: 16, cursor: 'pointer', accentColor: '#00756a' }}
                          />
                        </div>

                        {/* Rank badge */}
                        <div style={{ width: 34, height: 34, borderRadius: '50%', background: rank < 3 ? '#00756a' : '#f3f4f6', color: rank < 3 ? '#fff' : '#6b7280', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 800, flexShrink: 0 }}>
                          #{rank + 1}
                        </div>

                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 3, flexWrap: 'wrap' }}>
                            <span style={{ fontSize: 15, fontWeight: 700, color: '#111827' }}>{m.first_name} {m.last_name}</span>
                            <span style={{ fontSize: 12, color: '#6b7280' }}>{m.role}</span>
                            {m.scoring_breakdown?.seniority?.level && (
                              <span style={{ fontSize: 11, padding: '2px 8px', background: '#f5f3ff', color: '#7c3aed', borderRadius: 20, fontWeight: 600, textTransform: 'capitalize' }}>
                                {m.scoring_breakdown.seniority.level}
                              </span>
                            )}
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 10, flexWrap: 'wrap' }}>
                            <span style={{ fontSize: 12, color: '#9ca3af' }}>{m.email}</span>
                            {m.phone && (
                              <span style={{ fontSize: 12, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                                <Phone size={11} color="#9ca3af" />{m.phone}
                              </span>
                            )}
                          </div>

                          {/* Score bar */}
                          <div style={{ marginBottom: 4 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                              <span style={{ fontSize: 11, color: '#6b7280' }}>Match score</span>
                              <span style={{ fontSize: 11, fontWeight: 700, color: cfg.color }}>{Math.round(m.composite_score)}% · {cfg.label}</span>
                            </div>
                            <div style={{ height: 6, background: '#f3f4f6', borderRadius: 4, overflow: 'hidden' }}>
                              <div style={{ height: '100%', background: cfg.color, borderRadius: 4, width: `${m.composite_score}%`, transition: 'width 0.5s' }} />
                            </div>
                          </div>

                          <CandidateDetailPanel m={m} />
                        </div>

                        {/* Score badge */}
                        <div style={{ textAlign: 'center', flexShrink: 0 }}>
                          <div style={{ fontSize: 26, fontWeight: 900, color: cfg.color, lineHeight: 1 }}>{Math.round(m.composite_score)}</div>
                          <div style={{ fontSize: 10, color: '#9ca3af', marginTop: 2 }}>/ 100</div>
                          <span style={{ display: 'inline-block', marginTop: 6, fontSize: 10, padding: '2px 8px', borderRadius: 20, background: cfg.bg, color: cfg.color, fontWeight: 700 }}>{cfg.label}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Scheduling panel modal */}
              {showScheduler && (
                <div style={{ position: 'fixed', inset: 0, zIndex: 300, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', background: 'rgba(0,0,0,0.35)' }} onClick={() => setShowScheduler(false)}>
                  <div style={{ background: '#fff', borderRadius: '16px 16px 0 0', width: '100%', maxWidth: 560, padding: '28px 32px 32px', boxShadow: '0 -8px 40px rgba(0,0,0,0.15)' }} onClick={e => e.stopPropagation()}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                      <div>
                        <div style={{ fontSize: 16, fontWeight: 700, color: '#111827' }}>Schedule Interview</div>
                        <div style={{ fontSize: 13, color: '#6b7280', marginTop: 2 }}>
                          For {selectedCandidates.size} candidate{selectedCandidates.size > 1 ? 's' : ''} · {jobTitle}
                        </div>
                      </div>
                      <button onClick={() => setShowScheduler(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 4 }}>
                        <X size={20} />
                      </button>
                    </div>

                    {/* Date + Time */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                      <div>
                        <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 6 }}>Date</label>
                        <input
                          type="date"
                          value={scheduleDate}
                          min={new Date().toISOString().split('T')[0]}
                          onChange={e => setScheduleDate(e.target.value)}
                          style={{ width: '100%', padding: '9px 12px', border: '1.5px solid #e5e7eb', borderRadius: 8, fontSize: 14, color: '#111827', outline: 'none', boxSizing: 'border-box' }}
                        />
                      </div>
                      <div>
                        <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 6 }}>Time</label>
                        <input
                          type="time"
                          value={scheduleTime}
                          onChange={e => setScheduleTime(e.target.value)}
                          style={{ width: '100%', padding: '9px 12px', border: '1.5px solid #e5e7eb', borderRadius: 8, fontSize: 14, color: '#111827', outline: 'none', boxSizing: 'border-box' }}
                        />
                      </div>
                    </div>

                    {/* Busy slots warning */}
                    {busySlots.length > 0 && (
                      <div style={{ background: '#fef3c7', border: '1px solid #fde68a', borderRadius: 8, padding: '8px 12px', marginBottom: 14, fontSize: 12, color: '#92400e' }}>
                        ⚠ You have {busySlots.length} existing event{busySlots.length > 1 ? 's' : ''} on this date — check availability before confirming.
                      </div>
                    )}

                    {/* Duration */}
                    <div style={{ marginBottom: 16 }}>
                      <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 8 }}>Duration</label>
                      <div style={{ display: 'flex', gap: 8 }}>
                        {[30, 45, 60, 90].map(d => (
                          <button
                            key={d}
                            onClick={() => setScheduleDuration(d)}
                            style={{ padding: '7px 14px', borderRadius: 7, border: '1.5px solid', borderColor: scheduleDuration === d ? '#00756a' : '#e5e7eb', background: scheduleDuration === d ? '#00756a' : '#fff', color: scheduleDuration === d ? '#fff' : '#374151', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
                          >
                            {d} min
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Google Meet toggle */}
                    <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', marginBottom: 24 }}>
                      <input type="checkbox" checked={addMeet} onChange={e => setAddMeet(e.target.checked)} style={{ width: 16, height: 16, accentColor: '#00756a' }} />
                      <span style={{ fontSize: 13, color: '#374151', fontWeight: 500 }}>Add Google Meet link</span>
                      <span style={{ fontSize: 11, color: '#9ca3af' }}>· Invite sent to candidate's calendar automatically</span>
                    </label>

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: 10 }}>
                      <button
                        onClick={() => handleSendMail(true)}
                        disabled={!scheduleDate || !scheduleTime || sendingMail}
                        style={{
                          flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                          background: scheduleDate && scheduleTime ? '#00756a' : '#e5e7eb',
                          color: scheduleDate && scheduleTime ? '#fff' : '#9ca3af',
                          border: 'none', borderRadius: 9, padding: '13px 0', fontSize: 14, fontWeight: 700,
                          cursor: scheduleDate && scheduleTime ? 'pointer' : 'not-allowed',
                        }}
                      >
                        {sendingMail ? <><Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> Sending…</> : <><Mail size={15} /> Send Invite + Schedule</>}
                      </button>
                      <button
                        onClick={() => handleSendMail(false)}
                        disabled={sendingMail}
                        style={{ padding: '13px 20px', background: '#fff', border: '1.5px solid #e5e7eb', borderRadius: 9, fontSize: 14, fontWeight: 600, color: '#374151', cursor: 'pointer' }}
                      >
                        Email only
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Fixed bottom action bar */}
              <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 200, background: '#fff', borderTop: `2px solid ${job?.status === 'closed' ? '#fca5a5' : '#e5e7eb'}`, boxShadow: '0 -4px 24px rgba(0,0,0,0.09)', padding: '14px 36px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
                {job?.status === 'closed' ? (
                  <>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#fee2e2', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <AlertCircle size={18} color="#dc2626" />
                      </div>
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 700, color: '#dc2626' }}>This job is closed — sending invites is disabled</div>
                        <div style={{ fontSize: 12, color: '#6b7280' }}>Change the job status to <strong>Open</strong> in the admin dashboard to send invites or schedule interviews.</div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button disabled style={{ display: 'flex', alignItems: 'center', gap: 7, background: '#f3f4f6', color: '#9ca3af', border: '1.5px solid #e5e7eb', borderRadius: 9, padding: '11px 20px', fontSize: 13, fontWeight: 600, cursor: 'not-allowed', opacity: 0.6 }}>
                        <Mail size={14} /> Send Invite
                      </button>
                      <button disabled style={{ display: 'flex', alignItems: 'center', gap: 7, background: '#e5e7eb', color: '#9ca3af', border: 'none', borderRadius: 9, padding: '11px 20px', fontSize: 13, fontWeight: 700, cursor: 'not-allowed', opacity: 0.6 }}>
                        <CheckCircle2 size={14} /> Schedule Interview
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      <span style={{ fontSize: 13 }}>
                        {selectedCandidates.size > 0 ? (
                          <><strong>{selectedCandidates.size}</strong> candidate{selectedCandidates.size > 1 ? 's' : ''} selected
                            <span style={{ fontWeight: 400, color: '#6b7280', marginLeft: 6 }}>— {selectedMatches.map(m => `${m.first_name} ${m.last_name}`.trim()).join(', ')}</span>
                          </>
                        ) : <span style={{ color: '#9ca3af' }}>Select candidates above to send an invite</span>}
                      </span>
                      {selectedCandidates.size > 0 && (
                        <span style={{ fontSize: 11, color: '#9ca3af' }}>
                          Candidate will receive a profile match email with Interested / Not Interested options. Slot selection and scheduling is fully automated.
                        </span>
                      )}
                      {mailResult && (
                        <span style={{ fontSize: 12, fontWeight: 600, color: mailResult.error ? '#dc2626' : '#059669' }}>
                          {mailResult.error ? `Error: ${mailResult.error}` : `✓ Sent ${mailResult.sent} invite${mailResult.sent !== 1 ? 's' : ''}${mailResult.failed > 0 ? ` · ${mailResult.failed} failed` : ''}`}
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button
                        onClick={handleSendMail}
                        disabled={selectedCandidates.size === 0 || sendingMail}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 7,
                          background: selectedCandidates.size > 0 ? '#f9fafb' : '#f3f4f6',
                          color: selectedCandidates.size > 0 ? '#374151' : '#9ca3af',
                          border: '1.5px solid #e5e7eb', borderRadius: 9, padding: '11px 20px',
                          fontSize: 13, fontWeight: 600,
                          cursor: selectedCandidates.size > 0 ? 'pointer' : 'not-allowed',
                        }}
                      >
                        {sendingMail ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> Sending…</> : <><Mail size={14} /> Send Invite</>}
                      </button>
                      <button
                        onClick={() => setShowScheduler(true)}
                        disabled={selectedCandidates.size === 0 || sendingMail}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 7,
                          background: selectedCandidates.size > 0 ? '#00756a' : '#e5e7eb',
                          color: selectedCandidates.size > 0 ? '#fff' : '#9ca3af',
                          border: 'none', borderRadius: 9, padding: '11px 20px', fontSize: 13, fontWeight: 700,
                          cursor: selectedCandidates.size > 0 ? 'pointer' : 'not-allowed',
                        }}
                      >
                        <CheckCircle2 size={14} /> Schedule Interview
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div style={{ padding: '40px 0', maxWidth: 480, margin: '0 auto' }}>
              {scanError && (
                <div style={{ marginBottom: 20, padding: '10px 16px', background: '#fee2e2', color: '#dc2626', borderRadius: 8, fontSize: 13 }}>{scanError}</div>
              )}
              <div style={{ textAlign: 'center', marginBottom: 28 }}>
                <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#00756a10', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px' }}>
                  <Zap size={28} color="#00756a" />
                </div>
                <div style={{ fontSize: 17, fontWeight: 700, color: '#111827', marginBottom: 6 }}>Run AI Scan</div>
                <div style={{ fontSize: 13, color: '#6b7280', lineHeight: 1.6 }}>
                  AI will analyse and rank resumes against this JD — showing match scores, detailed reasoning, skill gaps, and candidate briefs.
                </div>
              </div>

              {submissions.length === 0 ? (
                <div style={{ textAlign: 'center', fontSize: 13, color: '#9ca3af' }}>Upload resumes first from the "Upload Resumes" tab</div>
              ) : (
                <div style={{ background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 12, padding: '20px 24px' }}>
                  {/* Top K selector */}
                  <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 10 }}>
                      How many top candidates to analyse?
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
                      {[3, 5, 10, 20].map(n => (
                        <button
                          key={n}
                          onClick={() => { setTopK(n); setCustomKInput(''); }}
                          style={{
                            padding: '7px 16px', borderRadius: 7, border: '1.5px solid',
                            borderColor: topK === n ? '#00756a' : '#e5e7eb',
                            fontSize: 13, fontWeight: topK === n ? 700 : 500,
                            background: topK === n ? '#00756a' : '#fff',
                            color: topK === n ? '#fff' : '#374151',
                            cursor: 'pointer', transition: 'all 0.15s',
                          }}
                        >
                          Top {n}
                        </button>
                      ))}
                      <button
                        onClick={() => setTopK('custom')}
                        style={{
                          padding: '7px 16px', borderRadius: 7, border: '1.5px solid',
                          borderColor: topK === 'custom' ? '#00756a' : '#e5e7eb',
                          fontSize: 13, fontWeight: topK === 'custom' ? 700 : 500,
                          background: topK === 'custom' ? '#00756a' : '#fff',
                          color: topK === 'custom' ? '#fff' : '#374151',
                          cursor: 'pointer', transition: 'all 0.15s',
                        }}
                      >
                        Custom
                      </button>
                      {topK === 'custom' && (
                        <input
                          autoFocus
                          type="number"
                          min={1}
                          max={submissions.length}
                          value={customKInput}
                          onChange={e => setCustomKInput(e.target.value.replace(/\D/g, ''))}
                          placeholder={`1–${submissions.length}`}
                          style={{
                            width: 90, padding: '7px 12px', borderRadius: 7,
                            border: '1.5px solid #00756a', fontSize: 13, fontWeight: 600,
                            color: '#111827', outline: 'none', textAlign: 'center', background: '#fff',
                          }}
                        />
                      )}
                    </div>
                    <div style={{ fontSize: 12, color: '#6b7280', marginTop: 8 }}>
                      {topK === 'custom' && parseInt(customKInput) > 0
                        ? `Will fetch top ${Math.min(parseInt(customKInput), submissions.length)} of ${submissions.length} resumes`
                        : `Will fetch top ${topK} of ${submissions.length} resume${submissions.length !== 1 ? 's' : ''}`
                      }
                    </div>
                  </div>

                  <button
                    onClick={runScan}
                    disabled={topK === 'custom' && !parseInt(customKInput)}
                    style={{
                      width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                      background: (topK === 'custom' && !parseInt(customKInput)) ? '#9ca3af' : '#00756a',
                      color: '#fff', border: 'none', borderRadius: 9, padding: '13px 0',
                      fontSize: 14, fontWeight: 700,
                      cursor: (topK === 'custom' && !parseInt(customKInput)) ? 'not-allowed' : 'pointer',
                    }}
                  >
                    <Zap size={16} />
                    Run AI Scan · Top {topK === 'custom' ? (parseInt(customKInput) || '?') : topK} of {submissions.length} resumes
                  </button>
                </div>
              )}
            </div>
          )
        ) : activeStage === 'status' ? (
          <div>
            {invitations.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#9ca3af' }}>
                <Mail size={36} style={{ opacity: 0.2, marginBottom: 12 }} />
                <div style={{ fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 4 }}>No invites sent yet</div>
                <div style={{ fontSize: 13 }}>Run AI Scan and send invites — candidates will appear here with live status</div>
              </div>
            ) : (
              <div>
                {/* Filter chips */}
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 18 }}>
                  {['all', 'pending', 'interested', 'scheduled', 'completed', 'selected', 'not_interested', 'recruiter_rejected'].map(f => {
                    const cnt = f === 'all' ? invitations.length : invitations.filter(i => i.status === f).length;
                    if (f !== 'all' && cnt === 0) return null;
                    const sm = STATUS_META[f] || {};
                    const active = invFilter === f;
                    return (
                      <button key={f} onClick={() => setInvFilter(f)} style={{ padding: '5px 14px', borderRadius: 20, border: '1.5px solid', borderColor: active ? (sm.color || '#00756a') : '#e5e7eb', background: active ? (sm.bg || '#f0fdf9') : '#fff', color: active ? (sm.color || '#00756a') : '#6b7280', fontSize: 12, fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s' }}>
                        {f === 'all' ? 'All' : (sm.label || f)} · {cnt}
                      </button>
                    );
                  })}
                </div>
                {/* Candidate rows */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {(invFilter === 'all' ? invitations : invitations.filter(i => i.status === invFilter)).map(inv => {
                    const sm = STATUS_META[inv.status] || { label: inv.status, color: '#6b7280', bg: '#f3f4f6' };
                    const isExp = expandedInvId === inv.id;
                    const isScheduled = inv.status === 'scheduled';
                    const isCompleted = inv.status === 'completed';
                    const isFinal = ['selected', 'recruiter_rejected', 'not_interested'].includes(inv.status);
                    const initials = (inv.candidate_name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
                    return (
                      <div key={inv.id} style={{ border: `1.5px solid ${isExp ? sm.color : '#e5e7eb'}`, borderRadius: 10, background: isExp ? sm.bg : '#fff', overflow: 'hidden', transition: 'all 0.15s' }}>
                        {/* Row header */}
                        <div style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }} onClick={() => setExpandedInvId(isExp ? null : inv.id)}>
                          <div style={{ width: 38, height: 38, borderRadius: '50%', background: sm.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 800, color: sm.color, flexShrink: 0, border: `1.5px solid ${sm.color}40` }}>
                            {initials}
                          </div>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ fontSize: 14, fontWeight: 700, color: '#111827' }}>{inv.candidate_name}</div>
                            <div style={{ fontSize: 12, color: '#6b7280' }}>{inv.candidate_email}</div>
                          </div>
                          <div style={{ textAlign: 'right', flexShrink: 0 }}>
                            <span style={{ fontSize: 12, fontWeight: 700, color: sm.color, background: `${sm.bg}`, padding: '4px 10px', borderRadius: 20, display: 'inline-block', marginBottom: 4, border: `1px solid ${sm.color}30` }}>{sm.label}</span>
                            {isCompleted && <span style={{ fontSize: 11, color: '#7c3aed', background: '#f5f3ff', padding: '2px 7px', borderRadius: 10, marginLeft: 6 }}>{inv.slot_duration_minutes} min</span>}
                            <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 2 }}>{inv.created_at ? new Date(inv.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}</div>
                          </div>
                          <span style={{ fontSize: 11, color: '#9ca3af', flexShrink: 0 }}>{isExp ? '▲' : '▼'}</span>
                        </div>
                        {/* Expanded panel */}
                        {isExp && (
                          <div style={{ padding: '0 18px 18px', borderTop: '1px solid #f3f4f6' }}>
                            {/* Scheduled: Meet link */}
                            {isScheduled && (
                              <div style={{ marginTop: 14, padding: '14px 18px', background: '#f0fdf9', border: '1px solid #a7f3d0', borderRadius: 9, display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                                <div style={{ flex: 1 }}>
                                  <div style={{ fontSize: 12, fontWeight: 700, color: '#065f46', marginBottom: 4 }}>Interview Details</div>
                                  <div style={{ fontSize: 13, color: '#374151' }}>
                                    {inv.selected_slot ? `${fmtSlot(inv.selected_slot)} · ` : ''}{inv.slot_duration_minutes} min
                                  </div>
                                  {!inv.meet_link && <div style={{ fontSize: 12, color: '#6b7280', marginTop: 4 }}>No Meet link — interview may be in-person or link not generated yet</div>}
                                </div>
                                {inv.meet_link && (
                                  <a href={inv.meet_link} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 7, background: '#00756a', color: '#fff', padding: '10px 20px', borderRadius: 8, fontSize: 13, fontWeight: 700, textDecoration: 'none', flexShrink: 0 }}>
                                    Join Meet
                                  </a>
                                )}
                              </div>
                            )}
                            {/* Completed: duration */}
                            {isCompleted && (
                              <div style={{ marginTop: 14, padding: '14px 18px', background: '#f5f3ff', border: '1px solid #ddd6fe', borderRadius: 9 }}>
                                <div style={{ fontSize: 12, fontWeight: 700, color: '#7c3aed', marginBottom: 4 }}>Interview Completed</div>
                                <div style={{ fontSize: 13, color: '#374151' }}>
                                  Duration: <strong>{inv.slot_duration_minutes} minutes</strong>
                                  {inv.selected_slot && ` · ${fmtSlot(inv.selected_slot)}`}
                                </div>
                                {inv.meet_link && (
                                  <a href={inv.meet_link} target="_blank" rel="noopener noreferrer" style={{ fontSize: 12, color: '#7c3aed', display: 'inline-block', marginTop: 6 }}>View recording link</a>
                                )}
                              </div>
                            )}
                            {/* Non-final, non-scheduled/completed: show slot if any */}
                            {!isScheduled && !isCompleted && !isFinal && inv.selected_slot && (
                              <div style={{ marginTop: 14, padding: '10px 14px', background: '#fef3c7', border: '1px solid #fde68a', borderRadius: 8, fontSize: 13, color: '#92400e' }}>
                                Candidate selected slot: {fmtSlot(inv.selected_slot)}
                              </div>
                            )}
                            {/* Action buttons */}
                            {!isFinal && (
                              <div style={{ display: 'flex', gap: 7, marginTop: 14, flexWrap: 'wrap' }} onClick={e => e.stopPropagation()}>
                                {!isCompleted && (
                                  <button onClick={() => updateInvStatus.mutate({ id: inv.id, status: 'completed' })} disabled={updateInvStatus.isPending} style={{ padding: '7px 14px', fontSize: 12, fontWeight: 600, background: '#f5f3ff', color: '#7c3aed', border: '1px solid #ddd6fe', borderRadius: 7, cursor: 'pointer' }}>
                                    Mark Done
                                  </button>
                                )}
                                <button onClick={() => updateInvStatus.mutate({ id: inv.id, status: 'selected' })} disabled={updateInvStatus.isPending} style={{ padding: '7px 14px', fontSize: 12, fontWeight: 600, background: '#dcfce7', color: '#059669', border: '1px solid #86efac', borderRadius: 7, cursor: 'pointer' }}>
                                  Select Candidate
                                </button>
                                <button onClick={() => updateInvStatus.mutate({ id: inv.id, status: 'recruiter_rejected' })} disabled={updateInvStatus.isPending} style={{ padding: '7px 14px', fontSize: 12, fontWeight: 600, background: '#fee2e2', color: '#dc2626', border: '1px solid #fca5a5', borderRadius: 7, cursor: 'pointer' }}>
                                  Reject
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#9ca3af' }}>
            <Briefcase size={36} style={{ opacity: 0.2, marginBottom: 12 }} />
            <div style={{ fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 4 }}>No candidates in {PIPELINE_STAGES.find(s => s.id === activeStage)?.label}</div>
            <div style={{ fontSize: 13 }}>Candidates will appear here as they move through the pipeline</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function SubmitCandidatePage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const qc = useQueryClient();
  const fileInputRef = useRef(null);
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') === 'workflow' ? 'workflow' : 'upload');

  const { data: job } = useJobDetails(jobId);
  const { data: submissions = [] } = useMySubmissions(jobId);

  const [files, setFiles] = useState([]);
  const [bulkSessionId, setBulkSessionId] = useState(null);
  const [done, setDone] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [multiProgress, setMultiProgress] = useState(null);

  const uploadCandidates = useUploadCandidates();
  const { data: bulkProgress } = useBulkProgress(bulkSessionId);

  React.useEffect(() => {
    if (bulkProgress?.status === 'completed') {
      setBulkSessionId(null);
      setDone(true);
      qc.invalidateQueries({ queryKey: ['job-submissions', jobId] });
      qc.invalidateQueries({ queryKey: ['employee-dashboard'] });
    }
  }, [bulkProgress?.status]);

  const handleFiles = (incoming) => {
    const arr = Array.from(incoming).filter(f => /\.(pdf|doc|docx|zip)$/i.test(f.name));
    setFiles(arr);
    setDone(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleUpload = async () => {
    if (!files.length) return;
    setUploadError(null);

    // Single ZIP → existing bulk path
    if (files.length === 1 && files[0].name.toLowerCase().endsWith('.zip')) {
      const fd = new FormData();
      fd.append('file', files[0]);
      fd.append('job_code', job?.job_code || '');
      fd.append('job_id', jobId);
      try {
        const res = await uploadCandidates.mutateAsync({ formData: fd, jobCode: job?.job_code });
        if (res?.session_id) {
          setBulkSessionId(res.session_id);
        } else {
          setDone(true);
          qc.invalidateQueries({ queryKey: ['job-submissions', jobId] });
          qc.invalidateQueries({ queryKey: ['employee-dashboard'] });
        }
        setFiles([]);
      } catch (e) {
        setUploadError(e?.response?.data?.detail || 'Upload failed. Please try again.');
      }
      return;
    }

    // Single or multiple PDF/DOC/DOCX → upload sequentially
    const errors = [];
    const warnings = [];
    for (let i = 0; i < files.length; i++) {
      setMultiProgress({ current: i + 1, total: files.length, name: files[i].name });
      const fd = new FormData();
      fd.append('file', files[i]);
      fd.append('job_code', job?.job_code || '');
      fd.append('job_id', jobId);
      try {
        const res = await uploadCandidates.mutateAsync({ formData: fd, jobCode: job?.job_code });
        const sub = res?.submission;
        if (sub?.status === 'duplicate_self') {
          warnings.push(`"${sub.message}" is already in your submissions for this JD.`);
        } else if (sub?.status === 'duplicate_other') {
          warnings.push(`"${sub.message}" was already submitted by ${sub.submitted_by} for this JD.`);
        }
      } catch (e) {
        const detail = e?.response?.data?.detail || 'Parse failed';
        errors.push(`${files[i].name}: ${detail}`);
      }
    }

    setMultiProgress(null);
    setFiles([]);
    setDone(true);
    qc.invalidateQueries({ queryKey: ['job-submissions', jobId] });
    qc.invalidateQueries({ queryKey: ['employee-dashboard'] });
    const allMessages = [...errors.map(m => `❌ ${m}`), ...warnings.map(m => `⚠ ${m}`)];
    if (allMessages.length > 0) setUploadError(allMessages.join('\n'));
  };

  const isPending = uploadCandidates.isPending;
  const isProcessing = !!bulkSessionId && bulkProgress && bulkProgress.status !== 'completed';

  const TABS = [
    { id: 'upload',   label: 'Upload Resumes' },
    { id: 'workflow', label: `Workflow ${submissions.length > 0 ? `(${submissions.length})` : ''}` },
  ];

  return (
    <div style={{ padding: '28px 36px', paddingBottom: 90 }}>
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, color: '#6b7280', fontSize: 14, marginBottom: 20 }}
      >
        <ArrowLeft size={16} /> Back
      </button>

      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111827', margin: 0 }}>
          {job?.current_title || 'Submit Candidates'}
        </h1>
        <p style={{ color: '#6b7280', fontSize: 14, marginTop: 4 }}>
          {job?.job_code}{job?.job_code ? ' · ' : ''}Submit candidate resumes for this role
        </p>
      </div>

      {/* Tab bar */}
      <div style={{ display: 'flex', borderBottom: '2px solid #e5e7eb', marginBottom: 24 }}>
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: 1,
              padding: '14px 0',
              border: 'none',
              background: activeTab === tab.id ? '#f0fdf9' : 'transparent',
              fontSize: 14,
              fontWeight: activeTab === tab.id ? 700 : 500,
              color: activeTab === tab.id ? '#00756a' : '#6b7280',
              borderBottom: activeTab === tab.id ? '2px solid #00756a' : '2px solid transparent',
              cursor: 'pointer',
              marginBottom: -2,
              textAlign: 'center',
              letterSpacing: 0.2,
              transition: 'all 0.15s',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Upload Resumes Tab */}
      {activeTab === 'upload' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 28 }}>
          <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 14, padding: 28 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 6 }}>Upload Resumes</h2>
            <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 24 }}>
              Select one or multiple PDF / DOC / DOCX · or a ZIP for bulk upload
            </p>

            {done ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <CheckCircle size={52} color="#059669" style={{ marginBottom: 14 }} />
                <div style={{ fontSize: 18, fontWeight: 700, color: '#111827', marginBottom: 6 }}>Upload Complete!</div>
                <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 8 }}>Resumes have been parsed and submitted.</div>
                {uploadError && (
                  <div style={{ marginBottom: 16, padding: '10px 14px', background: uploadError.includes('❌') ? '#fee2e2' : '#fef3c7', color: uploadError.includes('❌') ? '#dc2626' : '#92400e', borderRadius: 8, fontSize: 13, whiteSpace: 'pre-line', lineHeight: 1.7, textAlign: 'left' }}>{uploadError}</div>
                )}
                <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                  <button onClick={() => { setDone(false); setFiles([]); setUploadError(null); }} style={{ background: '#00756a', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 24px', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                    Upload More
                  </button>
                  <button onClick={() => setActiveTab('workflow')} style={{ background: '#fff', color: '#00756a', border: '1px solid #00756a', borderRadius: 8, padding: '10px 20px', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                    Save & Continue
                  </button>
                </div>
              </div>
            ) : multiProgress ? (
              <div style={{ padding: '24px 0' }}>
                <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                  <span style={{ fontSize: 14, fontWeight: 600, color: '#065f46', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Loader2 size={16} color="#00756a" style={{ animation: 'spin 1s linear infinite' }} />
                    Uploading {multiProgress.current} of {multiProgress.total}…
                  </span>
                  <span style={{ fontSize: 12, color: '#6b7280' }}>{multiProgress.current}/{multiProgress.total}</span>
                </div>
                <div style={{ height: 8, background: '#d1fae5', borderRadius: 6, overflow: 'hidden', marginBottom: 8 }}>
                  <div style={{ height: '100%', background: '#00756a', borderRadius: 6, width: `${Math.round((multiProgress.current / multiProgress.total) * 100)}%`, transition: 'width 0.3s' }} />
                </div>
                <div style={{ fontSize: 12, color: '#6b7280', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{multiProgress.name}</div>
              </div>
            ) : isPending ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <Loader2 size={40} color="#00756a" style={{ marginBottom: 12, animation: 'spin 1s linear infinite' }} />
                <div style={{ fontSize: 14, fontWeight: 600, color: '#065f46' }}>Parsing resume with AI...</div>
                <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>This may take ~30 seconds</div>
                <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
              </div>
            ) : isProcessing ? (
              <div style={{ padding: '20px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                  <span style={{ fontSize: 14, fontWeight: 600, color: '#065f46' }}>Processing bulk upload...</span>
                  <span style={{ fontSize: 13, color: '#6b7280' }}>{bulkProgress.processed} / {bulkProgress.total}</span>
                </div>
                <div style={{ height: 10, background: '#d1fae5', borderRadius: 6, overflow: 'hidden', marginBottom: 8 }}>
                  <div style={{ height: '100%', background: '#00756a', borderRadius: 6, width: `${Math.round((bulkProgress.processed / Math.max(bulkProgress.total, 1)) * 100)}%`, transition: 'width 0.4s' }} />
                </div>
                {bulkProgress.duplicates > 0 && <div style={{ fontSize: 12, color: '#9ca3af' }}>{bulkProgress.duplicates} duplicate(s) skipped</div>}
              </div>
            ) : (
              <>
                <div
                  onDrop={handleDrop}
                  onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    border: `2px dashed ${dragOver ? '#00756a' : '#d1d5db'}`,
                    borderRadius: 12, padding: '52px 24px', textAlign: 'center',
                    cursor: 'pointer', background: dragOver ? '#f0fdf9' : '#fafafa',
                    transition: 'all 0.2s', marginBottom: 20,
                  }}
                >
                  <input ref={fileInputRef} type="file" hidden multiple accept=".pdf,.doc,.docx,.zip" onChange={e => handleFiles(e.target.files)} />
                  <Upload size={40} color="#00756a" style={{ marginBottom: 14, opacity: 0.7 }} />
                  <div style={{ fontSize: 15, fontWeight: 600, color: '#374151', marginBottom: 6 }}>Click to browse or drag & drop</div>
                  <div style={{ fontSize: 13, color: '#9ca3af' }}>PDF · DOC · DOCX (multi-select OK) · ZIP (bulk)</div>
                </div>

                {uploadError && !done && (
                  <div style={{ marginBottom: 12, padding: '10px 14px', background: uploadError.includes('❌') ? '#fee2e2' : '#fef3c7', color: uploadError.includes('❌') ? '#dc2626' : '#92400e', borderRadius: 8, fontSize: 13, whiteSpace: 'pre-line', lineHeight: 1.7 }}>{uploadError}</div>
                )}

                {files.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20 }}>
                    {files.map((f, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', background: '#f0fdf9', border: '1px solid #a7f3d0', borderRadius: 8 }}>
                        <FileText size={16} color="#00756a" />
                        <span style={{ fontSize: 13, color: '#065f46', fontWeight: 500, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f.name}</span>
                        <span style={{ fontSize: 11, color: '#6b7280' }}>{(f.size / 1024).toFixed(0)} KB</span>
                        <button onClick={() => setFiles(prev => prev.filter((_, idx) => idx !== i))} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 2 }}>
                          <X size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <button
                  onClick={handleUpload}
                  disabled={!files.length}
                  style={{
                    width: '100%', background: '#00756a', color: '#fff', border: 'none',
                    borderRadius: 9, padding: '13px 0', fontSize: 15, fontWeight: 700,
                    cursor: files.length ? 'pointer' : 'not-allowed', opacity: files.length ? 1 : 0.45,
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  }}
                >
                  <Upload size={16} /> Upload {files.length > 1 ? `${files.length} Resumes` : '& Submit'}
                </button>
              </>
            )}
          </div>

          {/* Sidebar — recent submissions */}
          <div>
            <h2 style={{ fontSize: 15, fontWeight: 700, color: '#111827', marginBottom: 14 }}>
              My Submissions <span style={{ fontSize: 13, fontWeight: 400, color: '#6b7280' }}>({submissions.length})</span>
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {submissions.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '36px 16px', border: '2px dashed #e5e7eb', borderRadius: 12, color: '#9ca3af' }}>
                  <Users size={28} style={{ opacity: 0.3, marginBottom: 8 }} />
                  <div style={{ fontSize: 13, fontWeight: 600 }}>No submissions yet</div>
                </div>
              ) : submissions.map(sub => (
                <div key={sub.id} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: '12px 14px' }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>{sub.candidate_name}</div>
                  <div style={{ fontSize: 12, color: '#6b7280' }}>{sub.candidate_email}</div>
                  {(sub.skills || []).length > 0 && (
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
                      {(sub.skills || []).slice(0, 4).map(s => (
                        <span key={s} style={{ fontSize: 11, padding: '2px 6px', background: '#f3f4f6', borderRadius: 4, color: '#374151' }}>{s}</span>
                      ))}
                    </div>
                  )}
                  <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 6 }}>
                    {sub.submitted_at ? new Date(sub.submitted_at).toLocaleDateString('en-IN') : ''}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Workflow Tab */}
      {activeTab === 'workflow' && <WorkflowTab submissions={submissions} jobId={jobId} jobTitle={job?.current_title || 'this role'} job={job} />}
    </div>
  );
}
