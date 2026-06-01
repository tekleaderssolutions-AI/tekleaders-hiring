import React from 'react';
import { Outlet } from 'react-router-dom';
import TopBar from './TopBar';
import { Toast } from '@/components/ui';

export default function AppShell() {
  return (
    <div className="app-shell" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <TopBar />
      <main style={{ flex: 1, overflowY: 'auto' }}>
        <Outlet />
      </main>
      <Toast />
    </div>
  );
}
