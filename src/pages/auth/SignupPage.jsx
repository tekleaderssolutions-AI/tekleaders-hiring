import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, User, Mail, Lock, Eye, EyeOff, ArrowRight, CheckCircle, Building2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { authService } from '@/lib/authService';
import { GoogleLogin } from '@react-oauth/google';

export default function SignupPage() {
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [form, setForm] = useState({ firstName: '', lastName: '', companyName: '', email: '', password: '', confirm: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const update = (k, v) => setForm({ ...form, [k]: v });

  const handleGoogleSuccess = async (credentialResponse) => {
    setIsLoading(true);
    setError('');
    try {
      const response = await authService.loginWithGoogle(credentialResponse.credential);
      
      if (response && response.token) {
        await login(response.token);
        navigate('/dashboard');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail[0].msg : (detail || err.message || 'Google signup failed'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailSignup = async (e) => {
    e.preventDefault();
    setError('');
    if (!form.firstName.trim()) return setError('Please enter your first name');
    if (!form.lastName.trim()) return setError('Please enter your last name');
    if (!form.email.trim()) return setError('Please enter your email address');
    if (form.password.length < 8) return setError('Password must be at least 8 characters');
    if (form.password !== form.confirm) return setError('Passwords do not match');

    setIsLoading(true);
    try {
      const payload = {
        first_name: form.firstName.trim(),
        last_name: form.lastName.trim(),
        company_name: form.companyName.trim() || undefined,
        email: form.email.trim(),
        password: form.password,
        re_password: form.confirm
      };
      
      const response = await authService.registerUser(payload);
      
      // If the backend returns a token immediately upon signup
      if (response && response.token) {
        await login(response.token);
        navigate('/dashboard');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail[0].msg : (detail || 'Registration failed'));
    } finally {
      setIsLoading(false);
    }
  };

  const strengthChecks = [
    { label: 'At least 8 characters', met: form.password.length >= 8 },
    { label: 'Contains a number', met: /\d/.test(form.password) },
    { label: 'Contains uppercase', met: /[A-Z]/.test(form.password) },
  ];

  return (
    <div className="auth-page">
      <div className="auth-orb auth-orb-1" />
      <div className="auth-orb auth-orb-2" />
      <div className="auth-orb auth-orb-3" />

      <div className="auth-card">
        {/* Logo & Header */}
        <div className="auth-header">
          <Link to="/" className="auth-logo">
            <Sparkles size={32} />
            <span>Hirix</span>
          </Link>
          <h1 className="auth-title">Create your account</h1>
          <p className="auth-subtitle">Start hiring smarter with AI today</p>
        </div>

        {/* Error */}
        {error && (
          <div className="auth-error">
            <span>{error}</span>
          </div>
        )}

        {/* Google Sign Up */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 'var(--spacing-4)', minHeight: 40 }}>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError('Google signup popup closed or failed.')}
            useOneTap
            shape="rectangular"
            size="large"
            theme="outline"
            text="signup_with"
            width="100%"
          />
        </div>

        {/* Divider */}
        <div className="auth-divider">
          <div className="auth-divider-line" />
          <span className="auth-divider-text">or</span>
          <div className="auth-divider-line" />
        </div>

        {/* Email toggle / form */}
        {!showEmailForm ? (
          <button
            className="auth-email-toggle"
            onClick={() => setShowEmailForm(true)}
          >
            <Mail size={18} />
            <span>Sign up with Email</span>
            <ArrowRight size={16} className="auth-email-arrow" />
          </button>
        ) : (
          <form onSubmit={handleEmailSignup} className="auth-form animate-fade-in-up">
            <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
              <div className="auth-form-group" style={{ flex: 1 }}>
                <label className="auth-label">First name</label>
                <div className="auth-input-wrap">
                  <User size={16} className="auth-input-icon" />
                  <input
                    type="text"
                    className="auth-input"
                    placeholder="Jane"
                    value={form.firstName}
                    onChange={(e) => update('firstName', e.target.value)}
                    autoFocus
                    autoComplete="given-name"
                  />
                </div>
              </div>

              <div className="auth-form-group" style={{ flex: 1 }}>
                <label className="auth-label">Last name</label>
                <div className="auth-input-wrap">
                  <User size={16} className="auth-input-icon" />
                  <input
                    type="text"
                    className="auth-input"
                    placeholder="Doe"
                    value={form.lastName}
                    onChange={(e) => update('lastName', e.target.value)}
                    autoComplete="family-name"
                  />
                </div>
              </div>
            </div>

            <div className="auth-form-group">
              <label className="auth-label">Company name</label>
              <div className="auth-input-wrap">
                <Building2 size={16} className="auth-input-icon" />
                <input
                  type="text"
                  className="auth-input"
                  placeholder="Acme Recruitment"
                  value={form.companyName}
                  onChange={(e) => update('companyName', e.target.value)}
                  autoComplete="organization"
                />
              </div>
            </div>

            <div className="auth-form-group">
              <label className="auth-label">Email address</label>
              <div className="auth-input-wrap">
                <Mail size={16} className="auth-input-icon" />
                <input
                  type="email"
                  className="auth-input"
                  placeholder="you@company.com"
                  value={form.email}
                  onChange={(e) => update('email', e.target.value)}
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="auth-form-group">
              <label className="auth-label">Password</label>
              <div className="auth-input-wrap">
                <Lock size={16} className="auth-input-icon" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="auth-input"
                  placeholder="Min 8 characters"
                  value={form.password}
                  onChange={(e) => update('password', e.target.value)}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="auth-eye-btn"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {/* Password strength */}
              {form.password.length > 0 && (
                <div className="auth-pw-strength animate-fade-in-up">
                  {strengthChecks.map((c) => (
                    <div key={c.label} className={`auth-pw-check ${c.met ? 'met' : ''}`}>
                      <CheckCircle size={12} />
                      <span>{c.label}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="auth-form-group">
              <label className="auth-label">Confirm password</label>
              <div className="auth-input-wrap">
                <Lock size={16} className="auth-input-icon" />
                <input
                  type="password"
                  className="auth-input"
                  placeholder="••••••••"
                  value={form.confirm}
                  onChange={(e) => update('confirm', e.target.value)}
                  autoComplete="new-password"
                />
              </div>
            </div>

            <button
              type="submit"
              className="auth-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? <span className="auth-spinner" /> : 'Create Account'}
            </button>

            <p className="auth-terms">
              By creating an account, you agree to our{' '}
              <a href="#">Terms of Service</a> and{' '}
              <a href="#">Privacy Policy</a>
            </p>

            <button
              type="button"
              className="auth-back-btn"
              onClick={() => { setShowEmailForm(false); setError(''); }}
            >
              ← Back to all options
            </button>
          </form>
        )}

        {/* Footer */}
        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login" className="auth-footer-link">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
