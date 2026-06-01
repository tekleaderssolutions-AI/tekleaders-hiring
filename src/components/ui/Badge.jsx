import React from 'react';

export default function Badge({ children, variant = 'neutral', dot = false, className = '' }) {
  return (
    <span className={`badge badge-${variant} ${dot ? 'badge-dot' : ''} ${className}`}>
      {children}
    </span>
  );
}
