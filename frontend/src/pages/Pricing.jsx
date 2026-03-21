import React from 'react'
import { Check, X, Info, DollarSign } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Alert, AlertDescription } from '../components/ui/Alert'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

export default function Pricing() {
  const plans = [
    {
      name: "Starter",
      price: "$49",
      period: "/month",
      description: "Perfect for testing and small campaigns",
      badge: "ALPHA PRICING",
      features: [
        { name: "500 emails/month", included: true },
        { name: "1 sending domain", included: true },
        { name: "AI email generation", included: true },
        { name: "Basic deliverability monitoring", included: true },
        { name: "CSV lead import", included: true },
        { name: "Email support", included: true },
        { name: "Multi-user teams", included: false },
        { name: "Advanced analytics", included: false },
        { name: "API access", included: false }
      ],
      cta: "Current Plan",
      current: true
    },
    {
      name: "Growth",
      price: "$149",
      period: "/month",
      description: "Scale your outreach safely",
      badge: "MOST POPULAR",
      popular: true,
      features: [
        { name: "2,500 emails/month", included: true },
        { name: "3 sending domains", included: true },
        { name: "AI email generation", included: true },
        { name: "Advanced deliverability monitoring", included: true },
        { name: "CSV lead import", included: true },
        { name: "Priority email support", included: true },
        { name: "Multi-user teams (3 seats)", included: true },
        { name: "Advanced analytics", included: true },
        { name: "API access", included: false }
      ],
      cta: "Coming Soon"
    },
    {
      name: "Enterprise",
      price: "$499",
      period: "/month",
      description: "For high-volume sending teams",
      badge: "BEST VALUE",
      features: [
        { name: "10,000 emails/month", included: true },
        { name: "Unlimited sending domains", included: true },
        { name: "AI email generation", included: true },
        { name: "Advanced deliverability monitoring", included: true },
        { name: "CSV lead import", included: true },
        { name: "Priority phone & email support", included: true },
        { name: "Multi-user teams (unlimited)", included: true },
        { name: "Advanced analytics", included: true },
        { name: "API access", included: true },
        { name: "Custom integrations", included: true },
        { name: "Dedicated account manager", included: true }
      ],
      cta: "Contact Us"
    }
  ]

  return (
    <div className="p-6 space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-3">
          <DollarSign className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">Simple, Transparent Pricing</h1>
        </div>
        <p className="page-subtitle mb-6">
          Choose the plan that fits your needs. Upgrade or downgrade anytime.
        </p>
        
        {/* Alpha Warning */}
        <Alert variant="warning" className="max-w-3xl mx-auto">
          <Info className="h-4 w-4" />
          <AlertDescription className="text-left">
            <strong>⚠️ Alpha Pricing Notice:</strong> Billing is not active during alpha phase. 
            These prices are for evaluation purposes only and subject to change before public launch.
            All alpha users will receive special early-adopter pricing when billing goes live.
          </AlertDescription>
        </Alert>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan, idx) => (
          <Card 
            key={idx}
            className={`relative flex flex-col ${plan.popular ? 'border-2 border-brand-600 shadow-card-lg' : ''}`}
          >
            {plan.badge && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <Badge variant={plan.popular ? "brand" : "default"} className="px-4 py-1">
                  {plan.badge}
                </Badge>
              </div>
            )}
            
            <CardHeader className="text-center pt-8">
              <CardTitle className="text-2xl mb-2">{plan.name}</CardTitle>
              <div className="mb-4">
                <span className="text-4xl font-bold text-ink-900">{plan.price}</span>
                <span className="text-ink-500">{plan.period}</span>
              </div>
              <p className="text-sm text-ink-500">{plan.description}</p>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col">
              <ul className="space-y-3 mb-6 flex-1">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2">
                    {feature.included ? (
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    ) : (
                      <X className="w-5 h-5 text-ink-300 flex-shrink-0 mt-0.5" />
                    )}
                    <span className={feature.included ? 'text-ink-700' : 'text-ink-300'}>
                      {feature.name}
                    </span>
                  </li>
                ))}
              </ul>

              <Button 
                className="w-full" 
                variant={plan.current ? "secondary" : plan.popular ? "primary" : "outline"}
                disabled={true}
              >
                {plan.cta}
              </Button>
              
              {!plan.current && (
                <p className="text-xs text-center text-ink-400 mt-2">
                  Available after alpha phase
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* FAQ Section */}
      <div className="max-w-3xl mx-auto">
        <h2 className="text-xl font-bold text-ink-900 mb-6 text-center">
          Frequently Asked Questions
        </h2>
        
        <div className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-ink-800 mb-2">
                When will billing be activated?
              </h3>
              <p className="text-ink-500 text-sm">
                Billing will be enabled when we move from alpha to beta. All alpha testers 
                will receive at least 30 days notice and special early-adopter pricing.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-ink-800 mb-2">
                What happens if I exceed my email limit?
              </h3>
              <p className="text-ink-500 text-sm">
                We'll send you a warning at 80% usage. If you exceed your limit, you can either 
                upgrade your plan or wait until next month. We'll never auto-charge you.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-ink-800 mb-2">
                Can I cancel anytime?
              </h3>
              <p className="text-ink-500 text-sm">
                Yes, absolutely. You can cancel at any time and you'll retain access until the 
                end of your billing period. No long-term commitments required.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-ink-800 mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-ink-500 text-sm">
                Yes, we offer a 14-day money-back guarantee. If you're not satisfied, 
                contact us within 14 days of purchase for a full refund.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-ink-800 mb-2">
                What's included in email support?
              </h3>
              <p className="text-ink-500 text-sm">
                All plans include email support with response within 24 business hours. 
                Growth and Enterprise plans get priority support with faster response times.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Trust Section */}
      <div className="mt-12 text-center">
        <Card className="bg-brand-50 border-brand-200">
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold text-ink-900 mb-2">
              🎁 Alpha Tester Benefit
            </h3>
            <p className="text-ink-700">
              As an alpha tester, you'll receive <strong>lifetime 30% discount</strong> on any paid plan 
              when billing launches. Your feedback helps us build a better product!
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
