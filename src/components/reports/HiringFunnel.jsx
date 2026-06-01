import React from 'react';
export default function HiringFunnel({ data = [] }) {
  const maxVal = Math.max(...data.map((d) => d.value), 1);
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'var(--spacing-2)' }}>
      {data.map((stage) => (
        <div key={stage.label} style={{ display:'flex', alignItems:'center', gap:'var(--spacing-3)' }}>
          <span style={{ width:100, fontSize:'var(--text-xs)', color:'var(--color-text-muted)', textAlign:'right' }}>{stage.label}</span>
          <div style={{ flex:1, height:28, background:'var(--color-bg-secondary)', borderRadius:'var(--radius-md)', overflow:'hidden' }}>
            <div style={{ width:`${(stage.value / maxVal) * 100}%`, height:'100%', background:'var(--gradient-primary)', borderRadius:'var(--radius-md)', transition:'width 0.6s ease' }} />
          </div>
          <span style={{ width:40, fontSize:'var(--text-sm)', fontWeight:'var(--weight-semibold)', textAlign:'right' }}>{stage.value}</span>
        </div>
      ))}
    </div>
  );
}
