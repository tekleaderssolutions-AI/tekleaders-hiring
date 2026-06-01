import React from 'react';
import { Tabs } from '@/components/ui';

export default function JobFormTabs({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'details', label: 'Job Details' },
    { id: 'description', label: 'Description' },
    { id: 'requirements', label: 'Requirements' },
    { id: 'pipeline', label: 'Pipeline' },
    { id: 'settings', label: 'Settings' },
  ];
  return <div className="tabs">{tabs.map((t) => <button key={t.id} className={`tab ${activeTab === t.id ? 'active' : ''}`} onClick={() => onTabChange?.(t.id)}>{t.label}</button>)}</div>;
}
