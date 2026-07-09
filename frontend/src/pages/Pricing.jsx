import React from 'react'
import { Check, X, Info, DollarSign, Zap, ChevronDown } from 'lucide-react'
import { Card, CardContent } from '../components/ui/Card'
import { Alert, AlertDescription } from '../components/ui/Alert'
import Button from '../components/ui/Button'

const PLANS = [
  {
    name: 'Starter',
    price: '$49',
    period: '/month',
    description: 'Perfect for testing and small campaigns',
    badge: 'ALPHA PRICING',
    features: [
      { name: '500 emails/month', included: true },
      { name: '1 sending domain', included: true },
      { name: 'AI email generation', included: true },
      { name: 'Basic deliverability monitoring', included: true },
      { name: 'CSV lead import', included: true },
      { name: 'Email support', included: true },
      { name: 'Multi-user teams', included: false },
      { name: 'Advanced analytics', included: false },
      { name: 'API access', included: false },
    ],
    cta: 'Current Plan',
    current: true,
  },
  {
    name: 'Growth',
    price: '$149',
    period: '/month',
    description: 'Scale your outreach safely',
    badge: 'MOST POPULAR',
    popular: true,
    features: [
      { name: '2,500 emails/month', included: true },
      { name: '3 sending domains', included: true },
      { name: 'AI email generation', included: true },
      { name: 'Advanced deliverability monitoring', included: true },
      { name: 'CSV lead import', included: true },
      { name: 'Priority email support', included: true },
      { name: 'Multi-user teams (3 seats)', included: true },
      { name: 'Advanced analytics', included: true },
      { name: 'API access', included: false },
    ],
    cta: 'Coming Soon',
  },
  {
    name: 'Enterprise',
    price: '$499',
    period: '/month',
    description: 'For high-volume sending teams',
    badge: 'BEST VALUE',
    features: [
      { name: '10,000 emails/month', included: true },
      { name: 'Unlimited sending domains', included: true },
      { name: 'AI email generation', included: true },
      { name: 'Advanced deliverability monitoring', included: true },
      { name: 'CSV lead import', included: true },
      { name: 'Priority phone & email support', included: true },
      { name: 'Multi-user teams (unlimited)', included: true },
      { name: 'Advanced analytics', included: true },
      { name: 'API access', included: true },
      { name: 'Custom integrations', included: true },
      { name: 'Dedicated account manager', included: true },
    ],
    cta: 'Contact Us',
  },
]

const FAQS = [
  {
    q: 'When will billing be activated?',
    a: 'Billing will be enabled when we move from alpha to beta. All alpha testers will receive at least 30 days notice and special early-adopter pricing.',
  },
  {
    q: 'What happens if I exceed my email limit?',
    a: "We'll send you a warning at 80% usage. If you exceed your limit, you can either upgrade your plan or wait until next month. We'll never auto-charge you.",
  },
  {
    q: 'Can I cancel anytime?',
    a: "Yes, absolutely. You can cancel at any time and you'll retain access until the end of your billing period. No long-term commitments required.",
  },
  {
    q: 'Do you offer refunds?',
    a: "Yes, we offer a 14-day money-back guarantee. If you're not satisfied, contact us within 14 days of purchase for a full refund.",
  },
  {
    q: "What's included in email support?",
    a: 'All plans include email support with response within 24 business hours. Growth and Enterprise plans get priority support with faster response times.',
  },
]

function FAQItem({ q, a }) {
  const [open, setOpen] = React.useState(false)
  return (
    <div
      style={{ background: '#111220', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14 }}
      className="cursor-pointer transition-all duration-200"
      onClick={() => setOpen((o) => !o)}
      onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(245,158,11,0.2)'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'}
    >
      <div className="flex items-center justify-between gap-4 p-5">
        <h3 className="font-semibold text-sm" style={{ color: '#e8eaf5' }}>{q}</h3>
        <ChevronDown
          className={`shrink-0 w-4 h-4 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          style={{ color: '#343a52' }}
        />
      </div>
      {open && (
        <div className="px-5 pb-5 animate-fade-up">
          <p className="text-sm leading-relaxed" style={{ color: '#4a5168' }}>{a}</p>
        </div>
      )}
    </div>
  )
}

export default function Pricing() {
  return (
    <div className="p-6 space-y-10 max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="flex items-center justify-center gap-2 mb-1">
          <DollarSign className="w-5 h-5" style={{ color: '#f59e0b' }} />
          <h1 className="page-title">Simple, Transparent Pricing</h1>
        </div>
        <p className="page-subtitle">
          Choose the plan that fits your needs. Upgrade or downgrade anytime.
        </p>

        <Alert variant="warning" className="max-w-3xl mx-auto text-left">
          <AlertDescription>
            <strong>⚠️ Alpha Pricing Notice:</strong> Billing is not active during alpha phase.
            These prices are for evaluation purposes only and subject to change before public launch.
            All alpha users will receive special early-adopter pricing when billing goes live.
          </AlertDescription>
        </Alert>
      </div>

      {/* Pricing cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {PLANS.map((plan, idx) => (
          <div
            key={idx}
            className="relative flex flex-col rounded-2xl transition-all duration-200 hover:-translate-y-1"
            style={{
              background: plan.popular ? 'rgba(245,158,11,0.06)' : '#111220',
              border: plan.popular ? '1px solid rgba(245,158,11,0.35)' : '1px solid rgba(255,255,255,0.06)',
              boxShadow: plan.popular ? '0 0 40px rgba(245,158,11,0.1), inset 0 1px 0 rgba(245,158,11,0.15)' : 'none',
            }}
          >
            {/* Popular top edge */}
            {plan.popular && (
              <div style={{ position: 'absolute', top: 0, left: '10%', right: '10%', height: '1px', background: 'linear-gradient(90deg, transparent, #f59e0b, transparent)' }} />
            )}

            {plan.badge && (
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                <span
                  className="px-3 py-1 text-[10px] font-bold tracking-widest uppercase rounded-full whitespace-nowrap"
                  style={plan.popular
                    ? { background: 'linear-gradient(135deg,#d97706,#f59e0b)', color: '#07080f' }
                    : { background: 'rgba(255,255,255,0.06)', color: '#4a5168', border: '1px solid rgba(255,255,255,0.08)' }
                  }
                >
                  {plan.badge}
                </span>
              </div>
            )}

            <div className="text-center pt-10 pb-4 px-6">
              <h2 className="text-xl font-bold mb-1" style={{ fontFamily: 'Syne, sans-serif', color: '#f0f2ff' }}>{plan.name}</h2>
              <div className="mb-2">
                <span
                  className="text-4xl font-medium"
                  style={{ fontFamily: 'JetBrains Mono, monospace', letterSpacing: '-0.04em', color: plan.popular ? '#f59e0b' : '#e8eaf5' }}
                >
                  {plan.price}
                </span>
                <span className="text-sm ml-1" style={{ color: '#343a52' }}>{plan.period}</span>
              </div>
              <p className="text-sm" style={{ color: '#343a52' }}>{plan.description}</p>
            </div>

            <div className="flex-1 px-6 pb-6 flex flex-col">
              <ul className="space-y-2.5 mb-6 flex-1">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2">
                    {feature.included ? (
                      <Check className="w-4 h-4 shrink-0 mt-0.5" style={{ color: plan.popular ? '#f59e0b' : '#10b981' }} />
                    ) : (
                      <X className="w-4 h-4 shrink-0 mt-0.5" style={{ color: '#252840' }} />
                    )}
                    <span className="text-sm" style={{ color: feature.included ? '#6b7290' : '#252840' }}>
                      {feature.name}
                    </span>
                  </li>
                ))}
              </ul>

              <Button
                className="w-full"
                variant={plan.current ? 'secondary' : plan.popular ? 'primary' : 'outline'}
                disabled
              >
                {plan.cta}
              </Button>

              {!plan.current && (
                <p className="text-xs text-center mt-2" style={{ color: '#252840' }}>
                  Available after alpha phase
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* FAQ */}
      <div className="max-w-3xl mx-auto space-y-4">
        <h2 className="text-lg font-bold text-center" style={{ fontFamily: 'Syne, sans-serif', color: '#f0f2ff' }}>
          Frequently Asked Questions
        </h2>
        <div className="space-y-2.5">
          {FAQS.map((faq, i) => (
            <FAQItem key={i} q={faq.q} a={faq.a} />
          ))}
        </div>
      </div>

      {/* Trust banner */}
      <div className="max-w-3xl mx-auto">
        <div
          className="rounded-2xl px-6 py-6 text-center"
          style={{
            background: 'linear-gradient(135deg, rgba(245,158,11,0.08) 0%, rgba(6,182,212,0.04) 100%)',
            border: '1px solid rgba(245,158,11,0.2)',
            boxShadow: '0 0 40px rgba(245,158,11,0.05)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div style={{ position: 'absolute', top: 0, left: '10%', right: '10%', height: '1px', background: 'linear-gradient(90deg, transparent, #f59e0b, transparent)' }} />
          <div className="flex items-center justify-center gap-2 mb-2">
            <Zap className="w-5 h-5" style={{ color: '#f59e0b' }} />
            <h3 className="text-base font-bold" style={{ fontFamily: 'Syne, sans-serif', color: '#f0f2ff' }}>🎁 Alpha Tester Benefit</h3>
          </div>
          <p className="text-sm" style={{ color: '#4a5168' }}>
            As an alpha tester, you'll receive a{' '}
            <strong style={{ color: '#f59e0b' }}>lifetime 30% discount</strong> on any paid plan when
            billing launches. Your feedback helps us build a better product!
          </p>
        </div>
      </div>
    </div>
  )
}
