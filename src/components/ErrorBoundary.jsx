import React from 'react';

export default class ErrorBoundary extends React.Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          height: '100vh', flexDirection: 'column', gap: 16, padding: 32,
          fontFamily: 'system-ui, sans-serif',
        }}>
          <div style={{ fontSize: 40 }}>⚠</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: '#111827' }}>
            Something went wrong
          </div>
          <div style={{
            fontSize: 13, color: '#6b7280', maxWidth: 420,
            textAlign: 'center', lineHeight: 1.6,
          }}>
            {this.state.error.message || 'An unexpected error occurred.'}
          </div>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 24px', background: '#00756a', color: '#fff',
              border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600,
              cursor: 'pointer', marginTop: 8,
            }}
          >
            Reload page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
