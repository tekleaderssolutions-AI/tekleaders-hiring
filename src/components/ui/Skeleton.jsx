import React from 'react';

export default function Skeleton({ variant = 'text', width, height, className = '' }) {
  const cls = `skeleton skeleton-${variant} ${className}`;
  return <div className={cls} style={{ width, height }} />;
}
