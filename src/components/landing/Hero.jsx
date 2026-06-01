import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui';

export default function Hero() {
  return (
    <section style={{
      position: 'relative', minHeight: '90vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--gradient-hero)', overflow: 'hidden', textAlign: 'center', padding: 'var(--spacing-8)',
    }}>
      {/* Decorative orbs */}
      <div style={{ position:'absolute', width:600, height:600, borderRadius:'50%', background:'radial-gradient(circle, rgba(102,126,234,0.15) 0%, transparent 70%)', top:'-20%', left:'-10%' }} />
      <div style={{ position:'absolute', width:500, height:500, borderRadius:'50%', background:'radial-gradient(circle, rgba(118,75,162,0.12) 0%, transparent 70%)', bottom:'-15%', right:'-5%' }} />
      <div style={{ position:'absolute', width:300, height:300, borderRadius:'50%', background:'radial-gradient(circle, rgba(79,172,254,0.1) 0%, transparent 70%)', top:'30%', right:'20%' }} />

      <div style={{ position: 'relative', maxWidth: 800, zIndex: 1 }} className="animate-fade-in-up">
        <div style={{ display:'inline-flex', alignItems:'center', gap:8, padding:'6px 16px', borderRadius:'var(--radius-full)', background:'rgba(102,126,234,0.1)', border:'1px solid rgba(102,126,234,0.2)', marginBottom:'var(--spacing-6)', fontSize:'var(--text-sm)', color:'var(--color-primary-light)' }}>
          <Sparkles size={14} />
          <span>AI-Powered Hiring Platform</span>
        </div>

        <h1 style={{ fontFamily:'var(--font-display)', fontSize:'clamp(2.5rem, 6vw, 4.5rem)', fontWeight:'var(--weight-extrabold)', lineHeight:1.1, marginBottom:'var(--spacing-6)', color:'#fff' }}>
          Hire the <span style={{ background:'var(--gradient-text)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>best talent</span> with the power of AI
        </h1>

        <p style={{ fontSize:'var(--text-lg)', color:'var(--color-text-secondary)', maxWidth:560, margin:'0 auto var(--spacing-8)', lineHeight:'var(--leading-relaxed)' }}>
          Automate screening, streamline interviews, and make data-driven hiring decisions. Hirix helps your team hire 10x faster.
        </p>

        <div style={{ display:'flex', gap:'var(--spacing-4)', justifyContent:'center', flexWrap:'wrap' }}>
          <Link to="/signup">
            <Button variant="primary" size="lg">
              Get Started Free <ArrowRight size={18} />
            </Button>
          </Link>
          <Link to="/pricing">
            <Button variant="secondary" size="lg">View Pricing</Button>
          </Link>
        </div>

        <div style={{ marginTop:'var(--spacing-10)', display:'flex', justifyContent:'center', gap:'var(--spacing-8)', color:'var(--color-text-muted)', fontSize:'var(--text-sm)' }}>
          <span>✓ No credit card required</span>
          <span>✓ 14-day free trial</span>
          <span>✓ Cancel anytime</span>
        </div>
      </div>
    </section>
  );
}
