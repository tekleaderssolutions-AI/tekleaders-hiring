import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Mail, ArrowLeft, CheckCircle, Send } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (!email.trim()) return setError('Please enter your email address');
    if (!/\S+@\S+\.\S+/.test(email)) return setError('Please enter a valid email address');

    setIsLoading(true);
    // Simulate API call — in production this calls POST /api/v1/auth/forgot-password
    setTimeout(() => {
      setIsLoading(false);
      setIsSent(true);
    }, 1500);
  };

  const handleResend = () => {
    setIsSent(false);
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setIsSent(true);
    }, 1500);
  };

  return (
    <div className="auth-page">
      <div className="auth-orb auth-orb-1" />
      <div className="auth-orb auth-orb-2" />
      <div className="auth-orb auth-orb-3" />

      <div className="auth-card">
        {/* Back to login */}
        <Link to="/login" className="auth-back-link">
          <ArrowLeft size={16} />
          <span>Back to login</span>
        </Link>

        {!isSent ? (
          <>
            {/* Header */}
            <div className="auth-header">
              <div className="auth-icon-circle">
                <Mail size={28} />
              </div>
              <h1 className="auth-title">Forgot your password?</h1>
              <p className="auth-subtitle">
                No worries! Enter your email and we'll send you a link to reset your password.
              </p>
            </div>

            {/* Error */}
            {error && (
              <div className="auth-error">
                <span>{error}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="auth-form">
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

              <button
                type="submit"
                className="auth-submit-btn"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="auth-spinner" />
                ) : (
                  <>
                    <Send size={16} />
                    Send Reset Link
                  </>
                )}
              </button>
            </form>
          </>
        ) : (
          /* ── Success State ── */
          <div className="auth-success animate-fade-in-up">
            <div className="auth-success-icon">
              <CheckCircle size={48} />
            </div>
            <h2 className="auth-title">Check your email</h2>
            <p className="auth-subtitle">
              We've sent a password reset link to
            </p>
            <div className="auth-email-badge">
              <Mail size={14} />
              <span>{email}</span>
            </div>
            <p className="auth-success-hint">
              Didn't receive the email? Check your spam folder or
            </p>
            <button
              className="auth-resend-btn"
              onClick={handleResend}
              disabled={isLoading}
            >
              {isLoading ? 'Sending...' : 'Resend email'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
