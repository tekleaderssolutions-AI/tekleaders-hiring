import React from 'react';

export default function Avatar({ src, name = '', size = 'md', status, className = '' }) {
  const sizeClass = size !== 'md' ? `avatar-${size}` : '';
  const initials = name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase();

  return (
    <div className={`avatar ${sizeClass} ${className}`}>
      {src ? (
        <img src={src} alt={name} />
      ) : (
        <div className="avatar-placeholder">{initials || '?'}</div>
      )}
      {status && <span className={`avatar-status ${status}`} />}
    </div>
  );
}
