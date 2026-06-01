import React from 'react';

export default function StreamingMessage({ content = '', isStreaming = false }) {
  return (
    <div className="message-bubble ai">
      <span>{content}</span>
      {isStreaming && <span className="animate-pulse" style={{ display:'inline-block', width:6, height:16, background:'var(--color-primary)', borderRadius:2, marginLeft:4, verticalAlign:'middle' }} />}
    </div>
  );
}
