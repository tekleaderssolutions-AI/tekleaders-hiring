import React from 'react';
export default function StatCard({ label, value, change, icon: Icon }) {
  const isPositive = change && change > 0;
  return (
    <div className="kpi-card">
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
        <span className="kpi-label">{label}</span>
        {Icon && <Icon size={18} style={{ color:'var(--color-primary)' }} />}
      </div>
      <div className="kpi-value">{value}</div>
      {change != null && <div className={`kpi-change ${isPositive ? 'positive' : 'negative'}`}>{isPositive ? '↑' : '↓'} {Math.abs(change)}%</div>}
    </div>
  );
}
