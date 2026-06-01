import React from 'react';
import { FileText } from 'lucide-react';
export default function ResumeViewer({ url }) {
  return (
    <div className="card" style={{ padding:'var(--spacing-6)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', minHeight:400 }}>
      {url ? <iframe src={url} style={{ width:'100%', height:500, border:'none', borderRadius:'var(--radius-md)' }} title="Resume" />
        : <><FileText size={48} style={{ color:'var(--color-text-hint)', marginBottom:'var(--spacing-4)' }} /><p style={{ color:'var(--color-text-muted)' }}>No resume uploaded</p></>}
    </div>
  );
}
