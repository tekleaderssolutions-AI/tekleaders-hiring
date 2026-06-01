import React from 'react';
import { Badge, Button } from '@/components/ui';
const integrations = [
  { name:'Slack', desc:'Post notifications to channels', connected:true },
  { name:'Google Calendar', desc:'Sync interview schedules', connected:true },
  { name:'LinkedIn', desc:'Import candidate profiles', connected:false },
  { name:'Greenhouse', desc:'Sync with your ATS', connected:false },
];
export default function IntegrationsPage() {
  return (
    <div className="settings-page"><div className="settings-content">
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-8)' }}>Integrations</h1>
      <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-4)' }}>
        {integrations.map((i) => (
          <div key={i.name} className="card" style={{ padding:'var(--spacing-5)', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <div><div style={{ fontWeight:'var(--weight-medium)' }}>{i.name}</div><div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>{i.desc}</div></div>
            {i.connected ? <Badge variant="success">Connected</Badge> : <Button variant="secondary" size="sm">Connect</Button>}
          </div>
        ))}
      </div>
    </div></div>
  );
}
