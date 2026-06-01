import React, { forwardRef } from 'react';

const Input = forwardRef(({ label, error, icon: Icon, className = '', ...props }, ref) => {
  return (
    <div className="form-group">
      {label && <label className="form-label">{label}</label>}
      <div className="relative">
        {Icon && (
          <span style={{ position:'absolute', left:12, top:'50%', transform:'translateY(-50%)', color:'var(--color-text-hint)' }}>
            <Icon size={16} />
          </span>
        )}
        <input
          ref={ref}
          className={`form-input ${Icon ? 'has-icon' : ''} ${error ? 'has-error' : ''} ${className}`}
          style={Icon ? { paddingLeft: 36 } : undefined}
          {...props}
        />
      </div>
      {error && <span style={{ fontSize:'var(--text-xs)', color:'var(--color-danger)', marginTop:4, display:'block' }}>{error}</span>}
    </div>
  );
});

Input.displayName = 'Input';
export default Input;
