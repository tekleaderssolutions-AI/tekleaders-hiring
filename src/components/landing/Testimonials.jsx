import React from 'react';
import { Star } from 'lucide-react';
import { Avatar } from '@/components/ui';

const testimonials = [
  { name:'Sarah Chen', role:'VP of Talent, TechCorp', text:'Hirix cut our time-to-hire by 60%. The AI screening is incredibly accurate and saves our team dozens of hours each week.', rating:5 },
  { name:'Marcus Johnson', role:'Head of HR, ScaleUp Inc', text:'The best hiring platform we\'ve used. The pipeline analytics alone are worth the investment. Highly recommended!', rating:5 },
  { name:'Emily Rodriguez', role:'Recruiter, InnovateCo', text:'Finally a tool that actually understands what we need. The AI copilot feels like having an extra team member.', rating:5 },
];

export default function Testimonials() {
  return (
    <section style={{ padding:'var(--spacing-24) var(--spacing-6)', background:'var(--color-bg)' }}>
      <div style={{ maxWidth:1200, margin:'0 auto' }}>
        <div style={{ textAlign:'center', marginBottom:'var(--spacing-16)' }}>
          <span style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-semibold)', color:'var(--color-primary)', textTransform:'uppercase', letterSpacing:'0.05em' }}>Testimonials</span>
          <h2 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-4xl)', fontWeight:'var(--weight-bold)', marginTop:'var(--spacing-3)' }}>Loved by hiring teams worldwide</h2>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(300px, 1fr))', gap:'var(--spacing-6)' }}>
          {testimonials.map((t) => (
            <div key={t.name} className="card" style={{ padding:'var(--spacing-8)' }}>
              <div style={{ display:'flex', gap:2, marginBottom:'var(--spacing-4)' }}>
                {Array.from({ length: t.rating }).map((_, i) => <Star key={i} size={16} fill="var(--color-warning)" style={{ color:'var(--color-warning)' }} />)}
              </div>
              <p style={{ fontSize:'var(--text-sm)', color:'var(--color-text-secondary)', lineHeight:'var(--leading-relaxed)', marginBottom:'var(--spacing-6)', fontStyle:'italic' }}>"{t.text}"</p>
              <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-3)' }}>
                <Avatar name={t.name} />
                <div>
                  <div style={{ fontWeight:'var(--weight-semibold)', fontSize:'var(--text-sm)' }}>{t.name}</div>
                  <div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
