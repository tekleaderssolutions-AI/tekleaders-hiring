import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { UserPlus, Users } from 'lucide-react';
import api from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';

function useEmployees() {
  return useQuery({
    queryKey: ['admin-employees'],
    queryFn: () => api.get('/admin/employees').then(r => r.data),
  });
}

const ROLE_COLORS = {
  recruiter: { bg: '#dbeafe', color: '#1d4ed8' },
  hiring_manager: { bg: '#ede9fe', color: '#7c3aed' },
  admin: { bg: '#dcfce7', color: '#15803d' },
  interviewer: { bg: '#fef3c7', color: '#d97706' },
};

export default function PeoplePage() {
  const navigate = useNavigate();
  const { data: employees = [], isLoading } = useEmployees();
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  return (
    <div className="people-page">
      <div className="people-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--weight-bold)' }}>People</h1>
        {isAdmin && (
          <button
            onClick={() => navigate('/team')}
            style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#00756a', color: '#fff', border: 'none', borderRadius: 8, padding: '9px 18px', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
          >
            <UserPlus size={15} /> Add Employee
          </button>
        )}
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#9ca3af' }}>Loading...</div>
      ) : employees.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 80, color: '#9ca3af', border: '2px dashed #e5e7eb', borderRadius: 12, marginTop: 24 }}>
          <Users size={36} style={{ opacity: 0.3, marginBottom: 12 }} />
          <div style={{ fontSize: 15 }}>No team members yet</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>Add your first employee from the Team page</div>
        </div>
      ) : (
        <div className="people-grid">
          {employees.map(emp => {
            const roleStyle = ROLE_COLORS[emp.role] || { bg: '#f3f4f6', color: '#374151' };
            const initials = `${emp.first_name?.[0] || ''}${emp.last_name?.[0] || ''}`.toUpperCase();
            return (
              <div key={emp.id} style={{ background: '#fff', border: emp.is_current_user ? '2px solid #00756a' : '1px solid #e5e7eb', borderRadius: 12, padding: '24px 20px', textAlign: 'center', opacity: emp.is_active ? 1 : 0.5, position: 'relative' }}>
                {emp.is_current_user && (
                  <span style={{ position: 'absolute', top: 10, right: 10, fontSize: 10, background: '#00756a', color: '#fff', padding: '2px 8px', borderRadius: 20, fontWeight: 700 }}>You</span>
                )}
                <div style={{ width: 56, height: 56, borderRadius: '50%', background: '#00756a20', color: '#00756a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, fontWeight: 700, margin: '0 auto 12px' }}>
                  {initials}
                </div>
                <div style={{ fontSize: 15, fontWeight: 700, color: '#111827' }}>{emp.name}</div>
                <div style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>{emp.email}</div>
                <div style={{ marginTop: 8 }}>
                  <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 20, background: roleStyle.bg, color: roleStyle.color, fontWeight: 700 }}>
                    {emp.role?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  </span>
                </div>
                {!emp.is_active && <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 6 }}>Inactive</div>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
