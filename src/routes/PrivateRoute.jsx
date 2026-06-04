import React, { useEffect, useRef } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { getToken } from '@/lib/auth';

export default function PrivateRoute() {
  const { user, fetchProfile, isFetchingProfile } = useAuth();
  const fetched = useRef(false);

  useEffect(() => {
    // Only trigger once — App.jsx also calls fetchProfile, this is a safety net
    // for when the user lands directly on a deep URL with a token but no in-memory user.
    if (!fetched.current && getToken() && !user) {
      fetched.current = true;
      fetchProfile();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Token present but profile not yet loaded — show spinner instead of
  // immediately redirecting to login (which was causing blank pages on refresh).
  if (!user && getToken() && isFetchingProfile) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', flexDirection: 'column', gap: 12,
      }}>
        <div style={{
          width: 36, height: 36, border: '3px solid #e5e7eb',
          borderTopColor: '#00756a', borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        <span style={{ fontSize: 13, color: '#9ca3af' }}>Loading…</span>
      </div>
    );
  }

  // No token at all → send to login
  if (!user && !getToken()) {
    return <Navigate to="/login" replace />;
  }

  // user from localStorage (synchronous) or after fetchProfile — render the app
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}
