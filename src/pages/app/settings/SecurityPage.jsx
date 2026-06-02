import React, { useState } from 'react';
import { Shield } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import useUiStore from '@/store/uiStore';

function useChangePassword() {
  return useMutation({
    mutationFn: (data) => api.patch('/auth/change-password', data).then((r) => r.data),
  });
}

export default function SecurityPage() {
  const addToast = useUiStore((s) => s.addToast);
  const changePassword = useChangePassword();

  const [form, setForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: '' }));
  };

  const validate = () => {
    const e = {};
    if (!form.current_password) e.current_password = 'Required';
    if (!form.new_password) e.new_password = 'Required';
    else if (form.new_password.length < 8) e.new_password = 'Minimum 8 characters';
    if (!form.confirm_password) e.confirm_password = 'Required';
    else if (form.new_password !== form.confirm_password) e.confirm_password = 'Passwords do not match';
    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }

    try {
      await changePassword.mutateAsync(form);
      addToast({ title: 'Password Updated', message: 'Your password has been changed successfully.', type: 'success' });
      setForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to update password';
      addToast({ title: 'Error', message: msg, type: 'error' });
    }
  };

  return (
    <div className="settings-page">
      <div className="settings-content">
        <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--weight-bold)', marginBottom: 'var(--spacing-8)' }}>
          Security
        </h1>

        {/* Change Password */}
        <div className="settings-section">
          <h3 className="settings-section-title">Change Password</h3>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 420 }}>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--color-text-secondary)' }}>
                Current Password
              </label>
              <input
                type="password"
                className="form-input-custom"
                value={form.current_password}
                onChange={(e) => handleChange('current_password', e.target.value)}
                placeholder="Enter current password"
                autoComplete="current-password"
              />
              {errors.current_password && (
                <p style={{ color: 'var(--color-error, #ef4444)', fontSize: 12, marginTop: 4 }}>{errors.current_password}</p>
              )}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--color-text-secondary)' }}>
                New Password
              </label>
              <input
                type="password"
                className="form-input-custom"
                value={form.new_password}
                onChange={(e) => handleChange('new_password', e.target.value)}
                placeholder="Minimum 8 characters"
                autoComplete="new-password"
              />
              {errors.new_password && (
                <p style={{ color: 'var(--color-error, #ef4444)', fontSize: 12, marginTop: 4 }}>{errors.new_password}</p>
              )}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--color-text-secondary)' }}>
                Confirm New Password
              </label>
              <input
                type="password"
                className="form-input-custom"
                value={form.confirm_password}
                onChange={(e) => handleChange('confirm_password', e.target.value)}
                placeholder="Repeat new password"
                autoComplete="new-password"
              />
              {errors.confirm_password && (
                <p style={{ color: 'var(--color-error, #ef4444)', fontSize: 12, marginTop: 4 }}>{errors.confirm_password}</p>
              )}
            </div>

            <button
              type="submit"
              className="ai-generate-btn"
              disabled={changePassword.isPending}
              style={{ alignSelf: 'flex-start', background: 'var(--color-primary, #6366f1)', opacity: changePassword.isPending ? 0.7 : 1 }}
            >
              {changePassword.isPending ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </div>

        {/* 2FA placeholder */}
        <div className="settings-section" style={{ marginTop: 32 }}>
          <h3 className="settings-section-title">Two-Factor Authentication</h3>
          <div className="card" style={{ padding: 'var(--spacing-5)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
              <Shield size={20} style={{ color: 'var(--color-success)' }} />
              <div>
                <div style={{ fontWeight: 'var(--weight-medium)', fontSize: 'var(--text-sm)' }}>Two-Factor Authentication</div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>Coming soon</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
