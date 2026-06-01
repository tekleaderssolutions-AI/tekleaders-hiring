import React from 'react';
import { Mail, MessageSquare, Bell } from 'lucide-react';
import { Avatar, Badge } from '@/components/ui';
const messages = [
  { id:1, from:'Sarah Chen', subject:'Re: Interview Schedule', preview:'Thanks for confirming! I\'ll be there at 2pm...', time:'10m ago', unread:true },
  { id:2, from:'LinkedIn', subject:'5 new applicants for Senior Engineer', preview:'You have 5 new applications waiting...', time:'1h ago', unread:true },
  { id:3, from:'James Wilson', subject:'Portfolio submission', preview:'Please find my portfolio attached...', time:'3h ago', unread:false },
  { id:4, from:'System', subject:'Weekly pipeline digest', preview:'Your weekly hiring summary is ready...', time:'1d ago', unread:false },
];
export default function InboxPage() {
  return (
    <div style={{ padding:'var(--spacing-8)' }}>
      <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-6)' }}>Inbox</h1>
      <div className="card" style={{ padding:0, overflow:'hidden' }}>
        {messages.map((m) => (
          <div key={m.id} style={{ display:'flex', alignItems:'center', gap:'var(--spacing-4)', padding:'var(--spacing-4) var(--spacing-6)', borderBottom:'1px solid var(--color-border-light)', cursor:'pointer', background:m.unread?'rgba(102,126,234,0.03)':'transparent' }}>
            <Avatar name={m.from} size="sm" />
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ display:'flex', justifyContent:'space-between', marginBottom:2 }}>
                <span style={{ fontSize:'var(--text-sm)', fontWeight:m.unread?'var(--weight-semibold)':'var(--weight-normal)' }}>{m.from}</span>
                <span style={{ fontSize:'var(--text-xs)', color:'var(--color-text-hint)' }}>{m.time}</span>
              </div>
              <div style={{ fontSize:'var(--text-sm)', fontWeight:m.unread?'var(--weight-medium)':'var(--weight-normal)', marginBottom:2 }}>{m.subject}</div>
              <div style={{ fontSize:'var(--text-xs)', color:'var(--color-text-muted)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{m.preview}</div>
            </div>
            {m.unread && <div style={{ width:8, height:8, borderRadius:'50%', background:'var(--color-primary)', flexShrink:0 }} />}
          </div>
        ))}
      </div>
    </div>
  );
}
