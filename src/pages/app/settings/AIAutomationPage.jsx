import React from 'react';
import { Bot, Zap } from 'lucide-react';
export default function AIAutomationPage() {
  const automations = [
    { name:'Auto-screen new applicants', desc:'AI screens candidates when they apply', enabled:true },
    { name:'Smart interview scheduling', desc:'AI finds optimal slots', enabled:true },
    { name:'Auto-reject low scores', desc:'Reject candidates below 30% AI score', enabled:false },
    { name:'Weekly pipeline digest', desc:'Send AI summary every Monday', enabled:true },
  ];
  return (
    <div className="settings-page"><div className="settings-content">
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-8)' }}>AI Automation</h1>
      <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-4)' }}>
        {automations.map((a) => (
          <div key={a.name} className="card" style={{ padding:'var(--spacing-5)', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <div style={{ display:'flex', gap:'var(--spacing-3)' }}>
              <Bot size={20} style={{ color:'var(--color-primary)', marginTop:2 }} />
              <div><div style={{ fontWeight:'var(--weight-medium)', fontSize:'var(--text-sm)' }}>{a.name}</div><div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>{a.desc}</div></div>
            </div>
            <div style={{ width:44, height:24, borderRadius:12, background:a.enabled?'var(--color-primary)':'var(--color-bg-secondary)', cursor:'pointer', position:'relative', transition:'all var(--transition)' }}>
              <div style={{ width:18, height:18, borderRadius:'50%', background:'#fff', position:'absolute', top:3, left:a.enabled?23:3, transition:'left var(--transition)' }} />
            </div>
          </div>
        ))}
      </div>
    </div></div>
  );
}
