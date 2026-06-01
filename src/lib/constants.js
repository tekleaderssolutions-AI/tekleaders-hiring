/** Pipeline stages for job hiring flow */
export const PIPELINE_STAGES = [
  { id: 'applied', label: 'Applied', color: '#6b7394' },
  { id: 'screening', label: 'Screening', color: '#4facfe' },
  { id: 'interview', label: 'Interview', color: '#667eea' },
  { id: 'assessment', label: 'Assessment', color: '#764ba2' },
  { id: 'offer', label: 'Offer', color: '#38ef7d' },
  { id: 'hired', label: 'Hired', color: '#11998e' },
  { id: 'rejected', label: 'Rejected', color: '#ff416c' },
];

/** Job types */
export const JOB_TYPES = [
  { value: 'Full-time', label: 'Full-time' },
  { value: 'Part-time', label: 'Part-time' },
  { value: 'Contract', label: 'Contract' },
  { value: 'Internship', label: 'Internship' },
];

/** Job statuses */
export const JOB_STATUSES = [
  { value: 'active', label: 'Active', variant: 'success' },
  { value: 'paused', label: 'Paused', variant: 'warning' },
  { value: 'closed', label: 'Closed', variant: 'neutral' },
  { value: 'draft', label: 'Draft', variant: 'info' },
];

/** User roles */
export const ROLES = [
  { value: 'admin', label: 'Admin' },
  { value: 'recruiter', label: 'Recruiter' },
  { value: 'hiring_manager', label: 'Hiring Manager' },
  { value: 'interviewer', label: 'Interviewer' },
  { value: 'viewer', label: 'Viewer' },
];

/** Departments */
export const DEPARTMENTS = [
  'Engineering', 'Product', 'Design', 'Marketing',
  'Sales', 'HR', 'Finance', 'Operations', 'Legal', 'Customer Success',
];

/** WebSocket event types */
export const WS_EVENTS = {
  SCREENING_COMPLETED: 'SCREENING_COMPLETED',
  AGENT_HEARTBEAT: 'AGENT_HEARTBEAT',
  HUMAN_REVIEW_REQUIRED: 'HUMAN_REVIEW_REQUIRED',
  SCREENING_FAILED: 'SCREENING_FAILED',
  HIRING_DECISION_MADE: 'HIRING_DECISION_MADE',
};

/** Industries */
export const INDUSTRIES = [
  'Technology', 'Healthcare', 'Finance', 'Education', 'Manufacturing', 
  'Retail', 'Consulting', 'Energy', 'Media & Entertainment', 'Real Estate',
];

/** Job Functions */
export const JOB_FUNCTIONS = [
  'Engineering', 'Product Management', 'Design', 'Sales', 'Marketing', 
  'Human Resources', 'Finance', 'Legal', 'Operations', 'Customer Support',
];

/** Experience Levels */
export const EXPERIENCE_LEVELS = [
  'Entry Level', 'Mid Level', 'Senior Level', 'Director', 'Executive', 'Internship',
];

/** Education Levels */
export const EDUCATION_LEVELS = [
  'High School', "Associate's Degree", "Bachelor's Degree", "Master's Degree", 'PhD', 'None',
];
