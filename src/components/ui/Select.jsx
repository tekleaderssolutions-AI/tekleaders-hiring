import React, { forwardRef } from 'react';

const Select = forwardRef(({ label, options = [], error, className = '', ...props }, ref) => {
  return (
    <div className="form-group">
      {label && <label className="form-label">{label}</label>}
      <select ref={ref} className={`form-input ${className}`} {...props}>
        <option value="">Select...</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
      {error && <span style={{ fontSize:'var(--text-xs)', color:'var(--color-danger)', marginTop:4, display:'block' }}>{error}</span>}
    </div>
  );
});

Select.displayName = 'Select';
export default Select;
