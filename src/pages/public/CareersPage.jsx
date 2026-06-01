import React from 'react';
import { useParams } from 'react-router-dom';
import { MapPin, Clock, Briefcase } from 'lucide-react';
import { Button, Badge } from '@/components/ui';
const mockJobs = [
  { id:1, title:'Senior Frontend Engineer', location:'Remote', type:'Full-time', dept:'Engineering' },
  { id:2, title:'Product Designer', location:'San Francisco', type:'Full-time', dept:'Design' },
  { id:3, title:'ML Engineer', location:'Remote', type:'Contract', dept:'AI' },
];
export default function CareersPage() {
  const { company } = useParams();
  return (
    <div style={{ maxWidth:800, margin:'0 auto', padding:'calc(80px + var(--spacing-12)) var(--spacing-6)' }}>
      <h1 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-3xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-2)' }}>Careers at {company || 'Hirix'}</h1>
      <p style={{ color:'var(--color-text-muted)', marginBottom:'var(--spacing-8)' }}>Join our mission to transform hiring.</p>
      <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-4)' }}>
        {mockJobs.map((job) => (
          <div key={job.id} className="card" style={{ padding:'var(--spacing-5)', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <div>
              <h3 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-2)' }}>{job.title}</h3>
              <div style={{ display:'flex', gap:'var(--spacing-4)', fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>
                <span style={{ display:'flex', alignItems:'center', gap:4 }}><MapPin size={12} />{job.location}</span>
                <span style={{ display:'flex', alignItems:'center', gap:4 }}><Clock size={12} />{job.type}</span>
                <span style={{ display:'flex', alignItems:'center', gap:4 }}><Briefcase size={12} />{job.dept}</span>
              </div>
            </div>
            <Button variant="primary" size="sm">Apply</Button>
          </div>
        ))}
      </div>
    </div>
  );
}
