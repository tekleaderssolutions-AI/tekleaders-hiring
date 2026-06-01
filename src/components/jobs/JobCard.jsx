import React from 'react';
import { MapPin, Users, Clock } from 'lucide-react';
import { Badge } from '@/components/ui';

export default function JobCard({ job = {}, onClick }) {
  return (
    <div className="job-card" onClick={() => onClick?.(job)}>
      <div className="job-card-header">
        <div>
          <div className="job-card-title">{job.title || 'Untitled Position'}</div>
          <div className="job-card-company">{job.department || 'Engineering'}</div>
        </div>
        <Badge variant={job.status === 'active' ? 'success' : job.status === 'paused' ? 'warning' : 'neutral'} dot>{job.status || 'active'}</Badge>
      </div>
      <div style={{ display:'flex', gap:'var(--spacing-4)', fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>
        <span style={{ display:'flex', alignItems:'center', gap:4 }}><MapPin size={12} />{job.location || 'Remote'}</span>
        <span style={{ display:'flex', alignItems:'center', gap:4 }}><Clock size={12} />{job.type || 'Full-time'}</span>
      </div>
      <div className="job-card-stats">
        <div className="job-card-stat"><strong>{job.applicants || 0}</strong>Applicants</div>
        <div className="job-card-stat"><strong>{job.interviews || 0}</strong>Interviews</div>
        <div className="job-card-stat"><strong>{job.daysOpen || 0}</strong>Days Open</div>
      </div>
    </div>
  );
}
