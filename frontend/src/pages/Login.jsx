import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Mail, Zap, ArrowRight, CheckCircle } from 'lucide-react'
import PasswordInput from '../components/ui/PasswordInput'

const features = [
  'AI-powered lead discovery across 50M+ contacts',
  'Automated multi-step email campaigns',
  'Real-time analytics & deliverability monitoring',
  'Smart personalization with Gemini AI',
]

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

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
    <div className="min-h-screen flex bg-gradient-dark bg-gradient-mesh">
      {/* Ambient glow orbs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-brand-700/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -right-40 w-80 h-80 bg-brand-600/15 rounded-full blur-3xl" />
        <div className="absolute -bottom-20 left-1/3 w-72 h-72 bg-purple-700/10 rounded-full blur-3xl" />
      </div>

      {/* Left — feature panel */}
      <div className="hidden lg:flex flex-col justify-between w-[440px] shrink-0 px-12 py-14 border-r border-white/5">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-brand flex items-center justify-center shadow-glow-sm">
            <Zap className="w-4.5 h-4.5 text-white" style={{width:'18px',height:'18px'}} />
          </div>
          <span className="text-white font-bold text-lg tracking-tight">Lead Gen AI</span>
        </div>

        {/* Features */}
        <div className="space-y-8">
          <div>
            <h2 className="text-3xl font-bold text-white leading-tight mb-3">
              Grow your pipeline<br />with AI automation
            </h2>
            <p className="text-ink-400 text-sm leading-relaxed">
              The smartest outreach platform for B2B teams — discover, engage, and convert leads at scale.
            </p>
          </div>
          <ul className="space-y-3">
            {features.map((f, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <CheckCircle className="w-4 h-4 text-brand-400 shrink-0 mt-0.5" />
                <span className="text-ink-300 text-sm">{f}</span>
              </li>
            ))}
          </ul>
          {/* Social proof */}
          <div className="flex gap-4">
            {[['10x', 'Faster outreach'], ['50M+', 'Contacts indexed'], ['99.9%', 'Uptime SLA']].map(([val, lab]) => (
              <div key={lab} className="flex-1 bg-white/5 border border-white/8 rounded-xl px-3 py-3 text-center" style={{borderColor:'rgba(255,255,255,0.08)'}}>
                <p className="text-white font-bold text-lg">{val}</p>
                <p className="text-ink-500 text-[11px] mt-0.5">{lab}</p>
              </div>
            ))}
          </div>
        </div>

        <p className="text-ink-600 text-xs">© 2025 Lead Gen AI. All rights reserved.</p>
      </div>

      {/* Right — form panel */}
      <div className="flex-1 flex items-center justify-center px-4 py-12 sm:px-8">
        <div className="w-full max-w-sm animate-fade-up">
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2.5 mb-10 justify-center">
            <div className="w-9 h-9 rounded-xl bg-gradient-brand flex items-center justify-center shadow-glow-sm">
              <Zap style={{width:'18px',height:'18px'}} className="text-white" />
            </div>
            <span className="text-white font-bold text-lg">Lead Gen AI</span>
          </div>

          {/* Card */}
          <div className="glass-dark rounded-2xl px-8 py-8 shadow-card-lg border border-white/8" style={{borderColor:'rgba(255,255,255,0.08)'}}>
            <div className="mb-7">
              <h1 className="text-2xl font-bold text-white mb-1">Welcome back</h1>
              <p className="text-ink-400 text-sm">Sign in to your account to continue</p>
            </div>

            {error && (
              <div className="mb-5 flex items-start gap-2.5 bg-danger/10 border border-danger/25 text-red-300 rounded-lg px-3.5 py-3 text-sm animate-fade-up">
                <span className="shrink-0 mt-0.5">⚠</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label className="block text-xs font-medium text-ink-300 mb-1.5">
                  Email address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-500 pointer-events-none" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                    placeholder="you@company.com"
                    className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-3.5 py-2.5 text-sm text-white placeholder-ink-600
                               focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label htmlFor="login-password" className="text-xs font-medium text-ink-300">Password</label>
                  <a href="#" className="text-xs text-brand-400 hover:text-brand-300 transition-colors">
                    Forgot password?
                  </a>
                </div>
                <PasswordInput
                  id="login-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  dark
                  autoComplete="current-password"
                />
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 disabled:opacity-60
                           text-white font-semibold text-sm rounded-lg py-2.5 mt-2 transition-all duration-150 shadow-glow-sm
                           hover:shadow-glow focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 focus:ring-offset-[#0f1117]"
              >
                {loading ? (
                  <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                  </svg>
                ) : (
                  <>
                    Sign in
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-ink-500 text-sm">
                Don't have an account?{' '}
                <Link to="/signup" className="text-brand-400 hover:text-brand-300 font-medium transition-colors">
                  Create one free
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login

