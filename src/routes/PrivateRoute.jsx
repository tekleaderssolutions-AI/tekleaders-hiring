import React, { useEffect, useRef } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { getToken } from '@/lib/auth';

export default function PrivateRoute() {
  const { user, fetchProfile } = useAuth();
  const refreshed = useRef(false);

  useEffect(() => {
    // Refresh profile from backend once per mount so role is always current
    if (!refreshed.current && getToken()) {
      refreshed.current = true;
      fetchProfile();
    }
  }, [fetchProfile]);

  return user ? <Outlet /> : <Navigate to="/login" replace />;
}
