import React, { forwardRef } from 'react';
import { Calendar } from 'lucide-react';

const DatePicker = forwardRef(({ label, error, className = '', ...props }, ref) => {
  return (
    <div className="form-group">
      {label && <label className="form-label">{label}</label>}
      <div className="relative">
        <span style={{ position:'absolute', right:12, top:'50%', transform:'translateY(-50%)', color:'var(--color-text-hint)', pointerEvents:'none' }}>
          <Calendar size={16} />
        </span>
        <input ref={ref} type="date" className={`form-input ${className}`} {...props} />
      </div>
      {error && <span style={{ fontSize:'var(--text-xs)', color:'var(--color-danger)', marginTop:4, display:'block' }}>{error}</span>}
    </div>
  );
});

DatePicker.displayName = 'DatePicker';
export default DatePicker;
