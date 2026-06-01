import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import { useAuth } from '@/hooks/useAuth';
import { authService } from '@/lib/authService';
import { GoogleLogin } from '@react-oauth/google';

export default function LoginPage() {
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

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
      setError(Array.isArray(detail) ? detail[0].msg : (detail || err.message || 'Google login failed'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setError('');
    if (!email.trim()) return setError('Please enter your email address');
    if (!password.trim()) return setError('Please enter your password');
    if (password.length < 6) return setError('Password must be at least 6 characters');

    setIsLoading(true);
    try {
      const response = await authService.loginWithEmail(email, password);
      if (response && response.token) {
        await login(response.token);
        navigate('/dashboard');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail[0].msg : (detail || 'Invalid email or password'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Background decorative elements */}
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
          <h1 className="auth-title">Welcome back</h1>
          <p className="auth-subtitle">Sign in to your account to continue</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="auth-error">
            <span>{error}</span>
          </div>
        )}

        {/* Google Sign In — always visible */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 'var(--spacing-4)', minHeight: 40 }}>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError('Google login popup closed or failed.')}
            useOneTap
            shape="rectangular"
            size="large"
            theme="outline"
            text="continue_with"
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
            <span>Continue with Email</span>
            <ArrowRight size={16} className="auth-email-arrow" />
          </button>
        ) : (
          <form onSubmit={handleEmailLogin} className="auth-form animate-fade-in-up">
            <div className="auth-form-group">
              <label className="auth-label">Email address</label>
              <div className="auth-input-wrap">
                <Mail size={16} className="auth-input-icon" />
                <input
                  type="email"
                  className="auth-input"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoFocus
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="auth-form-group">
              <div className="auth-label-row">
                <label className="auth-label">Password</label>
                <Link to="/forgot-password" className="auth-forgot-link">
                  Forgot password?
                </Link>
              </div>
              <div className="auth-input-wrap">
                <Lock size={16} className="auth-input-icon" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="auth-input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
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
            </div>

            <button
              type="submit"
              className="auth-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="auth-spinner" />
              ) : (
                <>Sign In</>
              )}
            </button>

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
          Don't have an account?{' '}
          <Link to="/signup" className="auth-footer-link">
            Create one for free
          </Link>
        </p>
      </div>
    </div>
  );
}
