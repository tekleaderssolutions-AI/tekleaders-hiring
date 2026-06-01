import React, { useRef, useState } from 'react';
import { Upload, X, FileText } from 'lucide-react';

export default function FileUpload({ label, accept, onChange, value }) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) onChange?.(e.dataTransfer.files[0]);
  };

  const handleChange = (e) => {
    if (e.target.files?.[0]) onChange?.(e.target.files[0]);
  };

  return (
    <div className="form-group">
      {label && <label className="form-label">{label}</label>}
      <div
        className={`form-input ${dragActive ? 'drag-active' : ''}`}
        style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'var(--spacing-8)', cursor:'pointer', textAlign:'center', borderStyle:'dashed' }}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        {value ? (
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <FileText size={20} />
            <span className="text-sm">{value.name || value}</span>
            <button onClick={(e) => { e.stopPropagation(); onChange?.(null); }} style={{ background:'none', border:'none', cursor:'pointer', color:'var(--color-text-muted)' }}><X size={16} /></button>
          </div>
        ) : (
          <>
            <Upload size={24} style={{ color:'var(--color-text-hint)', marginBottom:8 }} />
            <span className="text-sm text-muted">Drop file here or click to browse</span>
          </>
        )}
        <input ref={inputRef} type="file" accept={accept} onChange={handleChange} style={{ display:'none' }} />
      </div>
    </div>
  );
}
