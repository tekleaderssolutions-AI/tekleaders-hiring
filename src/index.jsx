import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

/* ── Style imports (order matters) ── */
import './styles/variables.css';
import './styles/reset.css';
import './styles/base.css';
import './styles/utils.css';
import './styles/animations.css';

/* ── Component CSS ── */
import './styles/components/button.css';
import './styles/components/card.css';
import './styles/components/modal.css';
import './styles/components/sidebar.css';
import './styles/components/badge.css';
import './styles/components/table.css';
import './styles/components/toast.css';
import './styles/components/avatar.css';
import './styles/components/tabs.css';
import './styles/components/skeleton.css';
import './styles/components/kanban.css';

/* ── Page CSS ── */
import './styles/pages/landing.css';
import './styles/pages/auth.css';
import './styles/pages/dashboard.css';
import './styles/pages/jobs.css';
import './styles/pages/candidates.css';
import './styles/pages/copilot.css';
import './styles/pages/people.css';
import './styles/pages/reports.css';
import './styles/pages/settings.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
