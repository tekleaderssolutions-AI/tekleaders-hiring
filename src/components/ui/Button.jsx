import React from 'react';

export default function Button({ children, variant = 'primary', size = 'md', icon: Icon, className = '', ...props }) {
  const cls = [
    'btn',
    `btn-${variant}`,
    size !== 'md' && `btn-${size}`,
    Icon && !children && 'btn-icon',
    className,
  ].filter(Boolean).join(' ');

  return (
    <button className={cls} {...props}>
      {Icon && <Icon size={size === 'sm' ? 14 : 18} />}
      {children}
    </button>
  );
}
