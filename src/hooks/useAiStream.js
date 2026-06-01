import { useCallback } from 'react';

export function useAiStream() {
  const startStream = useCallback((prompt, onChunk, onDone) => {
    const url = '/api/ai/copilot/stream?q=' + encodeURIComponent(prompt);
    const es = new EventSource(url);

    es.onmessage = (e) => {
      if (e.data === '[DONE]') {
        es.close();
        onDone?.();
        return;
      }
      onChunk?.(e.data);
    };

    es.onerror = () => {
      es.close();
      onDone?.();
    };

    return () => es.close();
  }, []);

  return { startStream };
}
