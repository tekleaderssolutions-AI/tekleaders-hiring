import React from 'react';
import { Link } from 'react-router-dom';
import { Lock } from 'lucide-react';
import { Button, Input } from '@/components/ui';
export default function ResetPasswordPage() {
  return (
    <div style={{ minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center', background:'var(--gradient-hero)', padding:'var(--spacing-6)' }}>
      <div className="card" style={{ width:'100%', maxWidth:440, padding:'var(--spacing-10)' }}>
        <div style={{ textAlign:'center', marginBottom:'var(--spacing-8)' }}>
          <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-2)' }}>Set new password</h1>
          <p style={{ color:'var(--color-text-muted)', fontSize:'var(--text-sm)' }}>Enter your new password below</p>
        </div>
        <form onSubmit={(e) => e.preventDefault()}>
          <Input label="New Password" type="password" icon={Lock} placeholder="Min 8 characters" />
          <Input label="Confirm Password" type="password" icon={Lock} placeholder="••••••••" />
          <Button variant="primary" type="submit" style={{ width:'100%', marginTop:'var(--spacing-4)' }}>Reset Password</Button>
        </form>
      </div>
    </div>
  );
}
