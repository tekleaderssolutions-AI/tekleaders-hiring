import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PrivateRoute from './PrivateRoute';
import PublicOnlyRoute from './PublicOnlyRoute';

/* ── Layout ── */
import AppShell from '@/components/layout/AppShell';

/* ── Public Pages ── */
import HomePage from '@/pages/public/HomePage';
import CareersPage from '@/pages/public/CareersPage';
import JobApplyPage from '@/pages/public/JobApplyPage';

/* ── Auth Pages ── */
import LoginPage from '@/pages/auth/LoginPage';
import SignupPage from '@/pages/auth/SignupPage';
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage';
import ResetPasswordPage from '@/pages/auth/ResetPasswordPage';
import OnboardingPage from '@/pages/auth/OnboardingPage';

/* ── App Pages ── */
import DashboardPage from '@/pages/app/DashboardPage';
import ClientsPage from '@/pages/app/clients/ClientsPage';
import JDAssignPage from '@/pages/app/admin/JDAssignPage';
import EmployeesPage from '@/pages/app/admin/EmployeesPage';
import SubmitCandidatePage from '@/pages/app/recruiter/SubmitCandidatePage';
import JobsListPage from '@/pages/app/jobs/JobsListPage';
import JobNewPage from '@/pages/app/jobs/JobNewPage';
import JobPipelinePage from '@/pages/app/jobs/JobPipelinePage';
import JobEditPage from '@/pages/app/jobs/JobEditPage';
import JobOverviewPage from '@/pages/app/jobs/JobOverviewPage';
import JobApplicationFormPage from '@/pages/app/jobs/JobApplicationFormPage';
import JobReportsPage from '@/pages/app/jobs/JobReportsPage';
import JobSettingsPage from '@/pages/app/jobs/JobSettingsPage';
import CandidatesPage from '@/pages/app/candidates/CandidatesPage';
import CandidateProfilePage from '@/pages/app/candidates/CandidateProfilePage';
import AICopilotPage from '@/pages/app/ai-copilot/AICopilotPage';
import PeoplePage from '@/pages/app/people/PeoplePage';
import EmployeeProfilePage from '@/pages/app/people/EmployeeProfilePage';
import OrgChartPage from '@/pages/app/people/OrgChartPage';
import PeopleOnboardingPage from '@/pages/app/people/OnboardingPage';
import PerformancePage from '@/pages/app/people/PerformancePage';
import CalendarPage from '@/pages/app/calendar/CalendarPage';
import MailPage from '@/pages/app/mail/MailPage';
import ReportsOverviewPage from '@/pages/app/reports/ReportsOverviewPage';
import PipelineReportPage from '@/pages/app/reports/PipelineReportPage';
import AIPerformancePage from '@/pages/app/reports/AIPerformancePage';
import DiversityPage from '@/pages/app/reports/DiversityPage';
import CustomReportPage from '@/pages/app/reports/CustomReportPage';
import FilesPage from '@/pages/app/files/FilesPage';
import InboxPage from '@/pages/app/inbox/InboxPage';
import SettingsLayout from '@/pages/app/settings/SettingsLayout';
import CompanySettingsPage from '@/pages/app/settings/CompanySettingsPage';
import TeamSettingsPage from '@/pages/app/settings/TeamSettingsPage';
import AIAutomationPage from '@/pages/app/settings/AIAutomationPage';
import IntegrationsPage from '@/pages/app/settings/IntegrationsPage';
import BillingPage from '@/pages/app/settings/BillingPage';
import SecurityPage from '@/pages/app/settings/SecurityPage';
import APIKeysPage from '@/pages/app/settings/APIKeysPage';

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ── Public Routes ── */}
        <Route path="/" element={<HomePage />} />
        <Route path="/careers/:company" element={<CareersPage />} />
        <Route path="/apply/:id" element={<JobApplyPage />} />

        {/* ── Auth Routes (redirect if already logged in) ── */}
        <Route element={<PublicOnlyRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
        </Route>
        {/* Onboarding is accessible whether logged in or not */}
        {/* ── App Routes (requires auth) ── */}
        <Route element={<PrivateRoute />}>
          <Route path="/onboarding" element={<OnboardingPage />} />
          
          <Route element={<AppShell />}>
            <Route path="/dashboard" element={<DashboardPage />} />

            {/* Admin */}
            <Route path="/clients" element={<ClientsPage />} />
            <Route path="/team" element={<EmployeesPage />} />
            <Route path="/jobs/:id/assign" element={<JDAssignPage />} />

            {/* Recruiter */}
            <Route path="/recruiter/jobs/:jobId/submit" element={<SubmitCandidatePage />} />

            {/* Jobs */}
            <Route path="/jobs" element={<JobsListPage />} />
            <Route path="/jobs/new" element={<JobNewPage />} />
            <Route path="/jobs/:id" element={<JobPipelinePage />} />
            <Route path="/jobs/:id/edit" element={<JobEditPage />} />
            <Route path="/jobs/:id/overview" element={<JobOverviewPage />} />
            <Route path="/jobs/:id/application-form" element={<JobApplicationFormPage />} />
            <Route path="/jobs/:id/reports" element={<JobReportsPage />} />
            <Route path="/jobs/:id/settings" element={<JobSettingsPage />} />

            {/* Candidates */}
            <Route path="/candidates" element={<CandidatesPage />} />
            <Route path="/candidates/:id" element={<CandidateProfilePage />} />

            {/* AI Copilot */}
            <Route path="/copilot" element={<AICopilotPage />} />

            {/* People */}
            <Route path="/people" element={<PeoplePage />} />
            <Route path="/people/:id" element={<EmployeeProfilePage />} />
            <Route path="/people/org-chart" element={<OrgChartPage />} />
            <Route path="/people/onboarding" element={<PeopleOnboardingPage />} />
            <Route path="/people/performance" element={<PerformancePage />} />

            {/* Calendar */}
            <Route path="/calendar" element={<CalendarPage />} />

            {/* Mail */}
            <Route path="/mail" element={<MailPage />} />

            {/* Reports */}
            <Route path="/reports" element={<ReportsOverviewPage />} />
            <Route path="/reports/pipeline" element={<PipelineReportPage />} />
            <Route path="/reports/ai-performance" element={<AIPerformancePage />} />
            <Route path="/reports/diversity" element={<DiversityPage />} />
            <Route path="/reports/custom" element={<CustomReportPage />} />

            {/* Files */}
            <Route path="/files" element={<FilesPage />} />

            {/* Inbox */}
            <Route path="/inbox" element={<InboxPage />} />

            {/* Settings */}
            <Route element={<SettingsLayout />}>
              <Route path="/settings" element={<CompanySettingsPage />} />
              <Route path="/settings/team" element={<TeamSettingsPage />} />
              <Route path="/settings/security" element={<SecurityPage />} />
              <Route path="/settings/integrations" element={<IntegrationsPage />} />
              <Route path="/settings/api-keys" element={<APIKeysPage />} />
              <Route path="/settings/ai-automation" element={<AIAutomationPage />} />
              <Route path="/settings/billing" element={<BillingPage />} />
            </Route>
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
