import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Mail, ArrowRight, Shield, Zap, Check } from 'lucide-react'
import PasswordInput from '../components/ui/PasswordInput'

const PERKS = [
  '14-day free trial, no credit card required',
  'AI-powered email personalization included',
  'Cancel anytime, no questions asked',
]

export default function Signup() {
  const [email, setEmail]                   = useState('')
  const [password, setPassword]             = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError]                   = useState('')
  const [loading, setLoading]               = useState(false)
  const { signup }                          = useAuth()
  const navigate                            = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (password !== confirmPassword) { setError('Passwords do not match'); return }
    setLoading(true)
    try {
      await signup(email, password)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create account')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-bg">
        <div className="auth-orb auth-orb-1" />
        <div className="auth-orb auth-orb-2" />
        <div className="auth-orb auth-orb-3" />
        <div className="auth-grid" />
      </div>

      {/* Left panel */}
      <div className="auth-left">
        <div className="auth-logo">
          <div className="auth-logo-icon"><Zap size={18} className="text-white" /></div>
          <span className="auth-logo-text">Lead Gen AI</span>
        </div>

        <div className="auth-hero">
          <div className="auth-badge">
            <span className="auth-badge-dot" />
            Free for 14 days
          </div>
          <h2 className="auth-headline">
            Start closing more<br />
            <span className="auth-headline-gradient">deals today</span>
          </h2>
          <p className="auth-subheadline">
            Join 500+ B2B teams using Lead Gen AI to automate outreach, discover leads, and convert at scale.
          </p>

          <ul className="auth-features">
            {PERKS.map((p) => (
              <li key={p} className="auth-feature-item">
                <div className="auth-feature-icon"><Check size={13} /></div>
                <span>{p}</span>
              </li>
            ))}
          </ul>

          <div className="auth-stats">
            {[['500+', 'Teams onboarded'], ['50M+', 'Leads discovered'], ['3 wks', 'Avg. time to ROI']].map(([v, l]) => (
              <div key={l} className="auth-stat">
                <p className="auth-stat-val">{v}</p>
                <p className="auth-stat-lab">{l}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="auth-testimonial">
          <div className="auth-avatar-row">
            {['J', 'S', 'R'].map((l, i) => (
              <div key={i} className="auth-avatar" style={{ marginLeft: i ? '-8px' : 0 }}>{l}</div>
            ))}
            <span className="auth-avatar-text">500+ happy teams</span>
          </div>
          <p className="auth-testimonial-quote">
            "Set up in 10 minutes, booked 5 meetings in the first week. Absolutely game-changing."
          </p>
          <p className="auth-testimonial-author">— James T., VP Sales at Nexora</p>
        </div>
      </div>

      {/* Right panel */}
      <div className="auth-right">
        <div className="auth-logo auth-logo-mobile">
          <div className="auth-logo-icon"><Zap size={18} className="text-white" /></div>
          <span className="auth-logo-text">Lead Gen AI</span>
        </div>

        <div className="auth-card animate-fade-up">
          <div className="auth-card-header">
            <h1 className="auth-card-title">Create your account</h1>
            <p className="auth-card-subtitle">Start your 14-day free trial — no card needed</p>
          </div>

          {error && (
            <div className="auth-error">
              <span>⚠</span><span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="auth-field">
              <label className="auth-label">Email address</label>
              <div className="auth-input-wrap">
                <Mail size={15} className="auth-input-icon" />
                <input
                  type="email" value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required autoComplete="email"
                  placeholder="you@company.com"
                  className="auth-input"
                />
              </div>
            </div>

            <PasswordInput
              label="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required autoComplete="new-password"
              placeholder="Min. 8 characters"
              dark
            />

            <PasswordInput
              label="Confirm password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required autoComplete="new-password"
              placeholder="••••••••"
              dark
            />

            <button type="submit" disabled={loading} className="auth-submit">
              {loading ? (
                <svg className="auth-spinner" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
              ) : (<>Create free account <ArrowRight size={16} /></>)}
            </button>
          </form>

          <p style={{ fontSize: '0.7rem', color: '#343a52', textAlign: 'center', marginTop: '0.75rem', lineHeight: 1.5 }}>
            By signing up you agree to our{' '}
            <a href="#" style={{ color: '#7c3aed' }}>Terms</a> and{' '}
            <a href="#" style={{ color: '#7c3aed' }}>Privacy Policy</a>
          </p>

          <p className="auth-switch">
            Already have an account?{' '}
            <Link to="/login" className="auth-switch-link">Sign in</Link>
          </p>

          <div className="auth-security">
            <Shield size={12} /><span>256-bit encryption · SOC 2 compliant</span>
          </div>
        </div>
      </div>
    </div>
  )
}
