import React from 'react';
import OnboardingChecklist from '@/components/people/OnboardingChecklist';
export default function OnboardingPage() {
  const items = [{label:'Complete paperwork',done:true},{label:'Set up laptop',done:true},{label:'Meet the team',done:false},{label:'First week training',done:false},{label:'30-day check-in',done:false}];
  return <div style={{ padding:'var(--spacing-8)', maxWidth:600, margin:'0 auto' }}><h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Employee Onboarding</h1><OnboardingChecklist items={items} /></div>;
}
