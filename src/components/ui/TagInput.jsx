import React, { useState } from 'react';
import { X } from 'lucide-react';

export default function TagInput({ label, value = [], onChange, placeholder = 'Add tag...' }) {
  const [input, setInput] = useState('');

  const addTag = () => {
    const tag = input.trim();
    if (tag && !value.includes(tag)) {
      onChange([...value, tag]);
    }
    setInput('');
  };

  const removeTag = (tag) => onChange(value.filter((t) => t !== tag));

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') { e.preventDefault(); addTag(); }
    if (e.key === 'Backspace' && !input && value.length) removeTag(value[value.length - 1]);
  };

  return (
    <div className="form-group">
      {label && <label className="form-label">{label}</label>}
      <div className="form-input" style={{ display:'flex', flexWrap:'wrap', gap:4, padding:8, minHeight:42 }}>
        {value.map((tag) => (
          <span key={tag} className="badge badge-primary" style={{ display:'inline-flex', alignItems:'center', gap:4 }}>
            {tag}
            <button onClick={() => removeTag(tag)} style={{ background:'none', border:'none', cursor:'pointer', padding:0, color:'inherit' }}><X size={12} /></button>
          </span>
        ))}
        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
          placeholder={value.length === 0 ? placeholder : ''} style={{ flex:1, minWidth:80, border:'none', background:'transparent', outline:'none', color:'var(--color-text)', fontSize:'var(--text-sm)' }}
        />
      </div>
    </div>
  );
}
