import React from 'react'
import { Check, X, Info, DollarSign, Zap } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Alert, AlertDescription } from '../components/ui/Alert'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

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
    <Card
      className="cursor-pointer hover:shadow-card transition-shadow"
      onClick={() => setOpen((o) => !o)}
    >
      <CardContent className="pt-5 pb-5">
        <div className="flex items-center justify-between gap-4">
          <h3 className="font-semibold text-ink-800 text-sm">{q}</h3>
          <span className={`shrink-0 text-ink-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}>
            ▾
          </span>
        </div>
        {open && (
          <p className="text-ink-500 text-sm mt-3 animate-fade-up">{a}</p>
        )}
      </CardContent>
    </Card>
  )
}

export default function Pricing() {
  return (
    <div className="p-6 space-y-10 max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="flex items-center justify-center gap-2 mb-1">
          <DollarSign className="w-5 h-5 text-brand-600" />
          <h1 className="page-title">Simple, Transparent Pricing</h1>
        </div>
        <p className="page-subtitle">
          Choose the plan that fits your needs. Upgrade or downgrade anytime.
        </p>

        <Alert variant="warning" className="max-w-3xl mx-auto text-left">
          <Info className="h-4 w-4" />
          <AlertDescription>
            <strong>⚠️ Alpha Pricing Notice:</strong> Billing is not active during alpha phase.
            These prices are for evaluation purposes only and subject to change before public launch.
            All alpha users will receive special early-adopter pricing when billing goes live.
          </AlertDescription>
        </Alert>
      </div>

      {/* Pricing cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {PLANS.map((plan, idx) => (
          <div
            key={idx}
            className={[
              'relative flex flex-col rounded-2xl border transition-all duration-200',
              'hover:-translate-y-1',
              plan.popular
                ? 'border-2 border-brand-500 shadow-card-lg bg-gradient-to-b from-brand-50/40 to-white hover:shadow-[0_20px_60px_-15px_rgba(124,58,237,0.25)]'
                : 'border-ink-100 bg-white shadow-card hover:shadow-card-lg',
            ].join(' ')}
          >
            {plan.badge && (
              <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                <Badge
                  variant={plan.popular ? 'brand' : 'default'}
                  className="px-4 py-1 text-xs tracking-wide"
                >
                  {plan.badge}
                </Badge>
              </div>
            )}

            <div className="text-center pt-10 pb-4 px-6">
              <h2 className="text-xl font-bold text-ink-900 mb-1">{plan.name}</h2>
              <div className="mb-2">
                <span className="text-4xl font-extrabold text-ink-900">{plan.price}</span>
                <span className="text-ink-400 text-sm">{plan.period}</span>
              </div>
              <p className="text-sm text-ink-500">{plan.description}</p>
            </div>

            <div className="flex-1 px-6 pb-6 flex flex-col">
              <ul className="space-y-2.5 mb-6 flex-1">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2">
                    {feature.included ? (
                      <Check className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
                    ) : (
                      <X className="w-4 h-4 text-ink-200 shrink-0 mt-0.5" />
                    )}
                    <span
                      className={`text-sm ${
                        feature.included ? 'text-ink-700' : 'text-ink-300'
                      }`}
                    >
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
                <p className="text-xs text-center text-ink-400 mt-2">
                  Available after alpha phase
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* FAQ */}
      <div className="max-w-3xl mx-auto space-y-4">
        <h2 className="text-lg font-bold text-ink-900 text-center">
          Frequently Asked Questions
        </h2>
        <div className="space-y-3">
          {FAQS.map((faq, i) => (
            <FAQItem key={i} q={faq.q} a={faq.a} />
          ))}
        </div>
      </div>

      {/* Trust banner */}
      <div className="max-w-3xl mx-auto">
        <div className="bg-gradient-to-r from-brand-50 to-purple-50 border border-brand-100 rounded-2xl px-6 py-6 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Zap className="w-5 h-5 text-brand-600" />
            <h3 className="text-base font-bold text-ink-900">🎁 Alpha Tester Benefit</h3>
          </div>
          <p className="text-ink-700 text-sm">
            As an alpha tester, you'll receive a{' '}
            <strong className="text-brand-700">lifetime 30% discount</strong> on any paid plan when
            billing launches. Your feedback helps us build a better product!
          </p>
        </div>
      </div>
    </div>
  )
}
