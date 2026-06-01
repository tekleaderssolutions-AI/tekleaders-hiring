import React from 'react';
import { Shield, Key } from 'lucide-react';
import { Input, Button, Badge } from '@/components/ui';
export default function SecurityPage() {
  return (
    <div className="settings-page"><div className="settings-content">
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-8)' }}>Security</h1>
      <div className="settings-section">
        <h3 className="settings-section-title">Password</h3>
        <Input label="Current Password" type="password" />
        <Input label="New Password" type="password" />
        <Input label="Confirm New Password" type="password" />
        <Button variant="primary">Update Password</Button>
      </div>
      <div className="settings-section">
        <h3 className="settings-section-title">Two-Factor Authentication</h3>
        <div className="card" style={{ padding:'var(--spacing-5)', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <div style={{ display:'flex', gap:'var(--spacing-3)' }}><Shield size={20} style={{ color:'var(--color-success)' }} /><div><div style={{ fontWeight:'var(--weight-medium)', fontSize:'var(--text-sm)' }}>2FA Enabled</div><div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)' }}>Using authenticator app</div></div></div>
          <Badge variant="success">Active</Badge>
        </div>
      </div>
    </div></div>
  );
}
