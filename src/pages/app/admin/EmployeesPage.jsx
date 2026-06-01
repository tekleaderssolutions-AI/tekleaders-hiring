import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { UserPlus, Mail, Shield, UserCheck, UserX, ChevronDown } from 'lucide-react';
import api from '@/lib/api';

function useEmployees() {
  return useQuery({
    queryKey: ['admin-employees'],
    queryFn: () => api.get('/admin/employees').then(r => r.data),
  });
}

function useCreateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/admin/employees', data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-employees'] }),
  });
}

function useUpdateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => api.patch(`/admin/employees/${id}`, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-employees'] }),
  });
}

const ROLE_COLORS = {
  admin: { bg: '#dcfce7', color: '#15803d' },
  recruiter: { bg: '#dbeafe', color: '#1d4ed8' },
  hiring_manager: { bg: '#ede9fe', color: '#7c3aed' },
};

const ROLE_OPTIONS = ['recruiter', 'hiring_manager'];

const EMPTY_FORM = { first_name: '', last_name: '', email: '', password: '', role: 'recruiter' };

export default function EmployeesPage() {
  const [showAddForm, setShowAddForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState('');

  const { data: employees = [], isLoading } = useEmployees();
  const createEmployee = useCreateEmployee();
  const updateEmployee = useUpdateEmployee();

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleAdd = async (e) => {
    e.preventDefault();
    setFormError('');
    if (!form.first_name.trim() || !form.last_name.trim()) return setFormError('First and last name are required');
    if (!form.email.trim()) return setFormError('Email is required');
    if (form.password.length < 8) return setFormError('Password must be at least 8 characters');
    try {
      await createEmployee.mutateAsync(form);
      setForm(EMPTY_FORM);
      setShowAddForm(false);
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to create employee');
    }
  };

  const handleToggleActive = (emp) => {
    updateEmployee.mutate({ id: emp.id, is_active: !emp.is_active });
  };

  const handleRoleChange = (emp, newRole) => {
    updateEmployee.mutate({ id: emp.id, role: newRole });
  };

  return (
    <div style={{ padding: '28px 36px', maxWidth: 1000 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111827', margin: 0 }}>Team Members</h1>
          <p style={{ color: '#6b7280', fontSize: 14, marginTop: 4 }}>Manage recruiters and hiring managers in your company</p>
        </div>
        <button
          onClick={() => { setShowAddForm(s => !s); setFormError(''); setForm(EMPTY_FORM); }}
          style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#00756a', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 18px', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
        >
          <UserPlus size={16} />
          Add Employee
        </button>
      </div>

      {/* Add Employee Form */}
      {showAddForm && (
        <form onSubmit={handleAdd} style={{ background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 12, padding: 24, marginBottom: 24 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#111827', margin: '0 0 16px' }}>New Employee</h3>
          {formError && (
            <div style={{ background: '#fee2e2', color: '#dc2626', padding: '10px 14px', borderRadius: 8, fontSize: 13, marginBottom: 14 }}>
              {formError}
            </div>
          )}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 5 }}>First Name *</label>
              <input
                value={form.first_name}
                onChange={e => update('first_name', e.target.value)}
                placeholder="Jane"
                style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db', borderRadius: 7, fontSize: 14, boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 5 }}>Last Name *</label>
              <input
                value={form.last_name}
                onChange={e => update('last_name', e.target.value)}
                placeholder="Doe"
                style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db', borderRadius: 7, fontSize: 14, boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 5 }}>Work Email *</label>
              <input
                type="email"
                value={form.email}
                onChange={e => update('email', e.target.value)}
                placeholder="jane@company.com"
                style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db', borderRadius: 7, fontSize: 14, boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 5 }}>Temporary Password *</label>
              <input
                type="password"
                value={form.password}
                onChange={e => update('password', e.target.value)}
                placeholder="Min 8 characters"
                style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db', borderRadius: 7, fontSize: 14, boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 5 }}>Role</label>
              <select
                value={form.role}
                onChange={e => update('role', e.target.value)}
                style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db', borderRadius: 7, fontSize: 14, background: '#fff', boxSizing: 'border-box' }}
              >
                {ROLE_OPTIONS.map(r => (
                  <option key={r} value={r}>{r.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
                ))}
              </select>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button
              type="submit"
              disabled={createEmployee.isPending}
              style={{ background: '#00756a', color: '#fff', border: 'none', borderRadius: 7, padding: '9px 20px', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
            >
              {createEmployee.isPending ? 'Creating...' : 'Create Employee'}
            </button>
            <button
              type="button"
              onClick={() => { setShowAddForm(false); setFormError(''); setForm(EMPTY_FORM); }}
              style={{ background: '#fff', color: '#374151', border: '1px solid #d1d5db', borderRadius: 7, padding: '9px 18px', fontSize: 14, cursor: 'pointer' }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Employees Table */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#9ca3af' }}>Loading...</div>
      ) : employees.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 12 }}>
          <UserCheck size={36} style={{ opacity: 0.3, marginBottom: 10 }} />
          <div style={{ fontSize: 15 }}>No team members yet</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>Add your first recruiter to get started</div>
        </div>
      ) : (
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                {['Name', 'Email', 'Role', 'Status', 'Joined', 'Actions'].map(h => (
                  <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {employees.map((emp, idx) => {
                const roleStyle = ROLE_COLORS[emp.role] || { bg: '#f3f4f6', color: '#374151' };
                return (
                  <tr key={emp.id} style={{ borderBottom: idx < employees.length - 1 ? '1px solid #f3f4f6' : 'none', opacity: emp.is_active ? 1 : 0.5 }}>
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{ width: 34, height: 34, borderRadius: '50%', background: '#00756a20', color: '#00756a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700, flexShrink: 0 }}>
                          {emp.first_name?.[0]}{emp.last_name?.[0]}
                        </div>
                        <div style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>{emp.name}</div>
                      </div>
                    </td>
                    <td style={{ padding: '14px 16px', fontSize: 13, color: '#6b7280' }}>{emp.email}</td>
                    <td style={{ padding: '14px 16px' }}>
                      <select
                        value={emp.role}
                        onChange={e => handleRoleChange(emp, e.target.value)}
                        style={{ background: roleStyle.bg, color: roleStyle.color, border: 'none', borderRadius: 20, padding: '4px 10px', fontSize: 12, fontWeight: 700, cursor: 'pointer' }}
                      >
                        {ROLE_OPTIONS.map(r => (
                          <option key={r} value={r}>{r.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
                        ))}
                      </select>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{ background: emp.is_active ? '#d1fae5' : '#f3f4f6', color: emp.is_active ? '#059669' : '#6b7280', fontSize: 11, padding: '3px 8px', borderRadius: 20, fontWeight: 700, textTransform: 'uppercase' }}>
                        {emp.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px', fontSize: 12, color: '#9ca3af' }}>
                      {emp.created_at ? new Date(emp.created_at).toLocaleDateString('en-IN') : '—'}
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <button
                        onClick={() => handleToggleActive(emp)}
                        style={{ display: 'flex', alignItems: 'center', gap: 4, background: emp.is_active ? '#fee2e2' : '#d1fae5', color: emp.is_active ? '#dc2626' : '#059669', border: 'none', borderRadius: 6, padding: '5px 10px', fontSize: 12, cursor: 'pointer' }}
                      >
                        {emp.is_active ? <><UserX size={12} /> Deactivate</> : <><UserCheck size={12} /> Activate</>}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
