import React from 'react';
import { Key, Copy, Eye, EyeOff } from 'lucide-react';
import { Button, Badge } from '@/components/ui';
const keys = [
  { name:'Production API Key', key:'hx_live_...a8f3', created:'Apr 10, 2026', lastUsed:'2h ago', status:'active' },
  { name:'Development Key', key:'hx_test_...b2c1', created:'Mar 15, 2026', lastUsed:'5d ago', status:'active' },
];
export default function APIKeysPage() {
  return (
    <div className="settings-page"><div className="settings-content">
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-8)' }}>API Keys</h1>
      <Button variant="primary" style={{ marginBottom:'var(--spacing-6)' }}>Generate New Key</Button>
      <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-4)' }}>
        {keys.map((k) => (
          <div key={k.name} className="card" style={{ padding:'var(--spacing-5)' }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'var(--spacing-3)' }}>
              <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)' }}><Key size={16} style={{ color:'var(--color-primary)' }} /><span style={{ fontWeight:'var(--weight-medium)' }}>{k.name}</span></div>
              <Badge variant="success">{k.status}</Badge>
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)', padding:'var(--spacing-2) var(--spacing-3)', background:'var(--color-bg-secondary)', borderRadius:'var(--radius-md)', fontFamily:'var(--font-mono)', fontSize:'var(--text-sm)', color:'var(--color-text-muted)' }}>
              <span style={{ flex:1 }}>{k.key}</span>
              <button style={{ color:'var(--color-text-hint)' }}><Copy size={14} /></button>
            </div>
            <div style={{ display:'flex', gap:'var(--spacing-4)', marginTop:'var(--spacing-3)', fontSize:'var(--text-xs)', color:'var(--color-text-hint)' }}>
              <span>Created: {k.created}</span><span>Last used: {k.lastUsed}</span>
            </div>
          </div>
        ))}
      </div>
    </div></div>
  );
}
