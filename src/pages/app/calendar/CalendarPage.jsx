import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Video, ExternalLink, RefreshCw } from 'lucide-react';
import api from '../../../lib/api';

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'];

function getCalendarDays(year, month) {
  const firstDay = new Date(year, month, 1).getDay();
  const startOffset = (firstDay + 6) % 7; // Mon=0
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  return { startOffset, daysInMonth };
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d)) return '';
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
}

function formatDateTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d)) return '';
  return d.toLocaleString('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short',
    hour: '2-digit', minute: '2-digit', hour12: true,
  });
}

const EVENT_COLORS = ['#00756a', '#2563eb', '#7c3aed', '#db2777', '#ea580c', '#16a34a'];

function colorForEvent(title = '') {
  let h = 0;
  for (let i = 0; i < title.length; i++) h = (h * 31 + title.charCodeAt(i)) & 0xffff;
  return EVENT_COLORS[h % EVENT_COLORS.length];
}

export default function CalendarPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth());
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      // Fetch 90 days to cover prev/next month navigation
      const res = await api.get('/gmail/calendar/events?days=90');
      setEvents(res.data.events || []);
    } catch {
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 60_000); // auto-sync every 60s
    return () => clearInterval(interval);
  }, []);

  const prev = () => {
    if (month === 0) { setYear(y => y - 1); setMonth(11); }
    else setMonth(m => m - 1);
  };
  const next = () => {
    if (month === 11) { setYear(y => y + 1); setMonth(0); }
    else setMonth(m => m + 1);
  };

  const { startOffset, daysInMonth } = getCalendarDays(year, month);
  const today = now.getDate();
  const isCurrentMonth = year === now.getFullYear() && month === now.getMonth();
  const totalCells = Math.ceil((startOffset + daysInMonth) / 7) * 7;

  // Map events to day numbers for the visible month
  const eventsByDay = {};
  events.forEach(ev => {
    const start = new Date(ev.start);
    if (start.getFullYear() === year && start.getMonth() === month) {
      const d = start.getDate();
      if (!eventsByDay[d]) eventsByDay[d] = [];
      eventsByDay[d].push(ev);
    }
  });

  // Upcoming events (sorted, next 30 days from today)
  const upcomingCutoff = new Date(now.getTime() + 30 * 86400000);
  const upcoming = [...events]
    .filter(e => new Date(e.start) >= now && new Date(e.start) <= upcomingCutoff)
    .sort((a, b) => new Date(a.start) - new Date(b.start))
    .slice(0, 10);

  return (
    <div style={{ padding: 'var(--spacing-8)', maxWidth: 1200 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--weight-bold)', margin: 0 }}>Work Calendar</h1>
          <p style={{ fontSize: 13, color: '#6b7280', marginTop: 4 }}>recruit@tekleaders.io</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            onClick={fetchEvents}
            disabled={loading}
            style={{ background: 'none', border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, fontSize: 13, color: '#6b7280' }}
          >
            <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            {loading ? 'Syncing…' : 'Sync'}
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button onClick={prev} style={{ background: 'none', border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
              <ChevronLeft size={16} />
            </button>
            <span style={{ fontWeight: 600, minWidth: 140, textAlign: 'center', fontSize: 15 }}>{MONTHS[month]} {year}</span>
            <button onClick={next} style={{ background: 'none', border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 20 }}>
        {/* Calendar grid */}
        <div className="card" style={{ padding: 'var(--spacing-4)', overflow: 'hidden' }}>
          {/* Day headers */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1, marginBottom: 2 }}>
            {DAYS.map(d => (
              <div key={d} style={{ padding: '6px 4px', textAlign: 'center', fontSize: 12, fontWeight: 600, color: '#9ca3af' }}>
                {d}
              </div>
            ))}
          </div>
          {/* Day cells */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gridAutoRows: '90px', gap: 1 }}>
            {Array.from({ length: totalCells }).map((_, i) => {
              const dayNum = i - startOffset + 1;
              const isValid = dayNum >= 1 && dayNum <= daysInMonth;
              const isToday = isCurrentMonth && isValid && dayNum === today;
              const dayEvents = isValid ? (eventsByDay[dayNum] || []) : [];

              return (
                <div
                  key={i}
                  style={{
                    padding: '6px 4px',
                    height: 90,
                    overflow: 'hidden',
                    border: '1px solid #f3f4f6',
                    borderRadius: 4,
                    background: isToday ? '#00756a08' : 'transparent',
                    position: 'relative',
                    boxSizing: 'border-box',
                  }}
                >
                  {isValid && (
                    <>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                        width: 22, height: 22, borderRadius: '50%',
                        background: isToday ? '#00756a' : 'transparent',
                        color: isToday ? '#fff' : '#374151',
                        fontWeight: isToday ? 700 : 500,
                        fontSize: 12,
                      }}>
                        {dayNum}
                      </span>
                      <div style={{ marginTop: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {dayEvents.slice(0, 2).map(ev => (
                          <button
                            key={ev.id}
                            onClick={() => setSelectedEvent(ev)}
                            style={{
                              display: 'block', width: '100%', textAlign: 'left',
                              background: colorForEvent(ev.title), color: '#fff',
                              border: 'none', borderRadius: 3, padding: '2px 5px',
                              fontSize: 11, fontWeight: 500, cursor: 'pointer',
                              whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                            }}
                            title={ev.title}
                          >
                            {formatTime(ev.start)} {ev.title}
                          </button>
                        ))}
                        {dayEvents.length > 2 && (
                          <span style={{ fontSize: 10, color: '#6b7280', paddingLeft: 4 }}>
                            +{dayEvents.length - 2} more
                          </span>
                        )}
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Sidebar: upcoming events */}
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 10 }}>
            Upcoming (next 30 days)
          </div>
          {upcoming.length === 0 ? (
            <div style={{ fontSize: 13, color: '#9ca3af', textAlign: 'center', paddingTop: 32 }}>
              No upcoming events
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {upcoming.map(ev => (
                <button
                  key={ev.id}
                  onClick={() => setSelectedEvent(ev)}
                  style={{
                    textAlign: 'left', background: '#fff', border: '1px solid #e5e7eb',
                    borderRadius: 8, padding: '10px 12px', cursor: 'pointer',
                    borderLeft: `3px solid ${colorForEvent(ev.title)}`,
                  }}
                >
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#111827', marginBottom: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {ev.title}
                  </div>
                  <div style={{ fontSize: 11, color: '#6b7280' }}>{formatDateTime(ev.start)}</div>
                  {ev.meet_link && (
                    <div style={{ fontSize: 11, color: '#00756a', marginTop: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
                      <Video size={10} /> Google Meet
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Event detail modal */}
      {selectedEvent && (
        <div
          onClick={() => setSelectedEvent(null)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', zIndex: 500, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{ background: '#fff', borderRadius: 12, padding: 28, width: 400, maxWidth: '90vw', boxShadow: '0 20px 60px rgba(0,0,0,0.2)' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: '#111827', flex: 1, paddingRight: 12 }}>
                {selectedEvent.title}
              </div>
              <button onClick={() => setSelectedEvent(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 18, color: '#9ca3af', lineHeight: 1 }}>×</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ fontSize: 13, color: '#374151' }}>
                <span style={{ color: '#9ca3af', marginRight: 6 }}>Start:</span>
                {formatDateTime(selectedEvent.start)}
              </div>
              <div style={{ fontSize: 13, color: '#374151' }}>
                <span style={{ color: '#9ca3af', marginRight: 6 }}>End:</span>
                {formatDateTime(selectedEvent.end)}
              </div>
              {selectedEvent.attendees?.length > 0 && (
                <div style={{ fontSize: 13, color: '#374151' }}>
                  <span style={{ color: '#9ca3af', marginRight: 6 }}>Attendees:</span>
                  {selectedEvent.attendees.join(', ')}
                </div>
              )}
              {selectedEvent.meet_link && (
                <a
                  href={selectedEvent.meet_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#00756a', color: '#fff', borderRadius: 8, padding: '8px 14px', textDecoration: 'none', fontSize: 13, fontWeight: 600, width: 'fit-content', marginTop: 4 }}
                >
                  <Video size={14} /> Join Google Meet
                </a>
              )}
              {selectedEvent.html_link && (
                <a
                  href={selectedEvent.html_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#6b7280', textDecoration: 'none', marginTop: 2 }}
                >
                  <ExternalLink size={11} /> Open in Google Calendar
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
