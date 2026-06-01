import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
export default function BlogPostPage() {
  const { slug } = useParams();
  return (
    <div style={{ maxWidth:720, margin:'0 auto', padding:'calc(80px + var(--spacing-12)) var(--spacing-6) var(--spacing-16)' }}>
      <Link to="/blog" style={{ display:'inline-flex', alignItems:'center', gap:6, fontSize:'var(--text-sm)', color:'var(--color-text-muted)', marginBottom:'var(--spacing-6)' }}><ArrowLeft size={16} />Back to Blog</Link>
      <h1 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-3xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-4)' }}>Blog Post: {slug}</h1>
      <p style={{ color:'var(--color-text-muted)', lineHeight:'var(--leading-relaxed)' }}>This is a placeholder blog post content for "{slug}". Full blog content would be loaded from the API.</p>
    </div>
  );
}
