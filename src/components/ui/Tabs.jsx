import React, { useState } from 'react';

export default function Tabs({ tabs = [], variant = 'default', defaultTab, onChange }) {
  const [active, setActive] = useState(defaultTab || tabs[0]?.id);

  const handleClick = (id) => {
    setActive(id);
    onChange?.(id);
  };

  const activeTab = tabs.find((t) => t.id === active);

  return (
    <div>
      <div className={`tabs ${variant === 'pill' ? 'tabs-pill' : ''}`}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab ${active === tab.id ? 'active' : ''}`}
            onClick={() => handleClick(tab.id)}
          >
            {tab.icon && <span style={{ marginRight: 6 }}>{tab.icon}</span>}
            {tab.label}
          </button>
        ))}
      </div>
      <div className="tab-content">{activeTab?.content}</div>
    </div>
  );
}
