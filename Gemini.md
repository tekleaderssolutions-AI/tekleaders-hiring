================================================================================
  HIRIX FRONTEND ARCHITECTURE (REFACTORED)
  Stack: React.js 18 | React Router v6 | Plain CSS | JavaScript (ES2022)
================================================================================


--------------------------------------------------------------------------------
  WHAT CHANGED
--------------------------------------------------------------------------------

  Before (Next.js stack)          After (React.js stack)
  ------------------------------  ------------------------------
  Next.js 14 App Router           Vite + React Router v6
  TypeScript (.tsx / .ts)         JavaScript (.jsx / .js)
  Tailwind CSS utility classes    Plain CSS with CSS variables
  Server Components (RSC)         Client-side rendering only
  Next.js API routes              Proxy via Vite dev server
  next.config.ts                  vite.config.js
  tsconfig.json                   jsconfig.json
  Zod validators                  Yup validators
  NextAuth                        Custom JWT auth util


--------------------------------------------------------------------------------
  FOLDER STRUCTURE
--------------------------------------------------------------------------------

hirix-frontend/
|
|-- .env                          API keys, public vars
|-- .env.example
|-- vite.config.js                proxy, aliases, build config
|-- jsconfig.json                 path aliases (@/ -> src/)
|-- package.json
|-- index.html                    single HTML shell
|-- eslint.config.js
|-- vitest.config.js
|
|-- public/
|   |-- logo.svg
|   |-- og-image.png
|   `-- icons/                    favicons
|
`-- src/
    |-- index.js                  ReactDOM.createRoot entry point
    |-- App.jsx                   root component, QueryClient, providers
    |
    |-- routes/
    |   |-- AppRouter.jsx         BrowserRouter + all route definitions
    |   |-- PrivateRoute.jsx      auth guard HOC (redirects to /login)
    |   `-- PublicOnlyRoute.jsx   redirect to /dashboard if already logged in
    |
    |-- pages/
    |   |
    |   |-- public/               [NO AUTH REQUIRED]
    |   |   |-- HomePage.jsx          hero, features, pricing sections
    |   |   |-- PricingPage.jsx
    |   |   |-- BlogListPage.jsx
    |   |   |-- BlogPostPage.jsx      uses :slug param
    |   |   |-- CareersPage.jsx       job listings per :company param
    |   |   `-- JobApplyPage.jsx      apply for :id param
    |   |
    |   |-- auth/                 [LOGIN FLOW]
    |   |   |-- LoginPage.jsx
    |   |   |-- SignupPage.jsx
    |   |   |-- ForgotPasswordPage.jsx
    |   |   |-- ResetPasswordPage.jsx
    |   |   `-- OnboardingPage.jsx    5-step wizard
    |   |
    |   `-- app/                  [REQUIRES AUTH]
    |       |-- DashboardPage.jsx     KPIs, pipeline overview, agent feed
    |       |
    |       |-- jobs/
    |       |   |-- JobsListPage.jsx          table / grid view
    |       |   |-- JobNewPage.jsx            create job (5-tab form)
    |       |   |-- JobPipelinePage.jsx       kanban board :id
    |       |   |-- JobEditPage.jsx
    |       |   |-- JobOverviewPage.jsx
    |       |   |-- JobApplicationFormPage.jsx
    |       |   |-- JobReportsPage.jsx
    |       |   `-- JobSettingsPage.jsx
    |       |
    |       |-- candidates/
    |       |   |-- CandidatesPage.jsx        global candidate database
    |       |   `-- CandidateProfilePage.jsx  full profile :id
    |       |
    |       |-- ai-copilot/
    |       |   `-- AICopilotPage.jsx         3-panel chat + agents
    |       |
    |       |-- people/
    |       |   |-- PeoplePage.jsx            employee directory
    |       |   |-- EmployeeProfilePage.jsx
    |       |   |-- OrgChartPage.jsx
    |       |   |-- OnboardingPage.jsx
    |       |   `-- PerformancePage.jsx
    |       |
    |       |-- calendar/
    |       |   `-- CalendarPage.jsx          month / week / day view
    |       |
    |       |-- reports/
    |       |   |-- ReportsOverviewPage.jsx
    |       |   |-- PipelineReportPage.jsx
    |       |   |-- AIPerformancePage.jsx
    |       |   |-- DiversityPage.jsx
    |       |   `-- CustomReportPage.jsx
    |       |
    |       |-- files/
    |       |   `-- FilesPage.jsx             file manager + templates
    |       |
    |       |-- inbox/
    |       |   `-- InboxPage.jsx             unified mailbox + activity
    |       |
    |       `-- settings/
    |           |-- CompanySettingsPage.jsx
    |           |-- TeamSettingsPage.jsx
    |           |-- AIAutomationPage.jsx
    |           |-- IntegrationsPage.jsx
    |           |-- BillingPage.jsx
    |           |-- SecurityPage.jsx
    |           `-- APIKeysPage.jsx
    |
    |-- components/
    |   |
    |   |-- ui/                   [DESIGN SYSTEM ATOMS]
    |   |   |-- Button.jsx
    |   |   |-- Input.jsx
    |   |   |-- Select.jsx
    |   |   |-- Modal.jsx
    |   |   |-- Badge.jsx
    |   |   |-- Card.jsx
    |   |   |-- Table.jsx
    |   |   |-- Tabs.jsx
    |   |   |-- Toast.jsx
    |   |   |-- Avatar.jsx
    |   |   |-- ScoreRing.jsx
    |   |   |-- Skeleton.jsx
    |   |   |-- TagInput.jsx
    |   |   |-- DatePicker.jsx
    |   |   |-- FileUpload.jsx
    |   |   `-- index.js          barrel export
    |   |
    |   |-- layout/               [SHELL COMPONENTS]
    |   |   |-- AppShell.jsx      wraps Sidebar + TopBar + outlet
    |   |   |-- Sidebar.jsx
    |   |   |-- TopBar.jsx
    |   |   |-- CommandPalette.jsx    Cmd+K AI search
    |   |   `-- NotificationsPanel.jsx
    |   |
    |   |-- ai/                   [AI-SPECIFIC UI]
    |   |   |-- CopilotDrawer.jsx
    |   |   |-- AgentStatusCard.jsx
    |   |   |-- ReasoningTrace.jsx
    |   |   |-- StreamingMessage.jsx
    |   |   `-- AiScoreBadge.jsx
    |   |
    |   |-- jobs/
    |   |   |-- JobCard.jsx
    |   |   |-- JobFilters.jsx
    |   |   |-- KanbanBoard.jsx
    |   |   |-- KanbanCard.jsx
    |   |   |-- CandidateDrawer.jsx
    |   |   |-- PipelineStageEditor.jsx
    |   |   `-- JobFormTabs.jsx
    |   |
    |   |-- candidates/
    |   |   |-- CandidateTable.jsx
    |   |   |-- CandidateGrid.jsx
    |   |   |-- AiEvaluationPanel.jsx
    |   |   |-- RequirementsChecklist.jsx
    |   |   `-- ResumeViewer.jsx
    |   |
    |   |-- people/
    |   |   |-- EmployeeCard.jsx
    |   |   |-- OrgChart.jsx
    |   |   |-- OnboardingChecklist.jsx
    |   |   `-- ReviewCycleForm.jsx
    |   |
    |   |-- reports/
    |   |   |-- HiringFunnel.jsx
    |   |   |-- StatCard.jsx
    |   |   |-- PipelineChart.jsx
    |   |   `-- AiInsightCard.jsx
    |   |
    |   `-- landing/
    |       |-- Hero.jsx
    |       |-- FeatureGrid.jsx
    |       |-- PricingTable.jsx
    |       `-- Testimonials.jsx
    |
    |-- store/                    [ZUSTAND CLIENT STATE]
    |   |-- authStore.js          JWT, user, org
    |   |-- uiStore.js            sidebar, modals, toasts
    |   |-- realtimeStore.js      WebSocket event queue
    |   `-- copilotStore.js       chat history, agent state
    |
    |-- hooks/
    |   |-- useAuth.js            reads from authStore
    |   |-- useWebSocket.js       auto-reconnect WebSocket
    |   |-- useAiStream.js        SSE streaming hook
    |   |-- useJobs.js            React Query hooks
    |   |-- useCandidates.js      React Query hooks
    |   `-- useDebounce.js
    |
    |-- lib/
    |   |-- api.js                axios client + interceptors
    |   |-- auth.js               token storage + refresh logic
    |   |-- validators.js         Yup schemas (replaces Zod)
    |   |-- formatters.js         date, currency, score
    |   `-- constants.js          pipeline stages, roles, enums
    |
    |-- styles/
    |   |-- variables.css         design tokens (CSS custom properties)
    |   |-- reset.css             browser reset
    |   |-- base.css              body, typography, links
    |   |-- utils.css             layout helpers (.flex, .grid, etc.)
    |   |-- animations.css        keyframes
    |   |-- components/           per-component CSS files
    |   |   |-- button.css
    |   |   |-- modal.css
    |   |   |-- sidebar.css
    |   |   |-- kanban.css
    |   |   |-- table.css
    |   |   |-- badge.css
    |   |   |-- card.css
    |   |   |-- toast.css
    |   |   |-- avatar.css
    |   |   |-- tabs.css
    |   |   `-- skeleton.css
    |   `-- pages/                per-page CSS files
    |       |-- dashboard.css
    |       |-- jobs.css
    |       |-- candidates.css
    |       |-- copilot.css
    |       |-- people.css
    |       |-- reports.css
    |       `-- settings.css
    |
    `-- tests/
        |-- unit/                 Vitest + React Testing Library
        |-- e2e/                  Playwright
        `-- __mocks__/


--------------------------------------------------------------------------------
  KEY REFACTORING DECISIONS
--------------------------------------------------------------------------------

1. ROUTING  (Next.js App Router -> React Router v6)
   -----------------------------------------------
   BEFORE:
     app/(app)/jobs/[id]/page.tsx       (file = route)

   AFTER:
     src/routes/AppRouter.jsx
       <Route element={<PrivateRoute />}>
         <Route path="/jobs/:id"        element={<JobPipelinePage />} />
         <Route path="/jobs/:id/edit"   element={<JobEditPage />} />
         <Route path="/jobs/new"        element={<JobNewPage />} />
       </Route>

   Route groups (public) / (auth) / (app) become separate
   <Route> subtrees with their own layout components.


2. CSS  (Tailwind utilities -> Plain CSS + CSS variables)
   -------------------------------------------------------
   BEFORE:
     <div className="flex items-center gap-4 rounded-lg bg-white p-4 shadow-sm">

   AFTER (variables.css):
     :root {
       --color-surface : #ffffff;
       --radius-md     : 8px;
       --spacing-4     : 1rem;
       --shadow-sm     : 0 1px 3px rgba(0,0,0,0.08);
     }

   AFTER (components/card.css):
     .card {
       display       : flex;
       align-items   : center;
       gap           : var(--spacing-4);
       border-radius : var(--radius-md);
       background    : var(--color-surface);
       padding       : var(--spacing-4);
       box-shadow    : var(--shadow-sm);
     }

   AFTER (component):
     <div className="card">


3. TYPESCRIPT -> JAVASCRIPT  (with JSDoc for optional type hints)
   ---------------------------------------------------------------
   BEFORE:
     interface Job {
       id     : string;
       title  : string;
       status : 'active' | 'closed';
     }

   AFTER:
     /**
      * @typedef  {Object}           Job
      * @property {string}           id
      * @property {string}           title
      * @property {'active'|'closed'} status
      */


4. VALIDATION  (Zod -> Yup)
   -------------------------
   BEFORE:
     import { z } from 'zod';
     const jobSchema = z.object({ title: z.string().min(1) });
     jobSchema.parse(data);

   AFTER:
     import * as yup from 'yup';
     const jobSchema = yup.object({ title: yup.string().required().min(1) });
     await jobSchema.validate(data);


5. AUTHENTICATION  (NextAuth -> Custom JWT)
   -----------------------------------------
   BEFORE:
     import { getSession } from 'next-auth/react';
     const session = await getSession();

   AFTER (src/lib/auth.js):
     const KEY = 'hirix_token';
     export const getToken   = ()  => localStorage.getItem(KEY);
     export const setToken   = (t) => localStorage.setItem(KEY, t);
     export const clearToken = ()  => localStorage.removeItem(KEY);

   AFTER (src/hooks/useAuth.js):
     export function useAuth() {
       return useAuthStore((s) => ({ user: s.user, logout: s.logout }));
     }

   AFTER (src/routes/PrivateRoute.jsx):
     import { Navigate, Outlet } from 'react-router-dom';
     import { useAuth } from '@/hooks/useAuth';
     export default function PrivateRoute() {
       const { user } = useAuth();
       return user ? <Outlet /> : <Navigate to="/login" replace />;
     }


6. SERVER COMPONENTS -> REACT QUERY
   ----------------------------------
   BEFORE (Next.js RSC):
     // app/(app)/jobs/page.tsx
     const jobs = await fetch('/api/v1/jobs').then(r => r.json());

   AFTER (src/hooks/useJobs.js):
     import { useQuery } from '@tanstack/react-query';
     import api from '@/lib/api';

     export function useJobs(filters) {
       return useQuery({
         queryKey : ['jobs', filters],
         queryFn  : () => api.get('/jobs', { params: filters })
                            .then(r => r.data),
       });
     }

   AFTER (src/pages/app/jobs/JobsListPage.jsx):
     const { data: jobs, isLoading } = useJobs(filters);


7. API ROUTES REMOVED  (Next.js /api/ -> Vite proxy)
   ---------------------------------------------------
   The entire app/api/ directory is removed.
   Vite proxies all /api and /ws traffic to FastAPI:

   vite.config.js:
     export default {
       server: {
         proxy: {
           '/api' : { target: 'http://localhost:8000', changeOrigin: true },
           '/ws'  : { target: 'ws://localhost:8000',  ws: true },
         }
       },
       resolve: { alias: { '@': '/src' } }
     };


8. SSE STREAMING  (Next.js route handler -> EventSource hook)
   -----------------------------------------------------------
   BEFORE:
     // app/api/ai/copilot/stream/route.ts
     export async function GET(req) { ... }

   AFTER (src/hooks/useAiStream.js):
     export function useAiStream() {
       const startStream = useCallback((prompt, onChunk, onDone) => {
         const url = '/api/ai/copilot/stream?q=' + encodeURIComponent(prompt);
         const es  = new EventSource(url);
         es.onmessage = (e) => onChunk(e.data);
         es.onerror   = ()  => { es.close(); onDone(); };
       }, []);
       return { startStream };
     }


9. WEBSOCKET  (identical hook, path alias updated)
   -------------------------------------------------
   src/hooks/useWebSocket.js
     const ws = new WebSocket(`wss://${host}/ws/${companyId}/${userId}`);
     // auto-reconnect logic with exponential backoff unchanged


10. AXIOS CLIENT  (lib/api.ts -> lib/api.js)
    -----------------------------------------
    src/lib/api.js:
      import axios from 'axios';
      import { getToken, clearToken } from './auth';

      const api = axios.create({ baseURL: '/api/v1' });

      api.interceptors.request.use((config) => {
        const token = getToken();
        if (token) config.headers.Authorization = `Bearer ${token}`;
        return config;
      });

      api.interceptors.response.use(
        (res) => res,
        (err) => {
          if (err.response?.status === 401) clearToken();
          return Promise.reject(err);
        }
      );

      export default api;


--------------------------------------------------------------------------------
  SYSTEM ARCHITECTURE — FRONTEND TOUCHPOINTS (unchanged)
--------------------------------------------------------------------------------

  Frontend Module                   Backend System                   Protocol
  --------------------------------  -------------------------------  ----------
  AICopilotPage.jsx                 L1 Agentic — Copilot Agent       SSE stream
  JobPipelinePage.jsx (kanban)      L4 Application — Screening       REST + WS
  CandidateProfilePage.jsx          L5 Domain — Candidate AR         REST
  AIPerformancePage.jsx             L1 Analytics + L4 Reports        REST
  realtimeStore.js                  L6 Kafka -> L4 Workers -> WS     WebSocket
  copilotStore.js                   L1 Orchestrator — Redis memory   SSE
  useAiStream.js                    L2 LLM Adapters (OpenAI / Ant.)  SSE
  ReasoningTrace.jsx                L1 Reasoning Trace — audit       REST
  AgentStatusCard.jsx               L1 Agent Task Queue state        REST / WS
  AIAutomationPage.jsx              L8 Governance — Policy Engine    REST
  SecurityPage.jsx                  L7 IAM — Okta / KeyCloak / RBAC  REST


--------------------------------------------------------------------------------
  WEBSOCKET EVENT SCHEMAS  (consumed by frontend)
--------------------------------------------------------------------------------

  Event                   Handler                          Effect
  ----------------------  -------------------------------  ---------------------
  SCREENING_COMPLETED     realtimeStore.js                 kanban card update
  AGENT_HEARTBEAT         AgentStatusCard.jsx              live state refresh
  HUMAN_REVIEW_REQUIRED   CandidateDrawer.jsx              review banner shown
  SCREENING_FAILED        uiStore.js -> Toast              error toast shown
  HIRING_DECISION_MADE    KanbanBoard.jsx                  pipeline stage update


--------------------------------------------------------------------------------
  STATE MANAGEMENT
--------------------------------------------------------------------------------

  Server state (API data)          -> React Query (@tanstack/react-query v5)
  Client / UI state                -> Zustand stores
  Form state                       -> React Hook Form + Yup

  Zustand stores:
    authStore.js      JWT token, user object, org info
    uiStore.js        sidebar open/close, active modals, toast queue
    realtimeStore.js  WebSocket event queue, connection status
    copilotStore.js   chat message history, active agent state


--------------------------------------------------------------------------------
  DEPENDENCY MAP
--------------------------------------------------------------------------------

  Runtime
  -------
  react@18                          UI framework
  react-dom@18                      DOM renderer
  react-router-dom@6                client-side routing
  @tanstack/react-query@5           server state / data fetching
  zustand                           client state management
  axios                             HTTP client with interceptors
  yup                               form schema validation
  react-hook-form                   form state management
  recharts                          charts for reports pages

  Build / Dev
  -----------
  vite                              build tool + dev server + proxy
  @vitejs/plugin-react              JSX transform

  Testing
  -------
  vitest                            unit test runner
  @testing-library/react            component testing
  @testing-library/user-event       user interaction simulation
  playwright                        end-to-end tests


--------------------------------------------------------------------------------
  STYLE SYSTEM  (src/styles/variables.css)
--------------------------------------------------------------------------------

  :root {
    /* Brand */
    --color-primary      : #6366f1;
    --color-primary-dark : #4f46e5;

    /* Surfaces */
    --color-surface      : #ffffff;
    --color-bg           : #f8f8f7;
    --color-bg-secondary : #f1f0ec;

    /* Text */
    --color-text         : #1a1a18;
    --color-text-muted   : #6b6b67;
    --color-text-hint    : #9a9a94;

    /* Border */
    --color-border       : rgba(0, 0, 0, 0.10);
    --color-border-focus : #6366f1;

    /* Status */
    --color-success      : #16a34a;
    --color-warning      : #d97706;
    --color-danger       : #dc2626;
    --color-info         : #2563eb;

    /* Spacing scale (4px base) */
    --spacing-1  : 0.25rem;
    --spacing-2  : 0.5rem;
    --spacing-3  : 0.75rem;
    --spacing-4  : 1rem;
    --spacing-6  : 1.5rem;
    --spacing-8  : 2rem;
    --spacing-12 : 3rem;
    --spacing-16 : 4rem;

    /* Border radii */
    --radius-sm  : 4px;
    --radius-md  : 8px;
    --radius-lg  : 12px;
    --radius-xl  : 16px;
    --radius-full: 9999px;

    /* Shadows */
    --shadow-sm  : 0 1px 3px rgba(0,0,0,0.08);
    --shadow-md  : 0 4px 12px rgba(0,0,0,0.10);
    --shadow-lg  : 0 8px 24px rgba(0,0,0,0.12);

    /* Typography */
    --font-sans  : 'Inter', system-ui, -apple-system, sans-serif;
    --font-mono  : 'JetBrains Mono', 'Fira Code', monospace;
    --text-xs    : 0.75rem;
    --text-sm    : 0.875rem;
    --text-base  : 1rem;
    --text-lg    : 1.125rem;
    --text-xl    : 1.25rem;
    --text-2xl   : 1.5rem;

    /* Transitions */
    --transition : 150ms ease;
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --color-surface      : #1e1e1c;
      --color-bg           : #141413;
      --color-bg-secondary : #1a1a18;
      --color-text         : #e8e8e4;
      --color-text-muted   : #9a9a94;
      --color-text-hint    : #6b6b67;
      --color-border       : rgba(255, 255, 255, 0.10);
    }
  }


================================================================================
  END OF HIRIX REACT.JS ARCHITECTURE DOCUMENT
================================================================================