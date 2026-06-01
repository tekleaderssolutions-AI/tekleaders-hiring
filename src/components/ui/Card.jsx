import React from 'react';

export default function Card({ children, variant = '', className = '', ...props }) {
  const cls = ['card', variant && `card-${variant}`, className].filter(Boolean).join(' ');
  return <div className={cls} {...props}>{children}</div>;
}

export function CardHeader({ children, className = '' }) {
  return <div className={`card-header ${className}`}>{children}</div>;
}

export function CardTitle({ children, className = '' }) {
  return <h3 className={`card-title ${className}`}>{children}</h3>;
}

export function CardDescription({ children }) {
  return <p className="card-description">{children}</p>;
}
