import React, { useState } from 'react';
import { Trash2, HelpCircle, User, Plus, CloudUpload } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Avatar } from '@/components/ui';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import {
  INDUSTRIES,
  JOB_FUNCTIONS,
  JOB_TYPES,
  EXPERIENCE_LEVELS,
  EDUCATION_LEVELS
} from '@/lib/constants';
import { useCreateJob, useNextJobCode, useAnalyzeJob } from '@/hooks/useJobs';
import { useCandidates, useUploadCandidates, useFetchAndAlign, useBulkProgress } from '@/hooks/useCandidates';
import CandidateMatchCard from '@/components/candidates/CandidateMatchCard';
import useUiStore from '@/store/uiStore';
import { useNavigate } from 'react-router-dom';

function useClients() {
  return useQuery({
    queryKey: ['clients'],
    queryFn: () => api.get('/clients').then(r => r.data),
  });
}

export default function JobNewPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Job details');
  const [activePipelineStage, setActivePipelineStage] = useState('phone');
  const [creationMode, setCreationMode] = useState(null); // null, 'manual', 'upload'
  const createJob = useCreateJob();
  const { data: nextCode } = useNextJobCode();
  const { data: clients = [] } = useClients();
  const analyzeJob = useAnalyzeJob();
  const uploadCandidates = useUploadCandidates();
  const fetchAndAlign = useFetchAndAlign();
  const addToast = useUiStore(s => s.addToast);
  const [selectedTop, setSelectedTop] = useState(3);
  const [scannedCandidates, setScannedCandidates] = useState([]);
  const [scanStats, setScanStats] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    job_code: '',
    department: 'Engineering',
    client_id: '',
    priority: 'medium',
    target_count: 1,
    workplace_type: 'On-site',
    location: '',
    description: '',
    requirements: '',
    benefits: '',
    industry: 'Technology',
    job_function: 'Engineering',
    employment_type: 'Full-time',
    experience_level: 'Entry Level',
    education_level: "Bachelor's Degree",
    keywords: '',
    salary_min: 0,
    salary_max: 0,
    salary_currency: 'INR',
    status: 'draft'
  });

  const [bulkSessionId, setBulkSessionId] = useState(null);
  const { data: bulkProgress } = useBulkProgress(bulkSessionId);

  // Clear session when completed
  React.useEffect(() => {
    if (bulkProgress?.status === 'completed') {
      addToast({ title: 'Upload Complete', message: `Processed ${bulkProgress.processed} of ${bulkProgress.total} resumes.`, type: 'success' });
      setBulkSessionId(null);
    }
  }, [bulkProgress?.status, addToast]);

  const { data: candidates } = useCandidates(
    formData?.id ? { job_id: formData.id } : null,
    { refetchOnWindowFocus: true }
  );
  const sourcedCount = candidates?.length || 0;

  const [uploadFiles, setUploadFiles] = useState([]);

  // Pre-fill job code when fetched
  React.useEffect(() => {
    if (nextCode) {
      // Handle both { code: "..." } and direct string "..." or { next_code: "..." }
      const codeValue = nextCode.code || nextCode.next_code || (typeof nextCode === 'string' ? nextCode : null);
      if (codeValue) {
        setFormData(prev => ({ ...prev, job_code: codeValue }));
      }
    }
  }, [nextCode]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };
  
  const handleSave = async (isDraft = true) => {
    try {
      const workplaceMap = {
        'On-site': 'on_site',
        'Hybrid': 'hybrid',
        'Remote': 'remote'
      };

      // Transform and provide strict defaults to prevent backend Enum crashes
      const dataToSave = {
        title: formData.title || 'Untitled Job',
        job_code: formData.job_code || 'JOB-' + Math.floor(Math.random() * 1000),
        department: formData.department || 'Engineering',
        client_id: formData.client_id || undefined,
        priority: formData.priority || 'medium',
        target_count: Number(formData.target_count) || 1,
        workplace_type: workplaceMap[formData.workplace_type] || 'on_site',
        location: formData.location || 'Remote',
        description: formData.description || 'Job description...',
        requirements: formData.requirements || 'Job requirements...',
        benefits: formData.benefits || 'Job benefits...',
        industry: formData.industry || 'Technology',
        job_function: formData.job_function || 'Engineering',
        employment_type: formData.employment_type || 'Full-time',
        experience_level: formData.experience_level || 'Entry Level',
        education_level: "Bachelor's Degree",
        keywords: formData.keywords ? formData.keywords.split(',').map(k => k.trim()) : [],
        salary_min: Number(formData.salary_min) || 0,
        salary_max: Number(formData.salary_max) || 0,
        salary_currency: formData.salary_currency || 'INR',
        status: isDraft ? 'draft' : 'open'
      };
      
      const response = await createJob.mutateAsync(dataToSave);
      console.log('Create Job Response:', response);
      
      // Update formData with any server-returned fields (like id)
      if (response && response.id) {
        setFormData(prev => ({ ...prev, id: response.id }));
      }
      
      addToast({
        title: isDraft ? 'Draft saved' : 'Job published',
        message: 'Job has been successfully ' + (isDraft ? 'saved as draft' : 'published'),
        type: 'success'
      });


      return response;
    } catch (error) {
      const errorData = error.response?.data?.detail;
      let message = 'Failed to save job';

      if (Array.isArray(errorData)) {
        // Handle FastAPI/Pydantic validation errors
        message = errorData.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
      } else if (typeof errorData === 'string') {
        message = errorData;
      } else if (errorData && typeof errorData === 'object') {
        // Handle objects like { detail: "error message" } or similar
        message = errorData.message || errorData.detail || JSON.stringify(errorData);
      } else if (error.message) {
        message = error.message;
      }

      addToast({
        title: 'Error',
        message: message,
        type: 'error'
      });
      throw error; // Re-throw so callers can handle failure
    }
  };

  const handleUpload = async () => {
    if (uploadFiles.length === 0) return;

    try {
      const formDataObj = new FormData();
      formDataObj.append('file', uploadFiles[0]); // Analysis only needs one file
      formDataObj.append('job_code', formData.job_code);

      addToast({ 
        title: 'Processing', 
        message: 'AI is extracting details from your document...', 
        type: 'info' 
      });

      const extractedData = await analyzeJob.mutateAsync(formDataObj);
      
      // Update form with extracted data
      setFormData(prev => ({
        ...prev,
        ...extractedData,
        // Ensure job_code is preserved if not returned
        job_code: extractedData.job_code || prev.job_code
      }));

      // Clear the files after successful upload
      setUploadFiles([]);
      // Switch to manual mode to review
      setCreationMode('manual');
      setActiveTab('Job details');
    } catch (error) {
      addToast({
        title: 'Error',
        message: error.response?.data?.detail || error.message || 'Failed to analyze document',
        type: 'error'
      });
    }
  };

  const handleCandidateUpload = async () => {
    if (uploadFiles.length === 0) return;

    let jobId = formData.id;
    let jobCode = formData.job_code;

    // Auto-save as draft if job hasn't been saved yet
    if (!jobId) {
      try {
        addToast({
          title: 'Saving Job',
          message: 'Saving job draft before uploading candidates...',
          type: 'info'
        });
        const savedJob = await handleSave(true);
        jobId = savedJob.id;
        jobCode = savedJob.job_code;
      } catch (error) {
        // handleSave already shows toast
        return;
      }
    }

    try {
      const formDataObj = new FormData();
      // Use 'file' (singular)
      formDataObj.append('file', uploadFiles[0]);
      
      // Send job_code and job_id in FormData
      formDataObj.append('job_code', jobCode);
      if (jobId) formDataObj.append('job_id', jobId);

      console.log('Sending upload for job_code:', jobCode);

      setBulkSessionId(null); // clear any stale bulk session before starting
      const response = await uploadCandidates.mutateAsync({
        formData: formDataObj,
        jobCode: jobCode
      });

      if (response?.session_id) {
        // ZIP bulk upload — track progress
        setBulkSessionId(response.session_id);
        addToast({
          title: 'Upload Started',
          message: `Processing ${response.unique_files || response.total_files} resumes in parallel...`,
          type: 'info'
        });
      } else {
        // Single file — already processed synchronously
        addToast({
          title: 'Resume Uploaded',
          message: 'Resume parsed and indexed successfully.',
          type: 'success'
        });
      }
      setUploadFiles([]);
    } catch (error) {
      console.error('Candidate upload failed:', error.response?.data || error.message);
      
      let message = 'Failed to upload candidates';
      const errorData = error.response?.data?.detail;

      if (errorData) {
        // If it's a validation error, show the raw JSON for debugging
        message = typeof errorData === 'object' ? JSON.stringify(errorData) : errorData;
      }

      addToast({
        title: 'Upload Error',
        message: message,
        type: 'error'
      });
    }
  };

  const handleScanWithAI = async () => {
    if (!formData.id) {
      addToast({
        title: 'Save Job First',
        message: 'Please save the job before scanning candidates.',
        type: 'warning'
      });
      return;
    }

    try {
      addToast({
        title: 'Scanning Candidates',
        message: 'AI is fetching and aligning candidates...',
        type: 'info'
      });

      const results = await fetchAndAlign.mutateAsync({
        jobId: formData.id,
        topK: selectedTop,
        rerankThreshold: 60
      });

      const matches = results?.matches || (Array.isArray(results) ? results : []);
      setScanStats(results?.stats || null);
      setScannedCandidates(matches);

      addToast({
        title: 'Scan Complete',
        message: `Successfully scanned and aligned ${matches.length} candidates.`,
        type: 'success'
      });
    } catch (error) {
      addToast({
        title: 'Scan Failed',
        message: error.response?.data?.detail || error.message || 'Failed to scan candidates',
        type: 'error'
      });
    }
  };

  const tabs = [
    'Job details',
    'Team members',
  ];

  const fullName = user?.first_name ? `${user.first_name} ${user.last_name}` : 'caveta N';
  const email = user?.email || 'caveta8872@spotshops.com';

  const renderJobDetails = () => (
    <div className="job-details-form-layout">
      <div className="job-details-form-main">
        {/* Job title and department */}
        <div className="form-section-card">
          <h3 className="form-section-title">Job title and department</h3>
          
          <div className="form-field">
            <label className="form-label-custom"><span>*</span>Job title</label>
            <input 
              type="text" 
              className="form-input-custom" 
              placeholder="e.g. AI Engineer"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
            />
          </div>

          <div className="form-field">
            <label className="form-label-custom">Job code</label>
            <input
              type="text"
              className="form-input-custom"
              placeholder="e.g. 2202"
              value={formData.job_code}
              onChange={(e) => handleChange('job_code', e.target.value)}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginTop: 4 }}>
            <div className="form-field" style={{ margin: 0 }}>
              <label className="form-label-custom">Priority</label>
              <select
                className="form-input-custom"
                value={formData.priority}
                onChange={(e) => handleChange('priority', e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div className="form-field" style={{ margin: 0 }}>
              <label className="form-label-custom">Target Positions</label>
              <input
                type="number"
                min="1"
                className="form-input-custom"
                placeholder="1"
                value={formData.target_count}
                onChange={(e) => handleChange('target_count', e.target.value)}
              />
            </div>
            <div className="form-field" style={{ margin: 0 }}>
              <label className="form-label-custom">Department</label>
              <input
                type="text"
                className="form-input-custom"
                placeholder="Engineering"
                value={formData.department}
                onChange={(e) => handleChange('department', e.target.value)}
              />
            </div>
          </div>

          <div className="form-field" style={{ marginTop: 12 }}>
            <label className="form-label-custom">Client</label>
            <select
              className="form-input-custom"
              value={formData.client_id}
              onChange={(e) => handleChange('client_id', e.target.value)}
            >
              <option value="">— No client —</option>
              {clients.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Location */}
        <div className="form-section-card">
          <h3 className="form-section-title">Location</h3>
          
          <div className="form-field">
            <label className="form-label-custom"><span>*</span>Workplace</label>
            <div className="workplace-options">
              {['On-site', 'Hybrid', 'Remote'].map(type => (
                <label key={type} className="workplace-option">
                  <input 
                    type="radio" 
                    name="workplace" 
                    checked={formData.workplace_type === type}
                    onChange={() => handleChange('workplace_type', type)}
                  />
                  <span className="workplace-label-text">{type}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-field">
            <label className="form-label-custom"><span>*</span>Office location</label>
            <input 
              type="text" 
              className="form-input-custom" 
              placeholder="e.g. New York, NY, United States"
              value={formData.location}
              onChange={(e) => handleChange('location', e.target.value)}
            />
          </div>
        </div>

        {/* Description */}
        <div className="form-section-card">
          <button className="ai-generate-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>
            Generate with AI
          </button>
          <h3 className="form-section-title">Description</h3>
          
          <div className="form-field">
            <label className="form-label-custom"><span>*</span>About the role</label>
            <div className="description-editor-container">
              <div className="description-editor-toolbar">
                <button style={{ background: 'none', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>B</button>
                <button style={{ background: 'none', border: 'none', fontStyle: 'italic', cursor: 'pointer' }}>I</button>
                <button style={{ background: 'none', border: 'none', textDecoration: 'underline', cursor: 'pointer' }}>U</button>
              </div>
              <textarea 
                className="description-editor-textarea" 
                placeholder="Enter the job description here..."
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
              />
            </div>
          </div>

          <div className="form-field">
            <label className="form-label-custom">Requirements</label>
            <textarea 
              className="description-editor-textarea" 
              placeholder="Enter the job requirements here..."
              style={{ minHeight: '120px' }}
              value={formData.requirements}
              onChange={(e) => handleChange('requirements', e.target.value)}
            />
          </div>

          <div className="form-field">
            <label className="form-label-custom">Benefits</label>
            <textarea 
              className="description-editor-textarea" 
              placeholder="Enter the job benefits here..."
              style={{ minHeight: '100px' }}
              value={formData.benefits}
              onChange={(e) => handleChange('benefits', e.target.value)}
            />
          </div>
        </div>

        {/* Company industry and Job function */}
        <div className="form-section-card">
          <h3 className="form-section-title">Company industry and Job function</h3>
          <div className="form-grid-2">
            <div className="form-field">
              <label className="form-label-custom">Company industry</label>
              <select 
                className="form-input-custom"
                value={formData.industry}
                onChange={(e) => handleChange('industry', e.target.value)}
              >
                <option value="">Select industry...</option>
                {INDUSTRIES.map(item => <option key={item} value={item}>{item}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label className="form-label-custom">Job function</label>
              <select 
                className="form-input-custom"
                value={formData.job_function}
                onChange={(e) => handleChange('job_function', e.target.value)}
              >
                <option value="">Select function...</option>
                {JOB_FUNCTIONS.map(item => <option key={item} value={item}>{item}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Employment details */}
        <div className="form-section-card">
          <h3 className="form-section-title">Employment details</h3>
          <div className="form-grid-2">
            <div className="form-field">
              <label className="form-label-custom">Employment type</label>
              <select 
                className="form-input-custom"
                value={formData.employment_type}
                onChange={(e) => handleChange('employment_type', e.target.value)}
              >
                <option value="">Select type...</option>
                {JOB_TYPES.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label className="form-label-custom">Experience</label>
              <select 
                className="form-input-custom"
                value={formData.experience_level}
                onChange={(e) => handleChange('experience_level', e.target.value)}
              >
                <option value="">Select experience...</option>
                {EXPERIENCE_LEVELS.map(item => <option key={item} value={item}>{item}</option>)}
              </select>
            </div>
          </div>
          <div className="form-grid-2">
            <div className="form-field">
              <label className="form-label-custom">Education</label>
              <select 
                className="form-input-custom"
                value={formData.education_level}
                onChange={(e) => handleChange('education_level', e.target.value)}
              >
                <option value="">Select education...</option>
                {EDUCATION_LEVELS.map(item => <option key={item} value={item}>{item}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label className="form-label-custom">Keywords</label>
              <input 
                type="text" 
                className="form-input-custom" 
                placeholder="e.g. React, Python"
                value={formData.keywords}
                onChange={(e) => handleChange('keywords', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Salary details */}
        <div className="form-section-card">
          <h3 className="form-section-title">Salary details</h3>
          <div className="form-grid-3">
            <div className="form-field">
              <label className="form-label-custom">Min salary</label>
              <input 
                type="number" 
                className="form-input-custom" 
                placeholder="0"
                value={formData.salary_min}
                onChange={(e) => handleChange('salary_min', e.target.value)}
              />
            </div>
            <div className="form-field">
              <label className="form-label-custom">Max salary</label>
              <input 
                type="number" 
                className="form-input-custom" 
                placeholder="0"
                value={formData.salary_max}
                onChange={(e) => handleChange('salary_max', e.target.value)}
              />
            </div>
            <div className="form-field">
              <label className="form-label-custom">Currency</label>
              <select 
                className="form-input-custom"
                value={formData.salary_currency}
                onChange={(e) => handleChange('salary_currency', e.target.value)}
              >
                <option value="INR">INR</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
              </select>
            </div>
          </div>
        </div>

        {/* Footer buttons */}
        <div className="btn-group-footer">
          <button
            className="btn-save-continue"
            onClick={async () => { await handleSave(false); setActiveTab('Team members'); }}
            disabled={createJob.isPending}
          >
            {createJob.isPending ? 'Saving...' : 'Save & continue'}
          </button>
          <button 
            className="btn-save-draft" 
            onClick={() => handleSave(true)}
            disabled={createJob.isPending}
          >
            Save draft
          </button>
        </div>
      </div>

    </div>
  );

  const renderTeamMembers = () => (
    <div className="job-content-card">
      <div className="job-content-header">
        <h3>Team members</h3>
        <HelpCircle size={16} color="#ccc" />
      </div>
      
      <div className="job-content-body">
        <div className="member-row">
          <div className="member-info">
            <Avatar name={fullName} size="sm" />
            <span className="member-name">{fullName}</span>
            <span className="member-email">{email}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
            <span className="member-role-text">You're an Admin for this job</span>
            <button style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#999' }}>
              <Trash2 size={18} />
            </button>
          </div>
        </div>

        <div style={{ marginTop: '32px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#999', textTransform: 'uppercase', marginBottom: '8px' }}>
            Other members
          </div>
          <p style={{ fontSize: '14px', color: '#666' }}>
            You can add other account members to your team or invite people to join Workable to collaborate on this job.
          </p>
          
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn-invite-member">
              Invite a new member
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFindCandidates = () => (
    <div className="find-candidates-container">
      {/* Option 1: Document Uploading */}
      <div className="sourcing-option-section" style={{ marginBottom: '40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', maxWidth: '600px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div className="option-number" style={{ padding: '2px 8px', fontSize: '11px' }}>Option 1</div>
            <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: 0 }}>Document Uploading</h3>
          </div>

          <button 
            className="btn-save-continue"
            style={{ padding: '8px 16px', fontSize: '13px' }}
            disabled={uploadFiles.length === 0 || uploadCandidates.isPending}
            onClick={handleCandidateUpload}
          >
            {uploadCandidates.isPending ? 'Uploading...' : 'Upload'}
          </button>
        </div>
        
        <div style={{ maxWidth: '600px' }}>
          <div className="upload-area secondary" style={{ padding: '32px 24px' }} onClick={() => document.getElementById('candidateUpload').click()}>
            <input
              type="file"
              id="candidateUpload"
              hidden
              multiple
              accept=".pdf,.doc,.docx,.zip"
              onChange={(e) => setUploadFiles(e.target.files)}
            />
            <div className="upload-icon-medium" style={{ marginBottom: '12px' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#00756a" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <p className="upload-text" style={{ fontSize: '14px' }}>Upload candidate resumes or a ZIP folder</p>
            <p className="upload-hint" style={{ fontSize: '12px' }}>Supported formats: PDF, DOCS, ZIP</p>
          </div>

          {/* Single-file processing indicator */}
          {uploadCandidates.isPending && !bulkSessionId && (
            <div style={{ marginTop: 16, padding: '14px 16px', background: '#f8fffe', border: '1px solid #a7f3d0', borderRadius: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00756a" strokeWidth="2.5" style={{ animation: 'spin 1s linear infinite', flexShrink: 0 }}>
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                </svg>
                <span style={{ fontSize: 13, fontWeight: 600, color: '#065f46' }}>Parsing resume with AI...</span>
                <span style={{ fontSize: 11, color: '#9ca3af', marginLeft: 'auto' }}>~30s</span>
              </div>
              <div style={{ height: 4, backgroundColor: '#d1fae5', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{
                  height: '100%', width: '100%',
                  background: 'linear-gradient(90deg, #00756a 0%, #34d399 50%, #00756a 100%)',
                  backgroundSize: '200% 100%',
                  animation: 'shimmer 1.5s infinite',
                  borderRadius: 4,
                }} />
              </div>
              <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
              `}</style>
            </div>
          )}

          {/* Progress bar — shown while bulk processing */}
          {bulkProgress && bulkProgress.status !== 'completed' && (
            <div style={{ marginTop: 16, padding: '14px 16px', background: '#f8fffe', border: '1px solid #a7f3d0', borderRadius: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: '#065f46' }}>Processing resumes...</span>
                <span style={{ fontSize: 12, color: '#6b7280' }}>
                  {bulkProgress.processed} of {bulkProgress.total}
                </span>
              </div>
              <div style={{ height: 6, backgroundColor: '#d1fae5', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${Math.round((bulkProgress.processed / Math.max(bulkProgress.total, 1)) * 100)}%`,
                  backgroundColor: '#00756a',
                  borderRadius: 4,
                  transition: 'width 0.4s ease',
                }} />
              </div>
              {bulkProgress.duplicates > 0 && (
                <p style={{ fontSize: 11, color: '#9ca3af', marginTop: 6 }}>
                  {bulkProgress.duplicates} duplicate{bulkProgress.duplicates > 1 ? 's' : ''} skipped
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      <div style={{ textAlign: 'center', margin: '24px 0', color: '#999', fontSize: '12px', fontWeight: 600 }}>OR</div>

      {/* Option 2: Multi-channel Sourcing */}
      <div className="sourcing-option-section">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div className="option-number" style={{ padding: '2px 8px', fontSize: '11px' }}>Option 2</div>
          <h3 className="option-title" style={{ marginBottom: 0, fontSize: '20px' }}>Multi-channel Sourcing</h3>
        </div>

        {/* Step 1 */}
        <div className="sourcing-step">
          <div className="step-marker">1</div>
          <div className="step-content">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <h3 className="step-title" style={{ marginBottom: 0 }}>Get off to the right start</h3>
              <span className="coming-soon-badge">Coming Soon</span>
            </div>
            <p className="step-subtitle">Get the most quality candidates quickly - these actions are our top performers.</p>
            
            <div className="sourcing-grid">
              <div className="sourcing-card">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h10"/><path d="M7 12h10"/><path d="M7 16h6"/></svg></div>
                <h4>Premium job boards</h4>
                <p>Use premium job boards to increase visibility and collect more candidates.</p>
                <button className="sourcing-link">Boost visibility</button>
              </div>

              <div className="sourcing-card">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 1 0-16 0"/></svg></div>
                <h4>Referrals</h4>
                <p>Send an email to your employees inviting them to submit referrals.</p>
                <button className="sourcing-link">Edit Referrals settings</button>
              </div>

              <div className="sourcing-card muted">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></div>
                <h4>Passive candidates</h4>
                <p>Profiles matching your job in our global database.</p>
                <button className="sourcing-link disabled">Preview candidates</button>
              </div>

              <div className="sourcing-card muted">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/></svg></div>
                <h4>Resurfaced candidates</h4>
                <p>Past candidates who match this new job.</p>
                <button className="sourcing-link disabled">Preview candidates</button>
              </div>
            </div>
          </div>
        </div>

        {/* Step 2 */}
        <div className="sourcing-step">
          <div className="step-marker">2</div>
          <div className="step-content">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <h3 className="step-title" style={{ marginBottom: 0 }}>More options to consider</h3>
              <span className="coming-soon-badge">Coming Soon</span>
            </div>
            <p className="step-subtitle">These inbound and outbound sourcing features provide a wide range of ways to find your next hire.</p>
            
            <div className="sourcing-grid">
              <div className="sourcing-card">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="17" y1="11" x2="23" y2="11"/></svg></div>
                <h4>Free job boards</h4>
                <p>Post your job to our network of free job boards to start receiving applications.</p>
                <button className="sourcing-link">View boards</button>
              </div>

              <div className="sourcing-card">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg></div>
                <h4>Invite Recruiters</h4>
                <p>Add external recruiters to your job and allow them to add candidates.</p>
                <button className="sourcing-link">Invite now</button>
              </div>

              <div className="sourcing-card">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg></div>
                <h4>Share on Social Media</h4>
                <div className="social-icons">
                  <span className="social-circle fb">f</span>
                  <span className="social-circle in">in</span>
                  <span className="social-circle tw">𝕏</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Step 3 */}
        <div className="sourcing-step">
          <div className="step-marker">3</div>
          <div className="step-content">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <h3 className="step-title" style={{ marginBottom: 0 }}>Finally, a few smaller actions you can take</h3>
              <span className="coming-soon-badge">Coming Soon</span>
            </div>
            <p className="step-subtitle">Actions that ensure you're receiving candidates from everywhere in your recruiting mix.</p>
            
            <div className="sourcing-grid">
              <div className="sourcing-card">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></div>
                <h4>Website Connect</h4>
                <p>Embed your jobs on your website. We provide the code and update automatically.</p>
                <button className="sourcing-link">Connect</button>
              </div>

              <div className="sourcing-card">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></div>
                <h4>Job Shortlink</h4>
                <div className="sourcing-input-box">https://apply.workable.com/j/7AA...</div>
                <button className="sourcing-link">Copy to clipboard</button>
              </div>

              <div className="sourcing-card">
                <div className="sourcing-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div>
                <h4>Job Mailbox</h4>
                <div className="sourcing-input-box">7AA6F6E414@jobs.workablemail...</div>
                <button className="sourcing-link">Copy to clipboard</button>
              </div>
            </div>
          </div>
        </div>

        <div className="sourcing-step last">
          <div className="step-marker">4</div>
          <div className="step-content">
            <h3 className="step-title">Happy recruiting! Good luck.</h3>
          </div>
        </div>
      </div>
    </div>
  );

  const renderWorkflow = () => {
    const stages = [
      { id: 'sourced', label: 'Sourced', icon: Settings },
      { id: 'applied', label: 'Applied', icon: User },
      { id: 'phone', label: 'Phone Screen', icon: Phone },
      { id: 'assessment', label: 'Assessment', icon: ClipboardCheck },
      { id: 'interview', label: 'Interview', icon: MessageSquare },
      { id: 'offer', label: 'Offer', icon: FileSignature },
      { id: 'hired', label: 'Hired', icon: CheckCircle },
    ];

    return (
      <div className="job-content-card full-fit" style={{ 
        margin: 0, 
        borderRadius: 0, 
        border: 'none'
      }}>
        <div className="job-content-header" style={{ borderBottom: 'none', padding: '24px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#666' }}>Default pipeline</h3>
        </div>
        
        <div className="pipeline-container">
          <div className="pipeline-stages" style={{ 
            display: 'flex', 
            borderTop: '1px solid #eee', 
            borderBottom: '1px solid #eee',
            backgroundColor: '#fcfbf8'
          }}>
            {stages.map((stage, index) => {
              const Icon = stage.icon;
              const isActive = stage.id === activePipelineStage;
              return (
                <div 
                  key={stage.id} 
                  className={`pipeline-stage ${isActive ? 'active' : ''}`}
                  onClick={() => setActivePipelineStage(stage.id)}
                  style={{ 
                    flex: 1, 
                    padding: '24px 12px', 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center', 
                    gap: '12px',
                    borderRight: index < stages.length - 1 ? '1px solid #eee' : 'none',
                    backgroundColor: isActive ? '#fff' : 'transparent',
                    cursor: 'pointer',
                    boxShadow: isActive ? 'inset 0 2px 0 #00756a, 0 4px 12px rgba(0,0,0,0.05)' : 'none',
                    zIndex: isActive ? 1 : 0,
                    position: 'relative',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <Icon size={24} color={isActive ? '#00756a' : '#999'} strokeWidth={1.5} />
                  <span style={{ 
                    fontSize: '12px', 
                    fontWeight: isActive ? 600 : 500, 
                    color: isActive ? '#333' : '#999',
                    whiteSpace: 'nowrap'
                  }}>
                    {stage.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Stage Content */}
        <div className="stage-content-container">
          {activePipelineStage === 'sourced' && (
            <div className="sourced-stage-content">
              {/* Top Controls */}
              <div className="sourced-controls-grid">
                <div className="sourced-control-row" style={{ alignItems: 'flex-start' }}>
                  <label style={{ marginTop: '10px' }}>Source</label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
                    <div className="sourced-select-display">
                      <CloudUpload size={18} color="#00756a" />
                      <span>Document uploading</span>
                      <span className="sourced-count-badge">{sourcedCount}</span>
                    </div>
                  </div>
                </div>

                <div className="sourced-control-row">
                  <label>Selected Top</label>
                  <div className="sourced-number-input-wrapper">
                    <button 
                      className="sourced-number-btn"
                      onClick={() => setSelectedTop(Math.max(1, selectedTop - 1))}
                    >
                      <Plus size={16} style={{ transform: 'rotate(45deg)' }} />
                    </button>
                    <input 
                      type="number" 
                      className="sourced-number-input"
                      value={selectedTop}
                      onChange={(e) => setSelectedTop(parseInt(e.target.value) || 1)}
                    />
                    <button 
                      className="sourced-number-btn"
                      onClick={() => setSelectedTop(selectedTop + 1)}
                    >
                      <Plus size={16} />
                    </button>
                  </div>
                </div>

                <button 
                  className="btn-scan-ai"
                  onClick={handleScanWithAI}
                  disabled={fetchAndAlign.isPending}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>
                  {fetchAndAlign.isPending ? 'Scanning...' : 'Scan with AI'}
                </button>
              </div>

              {/* Candidate List Container */}
              <div className="sourced-candidate-list-container" style={{ padding: scannedCandidates.length > 0 ? '24px' : '40px' }}>
                {scannedCandidates.length > 0 ? (
                  <div>
                    {/* Stats header */}
                    {scanStats && (
                      <div style={{
                        display: 'flex', gap: 20, alignItems: 'center',
                        padding: '10px 0 16px', borderBottom: '1px solid #f3f4f6', marginBottom: 16,
                        fontSize: 13, flexWrap: 'wrap',
                      }}>
                        <span><strong>Total: {scanStats.total}</strong></span>
                        <span style={{ color: '#00756a' }}>Matched: {scanStats.matched}</span>
                        <span style={{ color: '#dc2626' }}>Filtered: {scanStats.filtered}</span>
                        {scanStats.role && (
                          <span style={{ color: '#6b7280' }}>
                            Role: {scanStats.role}{scanStats.seniority ? ` · ${scanStats.seniority}` : ''}
                          </span>
                        )}
                      </div>
                    )}
                    {scannedCandidates.map((c) => (
                      <CandidateMatchCard key={c.resume_id || c.candidate_id} candidate={c} />
                    ))}
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', color: '#999' }}>
                    <div style={{ marginBottom: '16px', opacity: 0.5 }}>
                      <User size={48} strokeWidth={1} />
                    </div>
                    <p style={{ fontSize: '15px', fontWeight: 600, color: '#333', marginBottom: '8px' }}>Candidates will appear here after scanning</p>
                    <p style={{ fontSize: '13px' }}>Click "Scan with AI" to begin processing uploaded documents</p>
                  </div>
                )}
              </div>

              {/* Send Mail Footer */}
              <button className="btn-send-mail">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
                Send Mail
              </button>
            </div>
          )}

          {activePipelineStage !== 'sourced' && (
            <div style={{ padding: '60px', textAlign: 'center', color: '#999' }}>
              <p>Content for {activePipelineStage} stage will appear here.</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderSelectionScreen = () => (
    <div className="creation-mode-selection">
      <div className="selection-container">
        <h2 className="selection-title">How would you like to create this job?</h2>
        <p className="selection-subtitle">Select a method to start setting up your new position.</p>
        
        <div className="selection-grid">
          <div className="selection-card" onClick={() => setCreationMode('manual')}>
            <div className="selection-icon-wrapper manual">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </div>
            <h3 className="selection-card-title">Manual Creation</h3>
            <p className="selection-card-desc">Enter all job details manually using our step-by-step editor.</p>
            <button className="selection-btn">Start Manual</button>
          </div>

          <div className="selection-card" onClick={() => setCreationMode('upload')}>
            <div className="selection-icon-wrapper upload">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <h3 className="selection-card-title">Document Uploading</h3>
            <p className="selection-card-desc">Upload a PDF or Word document. Our AI will automatically extract details.</p>
            <button className="selection-btn">Upload Document</button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUploadMode = () => (
    <div className="upload-mode-container">
      <div className="job-content-card">
        <div className="job-content-header">
          <h3>Upload Job Description</h3>
        </div>
        <div className="job-content-body">
          <div className="upload-area" onClick={() => document.getElementById('fileInput').click()}>
            <input 
              type="file" 
              id="fileInput" 
              hidden 
              accept=".pdf,.doc,.docx"
              onChange={(e) => setUploadFiles(e.target.files)}
            />
            <div className="upload-icon-large">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#00756a" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <p className="upload-text">Click to upload or drag and drop</p>
            <p className="upload-hint">Supported formats: PDF, DOC, DOCX (Max 10MB)</p>
            {uploadFiles.length > 0 && (
              <div className="selected-file-badge">
                {uploadFiles[0].name}
              </div>
            )}
          </div>

          <div className="form-field" style={{ marginTop: '24px', maxWidth: '300px' }}>
            <label className="form-label-custom">Job code (Auto-generated)</label>
            <input 
              type="text" 
              className="form-input-custom" 
              value={formData.job_code}
              readOnly
            />
          </div>

          <div className="btn-group-footer" style={{ marginTop: '40px' }}>
            <button 
              className="btn-save-continue"
              disabled={uploadFiles.length === 0 || analyzeJob.isPending}
              onClick={handleUpload}
            >
              {analyzeJob.isPending ? 'Uploading...' : 'Upload'}
            </button>
            <button className="btn-save-draft" onClick={() => setCreationMode(null)}>
              Back
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  if (!creationMode) {
    return renderSelectionScreen();
  }

  return (
    <div className="job-create-container" style={{ maxWidth: '100%', width: '100%', padding: 0 }}>
      {/* Header section */}
      <div className="job-create-header" style={{ padding: '24px 40px' }}>
        <div className="job-create-header-top">
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button 
              onClick={() => setCreationMode(null)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center', color: '#666' }}
              title="Back to selection"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
            </button>
            <div>
              <h1 className="job-draft-title">
                {(formData.id && creationMode === 'manual') ? (
                  <>
                    {formData.title} <span className="job-draft-label">({formData.job_code})</span>
                  </>
                ) : 'New Job'}
              </h1>
              {formData.id && creationMode === 'manual' && (
                <div className="job-create-meta">
                  {formData.workplace_type} • {formData.location}
                </div>
              )}
            </div>
          </div>
          
          <div className="job-create-actions">
            <button 
              className="btn-preview" 
              onClick={() => handleSave(true)}
              disabled={createJob.isPending}
            >
              Save draft
            </button>
            <button
              className="btn-save-continue"
              onClick={async () => { await handleSave(false); setActiveTab('Team members'); }}
              disabled={createJob.isPending}
            >
              {createJob.isPending ? 'Saving...' : 'Save & continue'}
            </button>
          </div>
        </div>

        <div className="job-create-tabs" style={{ display: 'flex', justifyContent: 'space-between', padding: '0 40px' }}>
          {tabs.map(tab => (
            <div 
              key={tab} 
              className={`job-tab ${activeTab === tab ? 'active' : ''}`}
              style={{ flex: 1, textAlign: 'center' }}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content section */}
      <div className="job-create-content" style={activeTab === 'Workflow' ? { padding: 0, maxWidth: '100%' } : {}}>
        {activeTab === 'Job details' && (
          creationMode === 'manual' ? renderJobDetails() : renderUploadMode()
        )}
        {activeTab === 'Team members' && renderTeamMembers()}
      </div>
    </div>
  );
}
