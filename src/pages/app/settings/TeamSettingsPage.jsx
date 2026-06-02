import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { KeyRound, X } from 'lucide-react';
import { Avatar, Badge } from '@/components/ui';
import api from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import useUiStore from '@/store/uiStore';

function useEmployees() {
  return useQuery({
    queryKey: ['admin', 'employees'],
    queryFn: () => api.get('/admin/employees').then((r) => r.data),
  });
}

function useResetPassword(employeeId) {
  return useMutation({
    mutationFn: (new_password) =>
      api.post(`/admin/employees/${employeeId}/reset-password`, { new_password }).then((r) => r.data),
  });
}

function ResetPasswordModal({ employee, onClose }) {
  const addToast = useUiStore((s) => s.addToast);
  const reset = useResetPassword(employee.id);
  const [pw, setPw] = useState('');
  const [confirm, setConfirm] = useState('');
  const [err, setErr] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (pw.length < 8) { setErr('Minimum 8 characters'); return; }
    if (pw !== confirm) { setErr('Passwords do not match'); return; }
    try {
      await reset.mutateAsync(pw);
      addToast({ title: 'Password Reset', message: `Password for ${employee.name} has been reset.`, type: 'success' });
      onClose();
    } catch (ex) {
      setErr(ex?.response?.data?.detail || 'Reset failed');
    }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
    }}>
      <div style={{
        background: '#fff', borderRadius: 12, padding: 28, width: 380,
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)', position: 'relative'
      }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', cursor: 'pointer', color: '#6b7280' }}
        >
          <X size={18} />
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
          <KeyRound size={20} style={{ color: '#6366f1' }} />
          <div>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>Reset Password</h3>
            <p style={{ margin: 0, fontSize: 12, color: '#6b7280' }}>{employee.name} · {employee.email}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 5, color: '#374151' }}>
              New Password
            </label>
            <input
              type="password"
              className="form-input-custom"
              value={pw}
              onChange={(e) => { setPw(e.target.value); setErr(''); }}
              placeholder="Minimum 8 characters"
              autoComplete="new-password"
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 5, color: '#374151' }}>
              Confirm Password
            </label>
            <input
              type="password"
              className="form-input-custom"
              value={confirm}
              onChange={(e) => { setConfirm(e.target.value); setErr(''); }}
              placeholder="Repeat new password"
              autoComplete="new-password"
            />
          </div>
          {err && <p style={{ color: '#ef4444', fontSize: 12, margin: 0 }}>{err}</p>}
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 4 }}>
            <button
              type="button"
              onClick={onClose}
              style={{ padding: '8px 18px', borderRadius: 6, border: '1px solid #e5e7eb', background: '#fff', cursor: 'pointer', fontSize: 13, fontWeight: 600 }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={reset.isPending}
              style={{
                padding: '8px 18px', borderRadius: 6, border: 'none',
                background: '#6366f1', color: '#fff', cursor: 'pointer',
                fontSize: 13, fontWeight: 600, opacity: reset.isPending ? 0.7 : 1
              }}
            >
              {reset.isPending ? 'Resetting...' : 'Reset Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const ROLE_VARIANT = {
  admin: 'danger',
  recruiter: 'primary',
  hiring_manager: 'warning',
  interviewer: 'default',
};

export default function TeamSettingsPage() {
  const { user } = useAuth();
  const { data: employees = [], isLoading } = useEmployees();
  const [resetTarget, setResetTarget] = useState(null);

  const isAdmin = user?.role === 'admin';

  return (
    <div className="settings-page">
      <div className="settings-content">
        <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--weight-bold)', marginBottom: 'var(--spacing-8)' }}>
          Team
        </h1>

        {isLoading ? (
          <p style={{ color: '#6b7280' }}>Loading team members...</p>
        ) : employees.length === 0 ? (
          <p style={{ color: '#6b7280' }}>No team members yet.</p>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Role</th>
                  <th>Status</th>
                  {isAdmin && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {employees.map((m) => (
                  <tr key={m.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Avatar name={m.name} size="sm" />
                        <div>
                          <div style={{ fontWeight: 'var(--weight-medium)' }}>{m.name}</div>
                          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{m.email}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <Badge variant={ROLE_VARIANT[m.role] || 'default'}>
                        {m.role?.replace('_', ' ')}
                      </Badge>
                    </td>
                    <td>
                      <Badge variant={m.is_active ? 'success' : 'default'}>
                        {m.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    {isAdmin && (
                      <td>
                        <button
                          onClick={() => setResetTarget(m)}
                          style={{
                            display: 'inline-flex', alignItems: 'center', gap: 6,
                            padding: '5px 12px', borderRadius: 6, border: '1px solid #e5e7eb',
                            background: '#fff', cursor: 'pointer', fontSize: 12, fontWeight: 600, color: '#374151'
                          }}
                        >
                          <KeyRound size={13} />
                          Reset Password
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {resetTarget && (
          <ResetPasswordModal employee={resetTarget} onClose={() => setResetTarget(null)} />
        )}
      </div>
    </div>
  );
}
