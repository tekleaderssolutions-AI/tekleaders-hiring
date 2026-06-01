import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import AdminDashboardPage from '@/pages/app/admin/AdminDashboardPage';
import RecruiterDashboardPage from '@/pages/app/recruiter/RecruiterDashboardPage';

export default function DashboardPage() {
  const { user } = useAuth();
  const role = user?.role;

  if (role === 'admin') {
    return <AdminDashboardPage />;
  }

  // Default: recruiter / employee view
  return <RecruiterDashboardPage />;
}
