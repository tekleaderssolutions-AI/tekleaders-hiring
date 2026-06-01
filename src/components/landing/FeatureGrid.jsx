import React from 'react';
import { Zap, Shield, BarChart3, Users, Bot, Clock } from 'lucide-react';

const features = [
  { icon: Bot, title: 'AI Screening', desc: 'Automatically evaluate and rank candidates using advanced AI models trained on your requirements.' },
  { icon: Zap, title: 'Lightning Fast', desc: 'Reduce time-to-hire by 75% with automated pipelines and intelligent scheduling.' },
  { icon: Shield, title: 'Bias-Free Hiring', desc: 'Built-in fairness algorithms ensure equitable evaluation across all candidates.' },
  { icon: BarChart3, title: 'Deep Analytics', desc: 'Real-time dashboards with actionable insights on your hiring funnel performance.' },
  { icon: Users, title: 'Team Collaboration', desc: 'Shared scorecards, @mentions, and structured feedback for hiring committees.' },
  { icon: Clock, title: 'Smart Scheduling', desc: 'AI-powered interview scheduling that respects everyone\'s availability.' },
];

export default function FeatureGrid() {
  return (
    <section style={{ padding:'var(--spacing-24) var(--spacing-6)', background:'var(--color-bg)' }}>
      <div style={{ maxWidth:1200, margin:'0 auto' }}>
        <div style={{ textAlign:'center', marginBottom:'var(--spacing-16)' }}>
          <span style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-semibold)', color:'var(--color-primary)', textTransform:'uppercase', letterSpacing:'0.05em' }}>Features</span>
          <h2 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-4xl)', fontWeight:'var(--weight-bold)', marginTop:'var(--spacing-3)', color:'var(--color-text)' }}>
            Everything your team needs to hire at scale
          </h2>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(340px, 1fr))', gap:'var(--spacing-6)' }}>
          {features.map((f) => (
            <div key={f.title} className="card" style={{ padding:'var(--spacing-8)' }}>
              <div style={{ width:48, height:48, borderRadius:'var(--radius-lg)', background:'rgba(102,126,234,0.1)', display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'var(--spacing-5)' }}>
                <f.icon size={24} style={{ color:'var(--color-primary)' }} />
              </div>
              <h3 style={{ fontSize:'var(--text-xl)', fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-3)' }}>{f.title}</h3>
              <p style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)', lineHeight:'var(--leading-relaxed)' }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
