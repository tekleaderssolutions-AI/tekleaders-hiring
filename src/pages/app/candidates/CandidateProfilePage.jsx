import React from 'react';
import { useParams } from 'react-router-dom';
import { Avatar, Badge, ScoreRing } from '@/components/ui';
import AiEvaluationPanel from '@/components/candidates/AiEvaluationPanel';
import RequirementsChecklist from '@/components/candidates/RequirementsChecklist';
export default function CandidateProfilePage() {
  const { id } = useParams();
  return (
    <div style={{ padding:'var(--spacing-8)' }}>
      <div style={{ display:'flex', gap:'var(--spacing-6)', marginBottom:'var(--spacing-8)' }}>
        <Avatar name="Sarah Chen" size="xl" />
        <div><h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)' }}>Sarah Chen</h1><p style={{ color:'var(--color-text-muted)' }}>Senior Frontend Engineer</p><div style={{ display:'flex', gap:'var(--spacing-2)', marginTop:'var(--spacing-3)' }}><Badge variant="primary">Interview</Badge><Badge variant="info">AI Score: 92%</Badge></div></div>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'var(--spacing-6)' }}>
        <AiEvaluationPanel evaluation={{ overallScore:92, criteria:[{name:'Technical Skills',score:95},{name:'Experience',score:88},{name:'Culture Fit',score:90},{name:'Communication',score:85}] }} />
        <RequirementsChecklist requirements={[{label:'5+ years React experience',met:true},{label:'TypeScript proficiency',met:true},{label:'System design skills',met:true},{label:'Leadership experience',met:false}]} />
      </div>
    </div>
  );
}

