import React, { useState } from 'react';
import { Send, Bot } from 'lucide-react';
import AgentStatusCard from '@/components/ai/AgentStatusCard';

const mockMessages = [
  { id:1, role:'user', content:'Show me the top candidates for the Senior Engineer role' },
  { id:2, role:'ai', content:'Based on AI screening, here are the top 3 candidates for Senior Frontend Engineer:\n\n1. Sarah Chen — 92% match (5 yrs React, system design)\n2. David Park — 95% match (7 yrs full-stack)\n3. Maria Garcia — 88% match (4 yrs React, strong culture fit)\n\nWould you like me to schedule interviews with any of them?' },
];

export default function AICopilotPage() {
  const [input, setInput] = useState('');
  return (
    <div className="copilot-page">
      <div className="copilot-sidebar">
        <h3 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-4)' }}>Chat History</h3>
        {['Top candidates query','Interview scheduling','Pipeline analysis'].map((c,i) => (
          <div key={i} style={{ padding:'var(--spacing-2-5) var(--spacing-3)', borderRadius:'var(--radius-md)', fontSize:'var(--text-sm)', color:'var(--color-text-secondary)', cursor:'pointer', marginBottom:'var(--spacing-1)' }}>{c}</div>
        ))}
      </div>
      <div className="copilot-main">
        <div className="copilot-messages">
          {mockMessages.map((m) => (
            <div key={m.id} className={`message-bubble ${m.role}`} style={{ whiteSpace:'pre-line' }}>{m.content}</div>
          ))}
        </div>
        <div className="copilot-input-area">
          <div className="copilot-input-wrap">
            <Bot size={18} style={{ color:'var(--color-primary)', flexShrink:0 }} />
            <input className="copilot-input" placeholder="Ask the AI copilot..." value={input} onChange={(e) => setInput(e.target.value)} />
            <button className="btn btn-primary btn-sm"><Send size={16} /></button>
          </div>
        </div>
      </div>
      <div className="copilot-agents">
        <h3 style={{ fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-4)' }}>Agents</h3>
        <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-3)' }}>
          <AgentStatusCard agent={{ name:'Screening Agent', status:'active', task:'Processing candidates' }} />
          <AgentStatusCard agent={{ name:'Scheduler', status:'idle', task:'Waiting' }} />
          <AgentStatusCard agent={{ name:'Analytics', status:'active', task:'Report generation' }} />
        </div>
      </div>
    </div>
  );
}
