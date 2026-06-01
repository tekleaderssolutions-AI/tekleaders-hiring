import React from 'react';
import { Link } from 'react-router-dom';
const posts = [
  { slug:'ai-hiring-2026', title:'How AI is Transforming Hiring in 2026', excerpt:'Discover the latest trends in AI-powered recruitment...', date:'Apr 28, 2026', category:'AI' },
  { slug:'reduce-bias', title:'5 Ways to Reduce Bias in Your Hiring Process', excerpt:'Practical steps to build a more equitable hiring pipeline...', date:'Apr 22, 2026', category:'DEI' },
  { slug:'remote-hiring', title:'The Complete Guide to Remote Hiring', excerpt:'Best practices for evaluating and onboarding remote candidates...', date:'Apr 15, 2026', category:'Remote' },
];
export default function BlogListPage() {
  return (
    <div style={{ maxWidth:800, margin:'0 auto', padding:'calc(80px + var(--spacing-12)) var(--spacing-6) var(--spacing-16)' }}>
      <h1 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-4xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-8)' }}>Blog</h1>
      {posts.map((p) => (
        <Link key={p.slug} to={`/blog/${p.slug}`} style={{ display:'block', marginBottom:'var(--spacing-6)', textDecoration:'none' }}>
          <article className="card" style={{ padding:'var(--spacing-6)' }}>
            <div style={{ display:'flex', gap:'var(--spacing-3)', marginBottom:'var(--spacing-2)', fontSize:'var(--text-xs)' }}>
              <span className="badge badge-primary">{p.category}</span>
              <span style={{ color:'var(--color-text-hint)' }}>{p.date}</span>
            </div>
            <h2 style={{ fontSize:'var(--text-xl)', fontWeight:'var(--weight-semibold)', marginBottom:'var(--spacing-2)' }}>{p.title}</h2>
            <p style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)' }}>{p.excerpt}</p>
          </article>
        </Link>
      ))}
    </div>
  );
}
