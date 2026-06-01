import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Avatar } from '@/components/ui';

const MATCH_COLORS = {
  'Strong Match': '#00756a',
  'Good Match':   '#2563eb',
  'Fair Match':   '#d97706',
  'Weak Match':   '#dc2626',
};

const MATCH_BG = {
  'Strong Match': '#e6f4f1',
  'Good Match':   '#eff6ff',
  'Fair Match':   '#fef3c7',
  'Weak Match':   '#fee2e2',
};

function DimensionBar({ label, weight, score, color = '#00756a', extra }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#333' }}>{label}{extra ? <span style={{ fontSize: 11, color: '#9ca3af', fontWeight: 400, marginLeft: 4 }}>({extra})</span> : null}</span>
        <span style={{ fontSize: 12, color: '#888' }}>w:{weight}% · {score}%</span>
      </div>
      <div style={{ height: 6, backgroundColor: '#eee', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{
          height: '100%',
          width: `${score}%`,
          backgroundColor: color,
          borderRadius: 4,
          transition: 'width 0.5s ease',
        }} />
      </div>
    </div>
  );
}

export default function CandidateMatchCard({ candidate }) {
  const [expanded, setExpanded] = useState(false);

  const {
    first_name, last_name, email, phone, linkedin_url, role,
    composite_score, match_label, match_summary, scoring_breakdown,
    confidence, review_flags, candidate_brief,
  } = candidate;

  const name = `${first_name || ''} ${last_name || ''}`.trim() || 'Unknown';
  const breakdown = scoring_breakdown || {};
  const matchColor = MATCH_COLORS[match_label] || '#888';
  const matchBg    = MATCH_BG[match_label]    || '#f5f5f5';

  const dims = [
    { key: 'skills',     label: 'Skills',     color: '#00756a' },
    { key: 'experience', label: 'Experience',  color: '#00756a', extraFn: d => {
        if (d.domain_years > 0 && d.years > d.domain_years)
          return `${d.domain_years}y in domain / ${d.years}y total`;
        if (d.years) return `${d.years}y exp`;
        return null;
    }},
    { key: 'projects',   label: 'Projects',    color: '#3b82f6' },
    { key: 'education',  label: 'Education',   color: '#00756a' },
    { key: 'seniority',  label: 'Seniority',   color: '#00756a', extraFn: d => d.level ? d.level : null },
    { key: 'optimization', label: 'Optimization', color: '#7c3aed', extraFn: d => d.bonus > 0 ? `+${d.bonus}pts` : null },
    { key: 'ownership',    label: 'Ownership',    color: '#0891b2', extraFn: d => d.bonus > 0 ? `+${d.bonus}pts` : null },
    { key: 'achievements', label: 'Achievements', color: '#d97706', extraFn: d => d.bonus > 0 ? `+${d.bonus}pts` : null },
    { key: 'stability',    label: 'Stability',    color: '#059669', extraFn: d => d.avg_tenure > 0 ? `${d.avg_tenure}y avg tenure` : null },
  ];

  const matched    = breakdown.skills?.matched || [];
  const missing    = breakdown.skills?.missing || [];
  const skillDepth = breakdown.skills?.skill_depth || {};
  const progression = breakdown.progression || {};

  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: 12,
      padding: '20px 24px',
      backgroundColor: '#fff',
      marginBottom: 12,
    }}>
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, flex: 1, minWidth: 0 }}>
          <Avatar name={name} size="md" />
          <div style={{ minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span style={{ fontWeight: 700, fontSize: 15, color: '#111' }}>{name}</span>
              {role && <span style={{ fontSize: 12, color: '#666' }}>· {role}</span>}
              <span style={{
                fontSize: 11, fontWeight: 600, padding: '2px 8px',
                borderRadius: 20, color: matchColor, backgroundColor: matchBg,
              }}>
                {match_label}
              </span>
            </div>
            {/* Contact strip */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 3, flexWrap: 'wrap' }}>
              {email && (
                <a href={`mailto:${email}`} style={{ fontSize: 12, color: '#2563eb', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 3 }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                  {email}
                </a>
              )}
              {phone && (
                <a href={`tel:${phone}`} style={{ fontSize: 12, color: '#374151', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 3 }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                  {phone}
                </a>
              )}
              {linkedin_url && (
                <a href={linkedin_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 12, color: '#0077b5', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 3 }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>
                  LinkedIn
                </a>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4, flexWrap: 'wrap' }}>
              {match_summary && (
                <span style={{ fontSize: 12, color: '#4b5563', fontStyle: 'italic' }}>
                  {match_summary}
                </span>
              )}
              {confidence && (
                <span style={{
                  fontSize: 10, fontWeight: 700, padding: '1px 7px', borderRadius: 20,
                  letterSpacing: '0.05em', textTransform: 'uppercase',
                  color: confidence === 'high' ? '#065f46' : confidence === 'medium' ? '#92400e' : '#7f1d1d',
                  backgroundColor: confidence === 'high' ? '#d1fae5' : confidence === 'medium' ? '#fef3c7' : '#fee2e2',
                }}>
                  {confidence} confidence
                </span>
              )}
              {progression.trend === 'ascending' && (
                <span style={{
                  fontSize: 10, fontWeight: 700, padding: '1px 7px', borderRadius: 20,
                  color: '#065f46', backgroundColor: '#d1fae5',
                }}>
                  ↑ Growing Career
                </span>
              )}
              {progression.trend === 'descending' && (
                <span style={{
                  fontSize: 10, fontWeight: 700, padding: '1px 7px', borderRadius: 20,
                  color: '#92400e', backgroundColor: '#fef3c7',
                }}>
                  ↓ Declining Path
                </span>
              )}
            </div>
            {review_flags && review_flags.length > 0 && (
              <div style={{ marginTop: 5 }}>
                {review_flags.map((flag, i) => (
                  <div key={i} style={{
                    fontSize: 11, color: '#92400e', backgroundColor: '#fffbeb',
                    border: '1px solid #fde68a', borderRadius: 6,
                    padding: '2px 8px', marginTop: 3, display: 'inline-block', marginRight: 4,
                  }}>
                    ⚠ {flag}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Composite score */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: '#999', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 4 }}>
              Composite Score
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 120, height: 7, backgroundColor: '#eee', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${composite_score}%`,
                  backgroundColor: matchColor,
                  borderRadius: 4,
                }} />
              </div>
              <span style={{ fontSize: 18, fontWeight: 800, color: '#111' }}>{composite_score}%</span>
            </div>
          </div>
          <button
            onClick={() => setExpanded(v => !v)}
            style={{
              width: 32, height: 32, borderRadius: '50%', border: '1px solid #e5e7eb',
              background: '#f9fafb', display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', flexShrink: 0,
            }}
          >
            {expanded ? <ChevronUp size={16} color="#666" /> : <ChevronDown size={16} color="#666" />}
          </button>
        </div>
      </div>

      {/* ── Candidate Brief: Why Shortlisted / Strengths / Gaps ──────── */}
      {candidate_brief && (candidate_brief.reasons?.length > 0 || candidate_brief.strengths?.length > 0 || candidate_brief.gaps?.length > 0) && (
        <div style={{
          marginTop: 14,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: 12,
          paddingTop: 14,
          borderTop: '1px solid #f3f4f6',
        }}>
          {candidate_brief.reasons?.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#2563eb', letterSpacing: '0.06em', marginBottom: 6 }}>WHY SHORTLISTED</div>
              <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                {candidate_brief.reasons.map((r, i) => (
                  <li key={i} style={{ fontSize: 12, color: '#374151', marginBottom: 4, paddingLeft: 14, position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0, color: '#2563eb', fontWeight: 700 }}>·</span>
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {candidate_brief.strengths?.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#059669', letterSpacing: '0.06em', marginBottom: 6 }}>STRENGTHS</div>
              <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                {candidate_brief.strengths.map((s, i) => (
                  <li key={i} style={{ fontSize: 12, color: '#374151', marginBottom: 4, paddingLeft: 14, position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0, color: '#059669', fontWeight: 700 }}>✓</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {candidate_brief.gaps?.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#dc2626', letterSpacing: '0.06em', marginBottom: 6 }}>GAPS</div>
              <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                {candidate_brief.gaps.map((g, i) => (
                  <li key={i} style={{ fontSize: 12, color: '#374151', marginBottom: 4, paddingLeft: 14, position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0, color: '#dc2626', fontWeight: 700 }}>✗</span>
                    {g}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* ── Expanded breakdown ──────────────────────────────────────── */}
      {expanded && (
        <div style={{ marginTop: 20 }}>
          {/* Dimension bars — 2 columns */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 32px' }}>
            {dims.map(d => {
              const dim = breakdown[d.key];
              if (!dim) return null;
              return (
                <DimensionBar
                  key={d.key}
                  label={d.label}
                  weight={dim.weight}
                  score={dim.score}
                  color={d.color}
                  extra={d.extraFn ? d.extraFn(dim) : null}
                />
              );
            })}
          </div>

          {/* Skills tags */}
          {(matched.length > 0 || missing.length > 0) && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 16, borderTop: '1px solid #f3f4f6', paddingTop: 16 }}>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: '#00756a', letterSpacing: '0.06em', marginBottom: 8 }}>
                  MATCHED SKILLS
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {matched.slice(0, 8).map(s => {
                    const depth = skillDepth[s];
                    return (
                      <span key={s} style={{
                        fontSize: 12, padding: '3px 10px', borderRadius: 20,
                        border: '1px solid #a7f3d0', backgroundColor: '#f0fdf4', color: '#065f46', fontWeight: 500,
                        display: 'inline-flex', alignItems: 'center', gap: 4,
                      }}>
                        ✓ {s}
                        {depth >= 2 && (
                          <span style={{
                            fontSize: 10, background: '#00756a', color: '#fff',
                            borderRadius: 10, padding: '0 5px', fontWeight: 700,
                          }}>{depth} roles</span>
                        )}
                      </span>
                    );
                  })}
                </div>
              </div>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: '#dc2626', letterSpacing: '0.06em', marginBottom: 8 }}>
                  MISSING SKILLS
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {missing.slice(0, 6).map(s => (
                    <span key={s} style={{
                      fontSize: 12, padding: '3px 10px', borderRadius: 20,
                      border: '1px solid #fca5a5', backgroundColor: '#fff1f2', color: '#991b1b', fontWeight: 500,
                    }}>
                      {s}
                    </span>
                  ))}
                  {missing.length === 0 && (
                    <span style={{ fontSize: 12, color: '#9ca3af', fontStyle: 'italic' }}>None</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
