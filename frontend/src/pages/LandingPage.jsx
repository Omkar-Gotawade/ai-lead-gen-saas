import { Link } from 'react-router-dom'
import {
  Zap, ArrowRight, CheckCircle, Mail, TrendingUp,
  Shield, Users, Bot, BarChart3, Star, ChevronRight,
  Sparkles, Target, Clock
} from 'lucide-react'

const NAV_LINKS = ['Features', 'Pricing', 'Integrations', 'Docs']

const FEATURES = [
  {
    icon: Bot,
    color: '#f59e0b',
    bgColor: 'rgba(245,158,11,0.1)',
    borderColor: 'rgba(245,158,11,0.2)',
    title: 'AI-Powered Personalization',
    desc: 'Gemini AI crafts hyper-personalized emails using lead data — name, company, role, and more. Every email feels hand-written.',
  },
  {
    icon: Users,
    color: '#06b6d4',
    bgColor: 'rgba(6,182,212,0.1)',
    borderColor: 'rgba(6,182,212,0.2)',
    title: '50M+ Lead Database',
    desc: 'Discover verified B2B contacts instantly. Filter by role, industry, company size, location, and technology stack.',
  },
  {
    icon: Mail,
    color: '#10b981',
    bgColor: 'rgba(16,185,129,0.1)',
    borderColor: 'rgba(16,185,129,0.2)',
    title: 'Multi-Step Sequences',
    desc: 'Build automated follow-up sequences that run on autopilot. Set delays, conditions, and let AI handle the rest.',
  },
  {
    icon: BarChart3,
    color: '#f59e0b',
    bgColor: 'rgba(245,158,11,0.1)',
    borderColor: 'rgba(245,158,11,0.2)',
    title: 'Real-Time Analytics',
    desc: 'Track open rates, reply rates, and conversions with a live dashboard. Know exactly what is working.',
  },
  {
    icon: Shield,
    color: '#06b6d4',
    bgColor: 'rgba(6,182,212,0.1)',
    borderColor: 'rgba(6,182,212,0.2)',
    title: 'Deliverability Engine',
    desc: 'Built-in email warmup, health monitoring, and blacklist detection — your emails land in the inbox, not spam.',
  },
  {
    icon: TrendingUp,
    color: '#10b981',
    bgColor: 'rgba(16,185,129,0.1)',
    borderColor: 'rgba(16,185,129,0.2)',
    title: 'Smart Campaign Scheduling',
    desc: 'Send emails at optimal times based on timezone and behavior data. Maximize open rates automatically.',
  },
]

const TESTIMONIALS = [
  {
    name: 'Sarah K.',
    role: 'Head of Growth, Acme Corp',
    avatar: 'S',
    quote: "Lead Gen AI 10x'd our reply rates in 3 weeks. The AI personalization is incredible — clients think we wrote every email by hand.",
    stars: 5,
  },
  {
    name: 'James T.',
    role: 'VP Sales, Nexora',
    avatar: 'J',
    quote: 'Set up in 10 minutes, booked 5 meetings in the first week. This is the tool every B2B sales team needs.',
    stars: 5,
  },
  {
    name: 'Maria L.',
    role: 'Founder, GrowthLab',
    avatar: 'M',
    quote: "Finally an outreach tool that doesn't require a PhD to set up. Clean, fast, and the AI actually works.",
    stars: 5,
  },
]

const PLANS = [
  {
    name: 'Starter',
    price: '$49',
    period: '/mo',
    desc: 'Perfect for individuals and small teams',
    features: ['500 emails/month', 'AI personalization', 'Basic analytics', '1 sending domain', 'Email support'],
    cta: 'Start free trial',
    popular: false,
  },
  {
    name: 'Growth',
    price: '$149',
    period: '/mo',
    desc: 'For growing sales teams',
    features: ['2,500 emails/month', 'AI personalization', 'Advanced analytics', '3 sending domains', 'Priority support', 'Team collaboration'],
    cta: 'Start free trial',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: '$499',
    period: '/mo',
    desc: 'Unlimited scale for large teams',
    features: ['10,000 emails/month', 'AI personalization', 'Custom analytics', 'Unlimited domains', 'Dedicated manager', 'API access', 'Custom integrations'],
    cta: 'Contact sales',
    popular: false,
  },
]

const STATS = [
  ['50M+', 'Verified B2B contacts'],
  ['10×', 'Faster than manual outreach'],
  ['99.9%', 'Email deliverability rate'],
  ['<5 min', 'Average setup time'],
]

export default function LandingPage() {
  return (
    <div style={{ background: '#07080f', color: '#c8cce0', fontFamily: "'DM Sans', system-ui, sans-serif", minHeight: '100vh' }}>

      {/* ── Navbar ── */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 50,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 2rem', height: '64px',
        background: 'rgba(7,8,15,0.88)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <div style={{
            width: 34, height: 34, borderRadius: 9,
            background: 'linear-gradient(135deg,#d97706,#f59e0b)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 0 2px rgba(245,158,11,0.25), 0 4px 12px rgba(217,119,6,0.35)',
          }}>
            <Zap size={16} color="#07080f" />
          </div>
          <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.01em', color: '#fff' }}>Lead Gen AI</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }} className="hidden md:flex">
          {NAV_LINKS.map((l) => (
            <a key={l} href={`#${l.toLowerCase()}`}
              style={{ fontSize: '0.875rem', color: '#4a5168', textDecoration: 'none', transition: 'color 0.15s' }}
              onMouseEnter={e => e.target.style.color = '#e8eaf5'}
              onMouseLeave={e => e.target.style.color = '#4a5168'}
            >{l}</a>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Link to="/login" style={{
            fontSize: '0.84rem', color: '#6b7290', textDecoration: 'none',
            padding: '0.45rem 1rem', borderRadius: 8, transition: 'color 0.15s',
          }}>Sign in</Link>
          <Link to="/signup" style={{
            fontSize: '0.84rem', fontWeight: 600, color: '#07080f', textDecoration: 'none',
            padding: '0.5rem 1.25rem',
            background: 'linear-gradient(135deg,#d97706,#f59e0b)',
            borderRadius: 8,
            boxShadow: '0 2px 10px rgba(217,119,6,0.4)',
            transition: 'opacity 0.15s, box-shadow 0.15s',
          }}
            onMouseEnter={e => { e.currentTarget.style.opacity = '0.9'; e.currentTarget.style.boxShadow = '0 4px 18px rgba(217,119,6,0.55)'; }}
            onMouseLeave={e => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.boxShadow = '0 2px 10px rgba(217,119,6,0.4)'; }}
          >Get started free</Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section style={{ position: 'relative', overflow: 'hidden', padding: '6rem 2rem 7rem', textAlign: 'center' }}>
        {/* Background orbs */}
        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
          <div style={{ position: 'absolute', width: 700, height: 700, top: -300, left: '50%', transform: 'translateX(-50%)', borderRadius: '50%', background: 'radial-gradient(circle, rgba(217,119,6,0.18) 0%, transparent 70%)', filter: 'blur(70px)' }} />
          <div style={{ position: 'absolute', width: 400, height: 400, bottom: -100, left: '10%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%)', filter: 'blur(60px)' }} />
          <div style={{ position: 'absolute', width: 300, height: 300, bottom: 0, right: '10%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(245,158,11,0.1) 0%, transparent 70%)', filter: 'blur(60px)' }} />
          {/* Grid */}
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />
        </div>

        <div style={{ position: 'relative', maxWidth: 800, margin: '0 auto' }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '0.35rem 1rem',
            background: 'rgba(245,158,11,0.08)',
            border: '1px solid rgba(245,158,11,0.22)',
            borderRadius: 999, marginBottom: '2rem',
            fontSize: '0.72rem', fontWeight: 600, color: '#fcd34d',
            letterSpacing: '0.06em', textTransform: 'uppercase',
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#f59e0b', display: 'inline-block', boxShadow: '0 0 6px rgba(245,158,11,0.8)' }} />
            Now powered by Gemini AI
          </div>

          <h1 style={{
            fontFamily: 'Syne, system-ui, sans-serif',
            fontSize: 'clamp(2.5rem, 6vw, 4.75rem)',
            fontWeight: 800, lineHeight: 1.06,
            letterSpacing: '-0.04em', margin: '0 0 1.5rem',
            color: '#f0f2ff',
          }}>
            The AI outreach engine<br />
            <span style={{ background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 40%, #06b6d4 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              that closes deals for you
            </span>
          </h1>

          <p style={{ fontSize: '1.1rem', color: '#4a5168', lineHeight: 1.7, margin: '0 auto 2.5rem', maxWidth: 560 }}>
            Discover leads, craft AI-personalized emails, and automate follow-ups at scale. Built for B2B sales teams that want more meetings, less manual work.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <Link to="/signup" style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '0.9rem 2.25rem',
              background: 'linear-gradient(135deg,#d97706,#f59e0b)',
              color: '#07080f', textDecoration: 'none',
              fontWeight: 700, fontSize: '1rem',
              borderRadius: 12,
              boxShadow: '0 8px 28px rgba(217,119,6,0.45)',
              transition: 'transform 0.15s, box-shadow 0.15s',
            }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 12px 36px rgba(217,119,6,0.6)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 8px 28px rgba(217,119,6,0.45)'; }}
            >
              Start for free <ArrowRight size={18} />
            </Link>
            <a href="#features" style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '0.9rem 1.75rem',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#6b7290', textDecoration: 'none',
              fontWeight: 600, fontSize: '0.9rem',
              borderRadius: 12, transition: 'border-color 0.15s, color 0.15s',
            }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(245,158,11,0.3)'; e.currentTarget.style.color = '#e8eaf5'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; e.currentTarget.style.color = '#6b7290'; }}
            >
              See how it works <ChevronRight size={16} />
            </a>
          </div>

          <p style={{ fontSize: '0.76rem', color: '#252840', marginTop: '1rem' }}>
            No credit card required · 14-day free trial · Cancel anytime
          </p>

          {/* Social proof avatars */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginTop: '3rem' }}>
            <div style={{ display: 'flex' }}>
              {['S', 'J', 'M', 'R', 'A'].map((l, i) => (
                <div key={i} style={{
                  width: 32, height: 32, borderRadius: '50%',
                  background: i % 2 === 0
                    ? `linear-gradient(135deg, #d97706, #f59e0b)`
                    : `linear-gradient(135deg, #0891b2, #06b6d4)`,
                  border: '2px solid #07080f',
                  marginLeft: i ? -10 : 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.65rem', fontWeight: 700, color: '#07080f',
                }}>
                  {l}
                </div>
              ))}
            </div>
            <span style={{ fontSize: '0.82rem', color: '#4a5168' }}>
              <strong style={{ color: '#e8eaf5' }}>500+</strong> teams growing with Lead Gen AI
            </span>
          </div>
        </div>
      </section>

      {/* ── Stats bar ── */}
      <section style={{
        borderTop: '1px solid rgba(255,255,255,0.04)',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        padding: '2.5rem 2rem',
        background: 'rgba(255,255,255,0.015)',
      }}>
        <div style={{ maxWidth: 900, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem', textAlign: 'center' }}>
          {STATS.map(([val, lab]) => (
            <div key={lab}>
              <p style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '2.1rem', fontWeight: 500,
                letterSpacing: '-0.04em', color: '#f59e0b', margin: 0,
              }}>{val}</p>
              <p style={{ fontSize: '0.78rem', color: '#343a52', margin: '0.3rem 0 0' }}>{lab}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" style={{ padding: '6rem 2rem', maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <p style={{ fontSize: '0.72rem', fontWeight: 600, color: '#d97706', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>Everything you need</p>
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(1.75rem, 4vw, 2.75rem)', fontWeight: 800, letterSpacing: '-0.03em', margin: '0 0 1rem', color: '#f0f2ff' }}>
            Built to replace your entire<br />outreach stack
          </h2>
          <p style={{ color: '#4a5168', maxWidth: 500, margin: '0 auto', lineHeight: 1.7 }}>
            One platform for lead discovery, AI email writing, campaign automation, and deliverability monitoring.
          </p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
          {FEATURES.map(({ icon: Icon, color, bgColor, borderColor, title, desc }) => (
            <div key={title} style={{
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: 16, padding: '1.75rem',
              transition: 'background 0.2s, border-color 0.2s, transform 0.2s',
              cursor: 'default',
              position: 'relative',
              overflow: 'hidden',
            }}
              onMouseEnter={e => { e.currentTarget.style.background = bgColor; e.currentTarget.style.borderColor = borderColor; e.currentTarget.style.transform = 'translateY(-3px)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.02)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{
                width: 44, height: 44, borderRadius: 12, marginBottom: '1.25rem',
                background: bgColor, border: `1px solid ${borderColor}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon size={20} color={color} />
              </div>
              <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, margin: '0 0 0.5rem', color: '#f0f2ff' }}>{title}</h3>
              <p style={{ fontSize: '0.875rem', color: '#4a5168', lineHeight: 1.7, margin: 0 }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Testimonials ── */}
      <section style={{ padding: '6rem 2rem', background: 'rgba(255,255,255,0.01)', borderTop: '1px solid rgba(255,255,255,0.04)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <p style={{ fontSize: '0.72rem', fontWeight: 600, color: '#d97706', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>Wall of love</p>
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(1.5rem, 3vw, 2.25rem)', fontWeight: 800, letterSpacing: '-0.03em', margin: 0, color: '#f0f2ff' }}>
              Teams love Lead Gen AI
            </h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
            {TESTIMONIALS.map(({ name, role, avatar, quote, stars }) => (
              <div key={name} style={{
                background: 'rgba(255,255,255,0.025)',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: 16, padding: '1.75rem',
                transition: 'border-color 0.2s',
              }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(245,158,11,0.2)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'}
              >
                <div style={{ display: 'flex', gap: 2, marginBottom: '1rem' }}>
                  {Array(stars).fill(0).map((_, i) => <Star key={i} size={14} fill="#f59e0b" color="#f59e0b" />)}
                </div>
                <p style={{ fontSize: '0.9rem', color: '#6b7290', lineHeight: 1.75, margin: '0 0 1.25rem', fontStyle: 'italic' }}>"{quote}"</p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'linear-gradient(135deg,#d97706,#f59e0b)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700, color: '#07080f' }}>{avatar}</div>
                  <div>
                    <p style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.84rem', fontWeight: 700, color: '#e8eaf5', margin: 0 }}>{name}</p>
                    <p style={{ fontSize: '0.74rem', color: '#343a52', margin: 0 }}>{role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Pricing ── */}
      <section id="pricing" style={{ padding: '6rem 2rem', maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <p style={{ fontSize: '0.72rem', fontWeight: 600, color: '#d97706', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>Simple pricing</p>
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(1.5rem, 3vw, 2.25rem)', fontWeight: 800, letterSpacing: '-0.03em', margin: '0 0 0.75rem', color: '#f0f2ff' }}>
            Start free, scale as you grow
          </h2>
          <p style={{ color: '#4a5168', margin: 0 }}>All plans include a 14-day free trial. No credit card required.</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', alignItems: 'start' }}>
          {PLANS.map(({ name, price, period, desc, features, cta, popular }) => (
            <div key={name} style={{
              background: popular ? 'rgba(245,158,11,0.06)' : 'rgba(255,255,255,0.025)',
              border: popular ? '1px solid rgba(245,158,11,0.35)' : '1px solid rgba(255,255,255,0.06)',
              borderRadius: 18, padding: '2rem',
              position: 'relative',
              boxShadow: popular ? '0 0 40px rgba(245,158,11,0.1), inset 0 1px 0 rgba(245,158,11,0.15)' : 'none',
            }}>
              {popular && (
                <div style={{
                  position: 'absolute', top: -14, left: '50%', transform: 'translateX(-50%)',
                  background: 'linear-gradient(135deg,#d97706,#f59e0b)',
                  color: '#07080f', fontSize: '0.68rem', fontWeight: 700,
                  padding: '0.3rem 1rem', borderRadius: 999,
                  letterSpacing: '0.06em', textTransform: 'uppercase',
                  whiteSpace: 'nowrap',
                  fontFamily: 'Syne, sans-serif',
                }}>Most popular</div>
              )}
              <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.1rem', fontWeight: 700, margin: '0 0 0.25rem', color: '#f0f2ff' }}>{name}</h3>
              <p style={{ fontSize: '0.8rem', color: '#343a52', margin: '0 0 1.25rem' }}>{desc}</p>
              <div style={{ marginBottom: '1.5rem' }}>
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '2.5rem', fontWeight: 500, letterSpacing: '-0.04em', color: popular ? '#f59e0b' : '#f0f2ff' }}>{price}</span>
                <span style={{ fontSize: '0.85rem', color: '#343a52' }}>{period}</span>
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.75rem', display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                {features.map((f) => (
                  <li key={f} style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', fontSize: '0.875rem', color: '#6b7290' }}>
                    <CheckCircle size={15} color={popular ? '#f59e0b' : '#10b981'} style={{ flexShrink: 0 }} />{f}
                  </li>
                ))}
              </ul>
              <Link to="/signup" style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                width: '100%', padding: '0.8rem',
                background: popular ? 'linear-gradient(135deg,#d97706,#f59e0b)' : 'rgba(255,255,255,0.05)',
                border: popular ? 'none' : '1px solid rgba(255,255,255,0.09)',
                color: popular ? '#07080f' : '#e8eaf5', textDecoration: 'none',
                fontWeight: 700, fontSize: '0.875rem',
                borderRadius: 10,
                boxShadow: popular ? '0 4px 16px rgba(217,119,6,0.4)' : 'none',
                transition: 'opacity 0.15s',
              }}
                onMouseEnter={e => e.currentTarget.style.opacity = '0.88'}
                onMouseLeave={e => e.currentTarget.style.opacity = '1'}
              >
                {cta} <ArrowRight size={15} />
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section style={{ padding: '4rem 2rem', textAlign: 'center' }}>
        <div style={{
          maxWidth: 720, margin: '0 auto',
          background: 'linear-gradient(135deg, rgba(245,158,11,0.1) 0%, rgba(6,182,212,0.06) 100%)',
          border: '1px solid rgba(245,158,11,0.22)',
          borderRadius: 24, padding: '3.5rem 2rem',
          position: 'relative', overflow: 'hidden',
          boxShadow: '0 0 60px rgba(245,158,11,0.06)',
        }}>
          <div style={{ position: 'absolute', top: 0, left: '10%', right: '10%', height: '1px', background: 'linear-gradient(90deg, transparent, #f59e0b, transparent)' }} />
          <div style={{ position: 'absolute', top: -80, right: -80, width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(circle, rgba(245,158,11,0.2), transparent 70%)', filter: 'blur(40px)' }} />
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(1.5rem, 4vw, 2.5rem)', fontWeight: 900, letterSpacing: '-0.03em', margin: '0 0 1rem', position: 'relative', color: '#f0f2ff' }}>
            Ready to 10× your outreach?
          </h2>
          <p style={{ color: '#4a5168', marginBottom: '2rem', lineHeight: 1.7, position: 'relative' }}>
            Join 500+ B2B teams already using Lead Gen AI to book more meetings, faster.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', position: 'relative' }}>
            <Link to="/signup" style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '0.9rem 2.25rem',
              background: 'linear-gradient(135deg,#d97706,#f59e0b)',
              color: '#07080f', textDecoration: 'none',
              fontWeight: 700, fontSize: '1rem', borderRadius: 12,
              boxShadow: '0 8px 28px rgba(217,119,6,0.5)',
            }}>
              Get started free <ArrowRight size={18} />
            </Link>
            <Link to="/login" style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '0.9rem 1.75rem',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#6b7290', textDecoration: 'none',
              fontWeight: 600, fontSize: '0.9rem', borderRadius: 12,
            }}>
              Sign in →
            </Link>
          </div>
          <p style={{ fontSize: '0.75rem', color: '#1e2130', marginTop: '1rem' }}>No credit card · 14-day trial · Cancel anytime</p>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{ borderTop: '1px solid rgba(255,255,255,0.04)', padding: '2.5rem 2rem' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <div style={{ width: 28, height: 28, borderRadius: 8, background: 'linear-gradient(135deg,#d97706,#f59e0b)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Zap size={13} color="#07080f" />
            </div>
            <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.9rem', color: '#f0f2ff' }}>Lead Gen AI</span>
          </div>
          <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            {['Privacy', 'Terms', 'Support', 'Status'].map(link => (
              <a key={link} href="#" style={{ fontSize: '0.8rem', color: '#252840', textDecoration: 'none', transition: 'color 0.15s' }}
                onMouseEnter={e => e.target.style.color = '#6b7290'}
                onMouseLeave={e => e.target.style.color = '#252840'}
              >{link}</a>
            ))}
          </div>
          <p style={{ fontSize: '0.78rem', color: '#1a1c26', margin: 0 }}>© 2025 Lead Gen AI. All rights reserved.</p>
        </div>
      </footer>

    </div>
  )
}
