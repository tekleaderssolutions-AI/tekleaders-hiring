import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, Zap, Shield, BarChart3, Users, Bot, Clock, Star, CheckCircle, Play } from 'lucide-react';
import { Avatar } from '@/components/ui';

/* ── Feature data ── */
const features = [
  { icon: Bot, title: 'AI Screening', desc: 'Automatically evaluate and rank candidates using advanced AI models trained on your requirements.' },
  { icon: Zap, title: 'Lightning Fast', desc: 'Reduce time-to-hire by 75% with automated pipelines and intelligent scheduling.' },
  { icon: Shield, title: 'Bias-Free Hiring', desc: 'Built-in fairness algorithms ensure equitable evaluation across all candidates.' },
  { icon: BarChart3, title: 'Deep Analytics', desc: 'Real-time dashboards with actionable insights on your hiring funnel performance.' },
  { icon: Users, title: 'Team Collaboration', desc: 'Shared scorecards, @mentions, and structured feedback for hiring committees.' },
  { icon: Clock, title: 'Smart Scheduling', desc: 'AI-powered interview scheduling that respects everyone\'s availability.' },
];

/* ── Testimonial data ── */
const testimonials = [
  { name: 'Sarah Chen', role: 'VP of Talent, TechCorp', text: 'Hirix cut our time-to-hire by 60%. The AI screening is incredibly accurate and saves our team dozens of hours each week.', rating: 5 },
  { name: 'Marcus Johnson', role: 'Head of HR, ScaleUp Inc', text: 'The best hiring platform we\'ve used. The pipeline analytics alone are worth the investment. Highly recommended!', rating: 5 },
  { name: 'Emily Rodriguez', role: 'Recruiter, InnovateCo', text: 'Finally a tool that actually understands what we need. The AI copilot feels like having an extra team member.', rating: 5 },
];

/* ── Scroll reveal hook ── */
function useScrollReveal() {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.add('revealed');
          observer.unobserve(el);
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  return ref;
}

function RevealSection({ children, className = '', delay = 0 }) {
  const ref = useScrollReveal();
  return (
    <div
      ref={ref}
      className={`scroll-reveal ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="landing">
      {/* ── Navbar ── */}
      <nav className="landing-nav">
        <Link to="/" className="landing-nav-logo">
          <Sparkles size={24} />
          <span>Hirix</span>
        </Link>
        <div className="landing-nav-links">
          <Link to="/login" className="landing-nav-link">Log in</Link>
          <Link to="/signup" className="landing-nav-cta">
            Get started <ArrowRight size={14} />
          </Link>
        </div>
      </nav>

      {/* ── Hero Section ── */}
      <section className="landing-hero">
        <div className="landing-hero-orb landing-hero-orb-1" />
        <div className="landing-hero-orb landing-hero-orb-2" />
        <div className="landing-hero-orb landing-hero-orb-3" />

        <div className="landing-hero-content">
          <div className="landing-hero-pill">
            <Sparkles size={14} />
            <span>AI-Powered Hiring Platform</span>
          </div>

          <h1 className="landing-hero-title">
            Hire the <span className="landing-gradient-text">best talent</span>{' '}
            with the power of AI
          </h1>

          <p className="landing-hero-desc">
            Automate screening, streamline interviews, and make data-driven
            hiring decisions. Hirix helps your team hire 10x faster.
          </p>

          <div className="landing-hero-actions">
            <Link to="/signup" className="landing-btn-primary">
              Get Started Free <ArrowRight size={18} />
            </Link>
            <button className="landing-btn-secondary">
              <Play size={16} fill="currentColor" /> Request a demo
            </button>
          </div>

          <div className="landing-hero-trust">
            <span><CheckCircle size={14} /> No credit card required</span>
            <span><CheckCircle size={14} /> 14-day free trial</span>
            <span><CheckCircle size={14} /> Cancel anytime</span>
          </div>
        </div>
      </section>

      {/* ── Features Section ── */}
      <section className="landing-section">
        <RevealSection>
          <div className="landing-section-header">
            <span className="landing-label">Features</span>
            <h2 className="landing-section-title">
              Everything your team<br />needs to hire at scale
            </h2>
          </div>
        </RevealSection>

        <div className="landing-features-grid">
          {features.map((f, i) => (
            <RevealSection key={f.title} delay={i * 80}>
              <div className="landing-feature-card">
                <div className="landing-feature-icon">
                  <f.icon size={24} />
                </div>
                <h3 className="landing-feature-title">{f.title}</h3>
                <p className="landing-feature-desc">{f.desc}</p>
              </div>
            </RevealSection>
          ))}
        </div>
      </section>

      {/* ── Testimonials Section ── */}
      <section className="landing-section landing-section-alt">
        <RevealSection>
          <div className="landing-section-header">
            <span className="landing-label">Testimonials</span>
            <h2 className="landing-section-title">
              Loved by hiring teams worldwide
            </h2>
          </div>
        </RevealSection>

        <div className="landing-testimonials-grid">
          {testimonials.map((t, i) => (
            <RevealSection key={t.name} delay={i * 100}>
              <div className="landing-testimonial-card">
                <div className="landing-stars">
                  {Array.from({ length: t.rating }).map((_, j) => (
                    <Star key={j} size={14} fill="var(--color-warning)" style={{ color: 'var(--color-warning)' }} />
                  ))}
                </div>
                <p className="landing-testimonial-text">"{t.text}"</p>
                <div className="landing-testimonial-author">
                  <Avatar name={t.name} size="sm" />
                  <div>
                    <div className="landing-testimonial-name">{t.name}</div>
                    <div className="landing-testimonial-role">{t.role}</div>
                  </div>
                </div>
              </div>
            </RevealSection>
          ))}
        </div>
      </section>

      {/* ── CTA Section ── */}
      <section className="landing-cta">
        <RevealSection>
          <div className="landing-cta-inner">
            <h2 className="landing-cta-title">Ready to transform your hiring?</h2>
            <p className="landing-cta-desc">
              Join thousands of teams already using Hirix to hire smarter and faster.
            </p>
            <div className="landing-cta-actions">
              <Link to="/signup" className="landing-btn-primary">
                Get Started Free <ArrowRight size={18} />
              </Link>
              <button className="landing-btn-secondary">
                Request a demo
              </button>
            </div>
          </div>
        </RevealSection>
      </section>

      {/* ── Footer ── */}
      <footer className="landing-footer">
        <div className="landing-footer-inner">
          <div className="landing-footer-brand">
            <div className="landing-nav-logo" style={{ marginBottom: 'var(--spacing-4)' }}>
              <Sparkles size={20} />
              <span>Hirix</span>
            </div>
            <p className="landing-footer-tagline">AI-powered hiring platform for modern teams.</p>
          </div>
          <div className="landing-footer-columns">
            <div className="landing-footer-col">
              <h4>Product</h4>
              {['Features', 'Integrations', 'Changelog'].map((l) => (
                <a key={l} href="#">{l}</a>
              ))}
            </div>
            <div className="landing-footer-col">
              <h4>Company</h4>
              {['About', 'Careers', 'Contact'].map((l) => (
                <a key={l} href="#">{l}</a>
              ))}
            </div>
          </div>
        </div>
        <div className="landing-footer-bottom">
          © 2026 Hirix. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
