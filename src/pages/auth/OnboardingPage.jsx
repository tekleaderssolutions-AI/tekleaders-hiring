import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Users, Briefcase, Palette, CheckCircle } from 'lucide-react';
import { Button, Input } from '@/components/ui';

const steps = [
  { id: 1, title: 'Company Info', icon: Building2 },
  { id: 2, title: 'Team Size', icon: Users },
  { id: 3, title: 'Hiring Needs', icon: Briefcase },
  { id: 4, title: 'Preferences', icon: Palette },
  { id: 5, title: 'Complete', icon: CheckCircle },
];

export default function OnboardingPage() {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  return (
    <div style={{ minHeight:'100vh', display:'flex', background:'var(--color-bg)' }}>
      {/* Sidebar progress */}
      <div style={{ width:280, background:'var(--gradient-sidebar)', padding:'var(--spacing-8)', display:'flex', flexDirection:'column', gap:'var(--spacing-4)' }}>
        <h2 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-xl)', fontWeight:'var(--weight-bold)', color:'#fff', marginBottom:'var(--spacing-8)' }}>Setup Wizard</h2>
        {steps.map((s) => (
          <div key={s.id} style={{ display:'flex', alignItems:'center', gap:'var(--spacing-3)', padding:'var(--spacing-3)', borderRadius:'var(--radius-lg)', background: step >= s.id ? 'rgba(102,126,234,0.15)' : 'transparent', color: step >= s.id ? 'var(--color-primary-light)' : 'var(--color-text-hint)' }}>
            <s.icon size={18} /><span style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-medium)' }}>{s.title}</span>
          </div>
        ))}
      </div>
      {/* Main content */}
      <div style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', padding:'var(--spacing-8)' }}>
        <div style={{ maxWidth:480, width:'100%' }}>
          <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-2)' }}>{steps[step-1].title}</h1>
          <p style={{ color:'var(--color-text-muted)', marginBottom:'var(--spacing-8)' }}>Step {step} of 5</p>
          {step === 1 && <><Input label="Company Name" placeholder="Acme Inc." /><Input label="Website" placeholder="https://acme.com" /></>}
          {step === 2 && <><Input label="Team Size" placeholder="e.g. 25" /><Input label="Department" placeholder="Engineering" /></>}
          {step === 3 && <><Input label="Roles to fill" placeholder="e.g. 5 engineers" /><Input label="Timeline" placeholder="Next 3 months" /></>}
          {step === 4 && <><Input label="ATS currently used" placeholder="e.g. Greenhouse" /></>}
          {step === 5 && <div style={{ textAlign:'center', padding:'var(--spacing-8)' }}><CheckCircle size={64} style={{ color:'var(--color-success)', margin:'0 auto var(--spacing-4)' }} /><h3 style={{ fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-2)' }}>All set!</h3><p style={{ color:'var(--color-text-muted)' }}>Your account is ready to go.</p></div>}
          <div style={{ display:'flex', justifyContent:'space-between', marginTop:'var(--spacing-8)' }}>
            {step > 1 && <Button variant="secondary" onClick={() => setStep(step - 1)}>Back</Button>}
            <div style={{ marginLeft:'auto' }}>
              {step < 5 ? <Button variant="primary" onClick={() => setStep(step + 1)}>Continue</Button>
                : <Button variant="primary" onClick={() => navigate('/dashboard')}>Go to Dashboard</Button>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
