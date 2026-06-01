import React from 'react';
import { X, Mail, Phone, MapPin } from 'lucide-react';
import { Avatar, Badge, Button, ScoreRing } from '@/components/ui';

export default function CandidateDrawer({ candidate, onClose }) {
  if (!candidate) return null;
  return (
    <div style={{ position:'fixed', right:0, top:0, width:440, height:'100vh', background:'var(--color-surface)', borderLeft:'1px solid var(--color-border)', boxShadow:'var(--shadow-xl)', zIndex:'var(--z-overlay)', animation:'slideInRight 0.2s ease', display:'flex', flexDirection:'column' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'var(--spacing-4) var(--spacing-6)', borderBottom:'1px solid var(--color-border)' }}>
        <h3 style={{ fontSize:'var(--text-base)', fontWeight:'var(--weight-semibold)' }}>Candidate Profile</h3>
        <button onClick={onClose} style={{ color:'var(--color-text-muted)' }}><X size={18} /></button>
      </div>
      <div style={{ flex:1, overflowY:'auto', padding:'var(--spacing-6)' }}>
        <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-4)', marginBottom:'var(--spacing-6)' }}>
          <Avatar name={candidate.name} size="xl" />
          <div>
            <h4 style={{ fontWeight:'var(--weight-semibold)' }}>{candidate.name}</h4>
            <p style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)' }}>{candidate.role}</p>
            <Badge variant="primary" style={{ marginTop:4 }}>{candidate.stage}</Badge>
          </div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-3)', fontSize:'var(--text-sm)', color:'var(--color-text-secondary)' }}>
          <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)' }}><Mail size={14} />{candidate.email || 'No email'}</div>
          <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)' }}><Phone size={14} />{candidate.phone || 'No phone'}</div>
          <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)' }}><MapPin size={14} />{candidate.location || 'Unknown'}</div>
        </div>
        {candidate.aiScore != null && (
          <div style={{ marginTop:'var(--spacing-6)', display:'flex', alignItems:'center', gap:'var(--spacing-4)' }}>
            <ScoreRing score={candidate.aiScore} size={64} />
            <div><div style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-medium)' }}>AI Match Score</div><div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>Based on job requirements</div></div>
          </div>
        )}
      </div>
      <div style={{ padding:'var(--spacing-4) var(--spacing-6)', borderTop:'1px solid var(--color-border)', display:'flex', gap:'var(--spacing-3)' }}>
        <Button variant="primary" style={{ flex:1 }}>Advance</Button>
        <Button variant="secondary" style={{ flex:1 }}>Reject</Button>
      </div>
    </div>
  );
}
