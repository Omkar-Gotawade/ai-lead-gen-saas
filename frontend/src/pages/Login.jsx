import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Mail, ArrowRight, Shield, Zap, TrendingUp, Users } from 'lucide-react'
import PasswordInput from '../components/ui/PasswordInput'

const FEATURES = [
  { icon: Zap,        text: 'AI-powered lead discovery across 50M+ contacts' },
  { icon: TrendingUp, text: 'Automated multi-step email sequences' },
  { icon: Mail,       text: 'Real-time deliverability monitoring' },
  { icon: Shield,     text: 'Smart personalization with Gemini AI' },
]

const STATS = [
  { val: '10×',   lab: 'Faster outreach' },
  { val: '50M+',  lab: 'Contacts indexed' },
  { val: '99.9%', lab: 'Uptime SLA' },
]

export default function Login() {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)
  const { login }               = useAuth()
  const navigate                = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/leads')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      {/* ── Animated background ── */}
      <div className="auth-bg">
        <div className="auth-orb auth-orb-1" />
        <div className="auth-orb auth-orb-2" />
        <div className="auth-orb auth-orb-3" />
        <div className="auth-grid" />
      </div>

      {/* ── Left panel ── */}
      <div className="auth-left">
        {/* Logo */}
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <Zap size={18} className="text-white" />
          </div>
          <span className="auth-logo-text">Lead Gen AI</span>
        </div>

        {/* Hero copy */}
        <div className="auth-hero">
          <div className="auth-badge">
            <span className="auth-badge-dot" />
            Trusted by 500+ B2B teams
          </div>
          <h2 className="auth-headline">
            Grow your pipeline<br />
            <span className="auth-headline-gradient">with AI automation</span>
          </h2>
          <p className="auth-subheadline">
            The smartest outreach platform for B2B teams — discover, engage, and convert leads at scale.
          </p>

          {/* Feature list */}
          <ul className="auth-features">
            {FEATURES.map(({ icon: Icon, text }) => (
              <li key={text} className="auth-feature-item">
                <div className="auth-feature-icon">
                  <Icon size={13} />
                </div>
                <span>{text}</span>
              </li>
            ))}
          </ul>

          {/* Stats row */}
          <div className="auth-stats">
            {STATS.map(({ val, lab }) => (
              <div key={lab} className="auth-stat">
                <p className="auth-stat-val">{val}</p>
                <p className="auth-stat-lab">{lab}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Testimonial */}
        <div className="auth-testimonial">
          <div className="auth-avatar-row">
            {['O', 'A', 'M'].map((l, i) => (
              <div key={i} className="auth-avatar" style={{ marginLeft: i ? '-8px' : 0 }}>
                {l}
              </div>
            ))}
            <span className="auth-avatar-text">Join 500+ teams</span>
          </div>
          <p className="auth-testimonial-quote">
            "Lead Gen AI 10x'd our reply rates in 3 weeks. The AI personalization is incredible."
          </p>
          <p className="auth-testimonial-author">— Sarah K., Head of Growth at Acme Corp</p>
        </div>
      </div>

      {/* ── Right panel — form ── */}
      <div className="auth-right">
        {/* Mobile logo */}
        <div className="auth-logo auth-logo-mobile">
          <div className="auth-logo-icon">
            <Zap size={18} className="text-white" />
          </div>
          <span className="auth-logo-text">Lead Gen AI</span>
        </div>

        <div className="auth-card animate-fade-up">
          <div className="auth-card-header">
            <h1 className="auth-card-title">Welcome back</h1>
            <p className="auth-card-subtitle">Sign in to your account to continue</p>
          </div>

          {error && (
            <div className="auth-error">
              <span>⚠</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            {/* Email */}
            <div className="auth-field">
              <label className="auth-label">Email address</label>
              <div className="auth-input-wrap">
                <Mail size={15} className="auth-input-icon" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  placeholder="you@company.com"
                  className="auth-input"
                />
              </div>
            </div>

            {/* Password */}
            <div className="auth-field">
              <div className="auth-label-row">
                <label className="auth-label">Password</label>
                <a href="#" className="auth-forgot">Forgot password?</a>
              </div>
              <PasswordInput
                id="login-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                dark
                autoComplete="current-password"
                placeholder="••••••••"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="auth-submit"
            >
              {loading ? (
                <svg className="auth-spinner" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
              ) : (
                <>Sign in <ArrowRight size={16} /></>
              )}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account?{' '}
            <Link to="/signup" className="auth-switch-link">Create one free</Link>
          </p>

          <div className="auth-security">
            <Shield size={12} />
            <span>256-bit encryption · SOC 2 compliant</span>
          </div>
        </div>
      </div>
    </div>
  )
}
