import React from 'react';
import { Bot, X } from 'lucide-react';

export default function CopilotDrawer({ isOpen, onClose }) {
  if (!isOpen) return null;
  return (
    <div style={{ position:'fixed', right:0, top:0, width:400, height:'100vh', background:'var(--color-surface)', borderLeft:'1px solid var(--color-border)', boxShadow:'var(--shadow-xl)', zIndex:'var(--z-overlay)', animation:'slideInRight 0.2s ease', display:'flex', flexDirection:'column' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'var(--spacing-4) var(--spacing-6)', borderBottom:'1px solid var(--color-border)' }}>
        <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)' }}><Bot size={20} style={{ color:'var(--color-primary)' }} /><h3 style={{ fontSize:'var(--text-base)', fontWeight:'var(--weight-semibold)' }}>AI Copilot</h3></div>
        <button onClick={onClose} style={{ color:'var(--color-text-muted)' }}><X size={18} /></button>
      </div>
      <div style={{ flex:1, padding:'var(--spacing-6)', display:'flex', alignItems:'center', justifyContent:'center', color:'var(--color-text-hint)' }}>
        <p>Ask me anything about your hiring pipeline...</p>
      </div>
    </div>
  );
}
