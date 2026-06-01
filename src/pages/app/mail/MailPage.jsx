import React, { useState, useEffect, useCallback } from 'react';
import { Send, RefreshCw, Mail, ChevronRight } from 'lucide-react';
import api from '../../../lib/api';

function parseDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  const now = new Date();
  const diffMs = now - d;
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffDays === 0) return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return d.toLocaleDateString('en-IN', { weekday: 'short' });
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

function parseFullDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true });
}

export default function MailPage() {
  const [folder, setFolder] = useState('SENT');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchMessages = useCallback(async () => {
    setLoading(true);
    setSelected(null);
    setDetail(null);
    try {
      const res = await api.get(`/gmail/messages?folder=${folder}&max_results=30`);
      setMessages(res.data.messages || []);
    } catch {
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, [folder]);

  useEffect(() => { fetchMessages(); }, [fetchMessages]);

  const openMessage = async (msg) => {
    setSelected(msg.id);
    setDetail(null);
    setDetailLoading(true);
    try {
      const res = await api.get(`/gmail/messages/${msg.id}`);
      setDetail(res.data);
    } catch {
      setDetail({ ...msg, body: '(Could not load message body)' });
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 60px)', overflow: 'hidden' }}>
      {/* Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 24px', borderBottom: '1px solid #f0f0f0', background: '#fff', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <h1 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>Mail</h1>
          <span style={{ fontSize: 12, color: '#9ca3af', marginLeft: 4 }}>recruit@tekleaders.io</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Folder toggle */}
          {['SENT', 'INBOX'].map(f => (
            <button
              key={f}
              onClick={() => setFolder(f)}
              style={{
                padding: '5px 14px', borderRadius: 6, border: '1px solid #e5e7eb', cursor: 'pointer', fontSize: 13, fontWeight: 500,
                background: folder === f ? '#00756a' : '#fff',
                color: folder === f ? '#fff' : '#374151',
              }}
            >
              {f === 'SENT' ? 'Sent' : 'Inbox'}
            </button>
          ))}
          <button
            onClick={fetchMessages}
            disabled={loading}
            style={{ background: 'none', border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, fontSize: 13, color: '#6b7280' }}
          >
            <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            Refresh
          </button>
        </div>
      </div>

      {/* Body: list + detail */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Message list */}
        <div style={{ width: 360, borderRight: '1px solid #f0f0f0', overflowY: 'auto', background: '#fafafa', flexShrink: 0 }}>
          {loading ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#9ca3af', fontSize: 13 }}>Loading…</div>
          ) : messages.length === 0 ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#9ca3af' }}>
              <Mail size={32} style={{ opacity: 0.3, marginBottom: 8 }} />
              <div style={{ fontSize: 13 }}>No messages</div>
            </div>
          ) : (
            messages.map(msg => (
              <button
                key={msg.id}
                onClick={() => openMessage(msg)}
                style={{
                  display: 'block', width: '100%', textAlign: 'left',
                  padding: '12px 16px', border: 'none', borderBottom: '1px solid #f0f0f0',
                  background: selected === msg.id ? '#00756a12' : '#fff',
                  cursor: 'pointer',
                  borderLeft: selected === msg.id ? '3px solid #00756a' : '3px solid transparent',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: '#111827', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', paddingRight: 8 }}>
                    {folder === 'SENT' ? msg.to : msg.from_}
                  </span>
                  <span style={{ fontSize: 11, color: '#9ca3af', whiteSpace: 'nowrap' }}>{parseDate(msg.date)}</span>
                </div>
                <div style={{ fontSize: 12, color: '#374151', fontWeight: 500, marginBottom: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {msg.subject}
                </div>
                <div style={{ fontSize: 11, color: '#9ca3af', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {msg.snippet}
                </div>
              </button>
            ))
          )}
        </div>

        {/* Detail pane */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 32, background: '#fff' }}>
          {!selected ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#d1d5db' }}>
              <Send size={48} style={{ marginBottom: 16, opacity: 0.4 }} />
              <div style={{ fontSize: 14 }}>Select a message to read</div>
            </div>
          ) : detailLoading ? (
            <div style={{ color: '#9ca3af', fontSize: 13 }}>Loading message…</div>
          ) : detail ? (
            <div style={{ maxWidth: 680 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, color: '#111827', marginBottom: 16 }}>{detail.subject}</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '6px 12px', marginBottom: 24, fontSize: 13 }}>
                <span style={{ color: '#9ca3af' }}>From</span>
                <span style={{ color: '#374151' }}>{detail.from_}</span>
                <span style={{ color: '#9ca3af' }}>To</span>
                <span style={{ color: '#374151' }}>{detail.to}</span>
                <span style={{ color: '#9ca3af' }}>Date</span>
                <span style={{ color: '#374151' }}>{parseFullDate(detail.date)}</span>
              </div>
              <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: 24 }}>
                <pre style={{ fontFamily: 'inherit', fontSize: 14, color: '#374151', whiteSpace: 'pre-wrap', lineHeight: 1.7, margin: 0 }}>
                  {detail.body || detail.snippet || '(Empty message)'}
                </pre>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
