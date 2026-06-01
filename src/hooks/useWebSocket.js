import { useEffect, useRef, useCallback } from 'react';
import useRealtimeStore from '@/store/realtimeStore';

export function useWebSocket(companyId, userId) {
  const wsRef = useRef(null);
  const retryCount = useRef(0);
  const { addEvent, setConnectionStatus } = useRealtimeStore();

  const connect = useCallback(() => {
    if (!companyId || !userId) return;
    // Use the explicit VITE_WS_URL if provided, otherwise default to the current host (for proxy/same-domain)
    const baseUrl = import.meta.env.VITE_WS_URL || `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;
    
    // Ensure we don't have double slashes if baseUrl has a trailing slash
    const wsUrl = `${baseUrl.replace(/\/$/, '')}/ws/${companyId}/${userId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionStatus('connected');
      retryCount.current = 0;
    };

    ws.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data);
        addEvent(event);
      } catch { /* ignore non-JSON */ }
    };

    ws.onclose = () => {
      setConnectionStatus('disconnected');
      const delay = Math.min(1000 * 2 ** retryCount.current, 30000);
      retryCount.current++;
      setTimeout(connect, delay);
    };

    ws.onerror = () => ws.close();
  }, [companyId, userId, addEvent, setConnectionStatus]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return wsRef;
}
