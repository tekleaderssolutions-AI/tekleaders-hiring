import React from 'react';
import { Avatar, Badge, Button } from '@/components/ui';
const members = [
  { name:'Demo User', email:'demo@hirix.com', role:'Admin' },
  { name:'Jane Smith', email:'jane@hirix.com', role:'Recruiter' },
  { name:'Bob Wilson', email:'bob@hirix.com', role:'Hiring Manager' },
];
export default function TeamSettingsPage() {
  return (
    <div className="settings-page"><div className="settings-content">
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-8)' }}>Team</h1>
      <Button variant="primary" style={{ marginBottom:'var(--spacing-6)' }}>Invite Member</Button>
      <div className="table-container"><table className="table"><thead><tr><th>Member</th><th>Role</th><th>Actions</th></tr></thead><tbody>
        {members.map((m) => <tr key={m.email}><td><div style={{ display:'flex', alignItems:'center', gap:8 }}><Avatar name={m.name} size="sm" /><div><div style={{ fontWeight:'var(--weight-medium)' }}>{m.name}</div><div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>{m.email}</div></div></div></td><td><Badge variant="primary">{m.role}</Badge></td><td><Button variant="ghost" size="sm">Edit</Button></td></tr>)}
      </tbody></table></div>
    </div></div>
  );
}
