import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft, Mail, Phone, Briefcase, Calendar,
  ChevronDown, ChevronUp, ExternalLink
} from 'lucide-react';
import api from '@/lib/api';

function Avatar({ name, size = 64 }) {
  const initials = (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
  const colors = ['#00756a', '#2563eb', '#7c3aed', '#d97706', '#dc2626'];
  const color = colors[initials.charCodeAt(0) % colors.length];
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%',
      background: color, color: '#fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * 0.35, fontWeight: 800, flexShrink: 0,
    }}>
      {initials}
    </div>
  );
}

function SkillTag({ label, variant = 'default' }) {
  const styles = {
    default: { background: '#f3f4f6', color: '#374151', border: '1px solid #e5e7eb' },
    matched: { background: '#d1fae5', color: '#065f46', border: '1px solid #a7f3d0' },
  };
  const s = styles[variant] || styles.default;
  return (
    <span style={{ fontSize: 12, padding: '3px 10px', borderRadius: 20, fontWeight: 500, ...s }}>
      {label}
    </span>
  );
}

function WorkExperienceItem({ job, index }) {
  const [expanded, setExpanded] = useState(index === 0);
  const company = job.company || job.employer || job.organization || '';
  const title = job.title || job.role || job.position || '';
  const start = job.start_date || job.start || '';
  const end = job.end_date || job.end || 'Present';
  const desc = job.description || job.responsibilities || job.summary || '';

  return (
    <div style={{ borderLeft: '2px solid #e5e7eb', paddingLeft: 16, paddingBottom: 12 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#111827' }}>{title || 'Role'}</div>
          <div style={{ fontSize: 13, color: '#6b7280', marginTop: 2 }}>{company}</div>
          {(start || end) && (
            <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 2, display: 'flex', alignItems: 'center', gap: 4 }}>
              <Calendar size={11} /> {start}{start && end ? ' – ' : ''}{end}
            </div>
          )}
        </div>
        {desc && (
          <button onClick={() => setExpanded(v => !v)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 2, flexShrink: 0 }}>
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        )}
      </div>
      {expanded && desc && (
        <div style={{ fontSize: 12, color: '#6b7280', marginTop: 8, lineHeight: 1.7 }}>{desc}</div>
      )}
    </div>
  );
}

export default function CandidateProfilePage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: candidate, isLoading, error } = useQuery({
    queryKey: ['candidate-profile', id],
    queryFn: () => api.get(`/candidates/${id}`).then(r => r.data),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div style={{ padding: '40px 36px', color: '#6b7280', fontSize: 14 }}>
        Loading candidate…
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <div style={{ padding: '40px 36px' }}>
        <div style={{ color: '#dc2626', fontSize: 14 }}>Candidate not found.</div>
      </div>
    );
  }

  const resume = candidate.resume;
  const name = `${candidate.first_name || ''} ${candidate.last_name || ''}`.trim() || 'Unknown';
  const skills = resume?.skills || [];
  const experience = resume?.experience || [];
  const seniority = resume?.seniority || {};
  const submissions = candidate.submissions || [];

  return (
    <div style={{ padding: '28px 36px', maxWidth: 1100 }}>
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, color: '#6b7280', fontSize: 14, marginBottom: 24 }}
      >
        <ArrowLeft size={16} /> Back
      </button>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 20, marginBottom: 28, padding: '24px', background: '#fff', border: '1px solid #e5e7eb', borderRadius: 14 }}>
        <Avatar name={name} size={72} />
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: '#111827', margin: 0 }}>{name}</h1>
          {resume?.title && (
            <div style={{ fontSize: 15, color: '#6b7280', marginTop: 4 }}>{resume.title}</div>
          )}
          {seniority.level && (
            <span style={{ display: 'inline-block', marginTop: 6, fontSize: 12, padding: '2px 10px', background: '#f5f3ff', color: '#7c3aed', borderRadius: 20, fontWeight: 600, textTransform: 'capitalize' }}>
              {seniority.level}
            </span>
          )}
          {resume?.experience_years && (
            <span style={{ display: 'inline-block', marginTop: 6, marginLeft: 6, fontSize: 12, padding: '2px 10px', background: '#eff6ff', color: '#2563eb', borderRadius: 20, fontWeight: 600 }}>
              {Number(resume.experience_years).toFixed(0)} yrs exp
            </span>
          )}

          {/* Contact row */}
          <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', marginTop: 12 }}>
            {candidate.email && (
              <a href={`mailto:${candidate.email}`} style={{ fontSize: 13, color: '#2563eb', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 5 }}>
                <Mail size={13} /> {candidate.email}
              </a>
            )}
            {candidate.phone && (
              <a href={`tel:${candidate.phone}`} style={{ fontSize: 13, color: '#374151', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 5 }}>
                <Phone size={13} /> {candidate.phone}
              </a>
            )}
            {candidate.linkedin_url && (
              <a href={candidate.linkedin_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 13, color: '#0077b5', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 5 }}>
                <ExternalLink size={13} /> LinkedIn
              </a>
            )}
          </div>

          {resume?.uploaded_by && (
            <div style={{ marginTop: 10, fontSize: 12, color: '#9ca3af' }}>
              Added by <strong style={{ color: '#6b7280' }}>{resume.uploaded_by}</strong>
              {candidate.created_at && ` · ${new Date(candidate.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}`}
            </div>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>
        {/* Left column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* Skills */}
          {skills.length > 0 && (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 20 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Skills <span style={{ fontWeight: 400, color: '#9ca3af', textTransform: 'none' }}>· {skills.length}</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7 }}>
                {skills.map(s => <SkillTag key={s} label={s} />)}
              </div>
            </div>
          )}

          {/* Work Experience */}
          {experience.length > 0 && (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 20 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 16, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Work Experience <span style={{ fontWeight: 400, color: '#9ca3af', textTransform: 'none' }}>· {experience.length} roles</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {experience.map((job, i) => (
                  <WorkExperienceItem key={i} job={job} index={i} />
                ))}
              </div>
            </div>
          )}

          {/* Empty state */}
          {skills.length === 0 && experience.length === 0 && (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 32, textAlign: 'center', color: '#9ca3af' }}>
              <Briefcase size={32} style={{ opacity: 0.2, marginBottom: 10 }} />
              <div style={{ fontSize: 14 }}>No resume data available</div>
            </div>
          )}
        </div>

        {/* Right column — Job Submissions */}
        <div>
          <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 20 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 14, textTransform: 'uppercase', letterSpacing: 0.5 }}>
              Job Submissions <span style={{ fontWeight: 400, color: '#9ca3af', textTransform: 'none' }}>· {submissions.length}</span>
            </div>
            {submissions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '20px 0', color: '#9ca3af', fontSize: 13 }}>
                Not submitted to any JD yet
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {submissions.map(s => (
                  <div key={s.submission_id} style={{ padding: '12px 14px', background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 9 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#111827' }}>{s.job_title}</div>
                    {s.job_code && (
                      <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 1 }}>{s.job_code}</div>
                    )}
                    <div style={{ fontSize: 12, color: '#6b7280', marginTop: 4 }}>
                      by {s.recruiter_name || 'Unknown'}
                    </div>
                    {s.submitted_at && (
                      <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 3, display: 'flex', alignItems: 'center', gap: 3 }}>
                        <Calendar size={10} />
                        {new Date(s.submitted_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
