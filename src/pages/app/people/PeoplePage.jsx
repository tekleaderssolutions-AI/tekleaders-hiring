import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { UserPlus, Users, UserCheck, UserX } from 'lucide-react';
import api from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';

function useEmployees() {
  return useQuery({
    queryKey: ['admin-employees'],
    queryFn: () => api.get('/admin/employees').then(r => r.data),
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
  recruiter: { bg: '#dbeafe', color: '#1d4ed8' },
  hiring_manager: { bg: '#ede9fe', color: '#7c3aed' },
  admin: { bg: '#dcfce7', color: '#15803d' },
  interviewer: { bg: '#fef3c7', color: '#d97706' },
};

const ROLE_OPTIONS = ['recruiter', 'hiring_manager', 'admin', 'interviewer'];

export default function PeoplePage() {
  const navigate = useNavigate();
  const { data: employees = [], isLoading } = useEmployees();
  const updateEmployee = useUpdateEmployee();
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const handleRoleChange = (emp, newRole) => {
    updateEmployee.mutate({ id: emp.id, role: newRole });
  };

  const handleToggleActive = (emp) => {
    updateEmployee.mutate({ id: emp.id, is_active: !emp.is_active });
  };

  return (
    <div style={{ padding: '28px 36px', maxWidth: 1100 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111827', margin: 0 }}>People</h1>
          <p style={{ color: '#6b7280', fontSize: 14, marginTop: 4 }}>
            {employees.length} team member{employees.length !== 1 ? 's' : ''}
          </p>
        </div>
        {isAdmin && (
          <button
            onClick={() => navigate('/team')}
            style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#00756a', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 18px', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
          >
            <UserPlus size={16} /> Add Employee
          </button>
        )}
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#9ca3af' }}>Loading...</div>
      ) : employees.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 80, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 12 }}>
          <Users size={36} style={{ opacity: 0.3, marginBottom: 12 }} />
          <div style={{ fontSize: 15 }}>No team members yet</div>
        </div>
      ) : (
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                {['Member', 'Email', 'Role', 'Status', 'Joined', ...(isAdmin ? ['Actions'] : [])].map(h => (
                  <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {employees.map((emp, idx) => {
                const isYou = emp.is_current_user;
                const roleStyle = ROLE_COLORS[emp.role] || { bg: '#f3f4f6', color: '#374151' };
                const initials = `${emp.first_name?.[0] || ''}${emp.last_name?.[0] || ''}`.toUpperCase();
                return (
                  <tr
                    key={emp.id}
                    style={{
                      borderBottom: idx < employees.length - 1 ? '1px solid #f3f4f6' : 'none',
                      background: isYou ? '#f0fdf9' : '#fff',
                      opacity: emp.is_active ? 1 : 0.55,
                    }}
                  >
                    {/* Member */}
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{
                          width: 38, height: 38, borderRadius: '50%', flexShrink: 0,
                          background: isYou ? '#00756a' : '#00756a20',
                          color: isYou ? '#fff' : '#00756a',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: 13, fontWeight: 700,
                          border: isYou ? '2px solid #00756a' : 'none',
                        }}>
                          {initials}
                        </div>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>
                              {emp.name}
                            </span>
                            {isYou && (
                              <span style={{ fontSize: 10, background: '#00756a', color: '#fff', padding: '2px 8px', borderRadius: 20, fontWeight: 700, letterSpacing: '0.03em' }}>
                                You
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Email */}
                    <td style={{ padding: '14px 16px', fontSize: 13, color: '#6b7280' }}>
                      {emp.email}
                    </td>

                    {/* Role */}
                    <td style={{ padding: '14px 16px' }}>
                      {isAdmin && !isYou ? (
                        <select
                          value={emp.role}
                          onChange={e => handleRoleChange(emp, e.target.value)}
                          style={{
                            background: roleStyle.bg, color: roleStyle.color,
                            border: 'none', borderRadius: 20, padding: '4px 10px',
                            fontSize: 12, fontWeight: 700, cursor: 'pointer',
                          }}
                        >
                          {ROLE_OPTIONS.map(r => (
                            <option key={r} value={r}>{r.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
                          ))}
                        </select>
                      ) : (
                        <span style={{ background: roleStyle.bg, color: roleStyle.color, borderRadius: 20, padding: '4px 10px', fontSize: 12, fontWeight: 700 }}>
                          {emp.role?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                        </span>
                      )}
                    </td>

                    {/* Status */}
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{
                        background: emp.is_active ? '#d1fae5' : '#f3f4f6',
                        color: emp.is_active ? '#059669' : '#6b7280',
                        fontSize: 11, padding: '3px 10px', borderRadius: 20,
                        fontWeight: 700, textTransform: 'uppercase',
                      }}>
                        {emp.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>

                    {/* Joined */}
                    <td style={{ padding: '14px 16px', fontSize: 12, color: '#9ca3af' }}>
                      {emp.created_at ? new Date(emp.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'}
                    </td>

                    {/* Actions — admin only */}
                    {isAdmin && (
                      <td style={{ padding: '14px 16px' }}>
                        {!isYou && (
                          <button
                            onClick={() => handleToggleActive(emp)}
                            style={{
                              display: 'flex', alignItems: 'center', gap: 4,
                              background: emp.is_active ? '#fee2e2' : '#d1fae5',
                              color: emp.is_active ? '#dc2626' : '#059669',
                              border: 'none', borderRadius: 6, padding: '5px 12px',
                              fontSize: 12, fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap',
                            }}
                          >
                            {emp.is_active
                              ? <><UserX size={12} /> Deactivate</>
                              : <><UserCheck size={12} /> Activate</>}
                          </button>
                        )}
                      </td>
                    )}
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
