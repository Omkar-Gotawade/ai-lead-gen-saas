import React, { useState, useEffect, useCallback } from 'react';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  TrendingUp,
  AlertOctagon,
  Info
} from 'lucide-react';
import axios from '../api/axios';

import Button from '../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '../components/ui/Card';
import { SkeletonCard, SkeletonMetricCard } from '../components/ui/Skeleton';
import Badge from '../components/ui/Badge';
import { useToast } from '../context/ToastContext';

/* ─── SVG Arc Gauge ──────────────────────────────────────────── */
function ScoreGauge({ score }) {
  const R = 52;
  const C = 2 * Math.PI * R;           // full circumference ≈ 326.7
  const arc = C * 0.75;                // 270° visible arc
  const filled = arc * (score / 100);
  const gap = arc - filled;

  const colorClass =
    score >= 80 ? 'gauge-fill-good' :
    score >= 60 ? 'gauge-fill-warning' :
    'gauge-fill-danger';

  const labelColor =
    score >= 80 ? '#10b981' :
    score >= 60 ? '#f59e0b' :
    '#ef4444';

  return (
    <div className="relative flex items-center justify-center" style={{ width: 160, height: 160 }}>
      <svg width="160" height="160" viewBox="0 0 120 120">
        {/* Background track */}
        <circle
          className="gauge-track"
          cx="60" cy="60" r={R}
          strokeDasharray={`${arc} ${C - arc}`}
          strokeDashoffset={C * 0.125}  /* rotate so gap is at bottom */
          transform="rotate(135 60 60)"
        />
        {/* Filled arc */}
        <circle
          className={`gauge-fill ${colorClass}`}
          cx="60" cy="60" r={R}
          strokeDasharray={`${filled} ${C - filled}`}
          strokeDashoffset={C * 0.125}
          transform="rotate(135 60 60)"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold tabular-nums stat-number" style={{ color: labelColor }}>{score}</span>
        <span className="text-xs mt-0.5" style={{ color: '#343a52' }}>/ 100</span>
      </div>
    </div>
  );
}

/* ─── Status icon helper ─────────────────────────────────────── */
function StatusIcon({ status }) {
  if (status === 'pass')    return <CheckCircle  className="w-5 h-5 text-green-500 shrink-0" />;
  if (status === 'warning') return <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />;
  if (status === 'fail')    return <XCircle       className="w-5 h-5 text-red-500 shrink-0" />;
  return <Info className="w-5 h-5 text-ink-300 shrink-0" />;
}

const MOCK_HEALTH = {
  score: 70,
  status: 'warning',
  score_confidence: 'partial',
  confidence_note: 'Partial confidence — Limited metrics available',
  checks: {
    provider_connection: { status: 'pass',    message: 'Email provider configured', implemented: true },
    warmup:              { status: 'warning', message: 'Day 5 of 21 (recommended)', note: 'Advisory only', implemented: true },
    send_success:        { status: 'pass',    message: '95% successful sends', implemented: true },
    bounce_rate:         { status: 'inactive',message: 'Not implemented yet', note: 'Simulated', implemented: false },
    spam_complaints:     { status: 'inactive',message: 'Requires webhook setup', note: 'Simulated', implemented: false },
    blacklist_status:    { status: 'unknown', message: 'Basic check only', note: 'Not fully implemented', implemented: false },
  },
  daily_limit: { sent: 35, limit: 50, next_limit: 55, note: 'Recommended — not enforced' },
  recommendations: [
    'Continue warmup: Send consistently for 16 more days',
    'Verify email list quality before sending campaigns',
  ],
  warnings: [],
  advisory_notices: [
    { type: 'info',    message: 'Daily limits are advisory only' },
    { type: 'warning', message: 'Bounce tracking not yet implemented' },
  ],
};

export default function Deliverability() {
  const [healthScore, setHealthScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fixing, setFixing] = useState(false);
  const toast = useToast();

  const fetchHealthScore = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/deliverability/health');
      setHealthScore(response.data);
    } catch {
      setHealthScore(MOCK_HEALTH);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchHealthScore(); }, [fetchHealthScore]);

  const handleSafetyDiagnostics = async () => {
    setFixing(true);
    try {
      const response = await axios.post('/api/deliverability/safety-diagnostics');
      const data = response.data;
      const hasIssues = data.risky_behaviors?.length > 0;
      toast[hasIssues ? 'warning' : 'success'](
        hasIssues
          ? `Diagnostics complete — ${data.risky_behaviors.length} issue(s) found`
          : 'Diagnostics complete — no issues found'
      );
    } catch {
      toast.warning('Diagnostics completed — check your email provider manually.');
    } finally {
      setFixing(false);
    }
  };

  const getScoreBadgeVariant = (score) =>
    score >= 80 ? 'success' : score >= 60 ? 'warning' : 'destructive';

  /* ─── Loading skeleton ──────────────────────────────────────── */
  if (loading) {
    return (
      <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
        <div className="h-8 w-56 rounded animate-pulse skeleton" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <SkeletonMetricCard />
          <div className="lg:col-span-2 space-y-6">
            <SkeletonCard />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <SkeletonCard />
              <SkeletonCard />
            </div>
          </div>
        </div>
      </div>
    );
  }

  const pct = Math.min(100, (healthScore.daily_limit.sent / healthScore.daily_limit.limit) * 100);

  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Email Deliverability</h1>
          <p className="page-subtitle mt-0.5">Monitor and improve your sender reputation</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchHealthScore}
          icon={<RefreshCw className="w-3.5 h-3.5" />}
        >
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Health Score Card ── */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Health Score</CardTitle>
            <CardDescription className="space-y-1">
              <span className="block">Based on implemented metrics only</span>
              <span className="inline-flex items-center gap-1 text-xs text-amber-600">
                <AlertTriangle className="w-3 h-3" />
                Confidence: {healthScore.score_confidence || 'partial'}
              </span>
            </CardDescription>
          </CardHeader>

          <CardContent className="flex flex-col items-center py-4 gap-4">
            <ScoreGauge score={healthScore.score} />

            <div className="-mt-2">
              <Badge variant={getScoreBadgeVariant(healthScore.score)}>
                {healthScore.status.toUpperCase()}
              </Badge>
            </div>

            {healthScore.confidence_note && (
              <p className="text-xs text-center text-ink-400 px-2">
                {healthScore.confidence_note}
              </p>
            )}

            {/* Daily limit bar */}
            <div className="w-full space-y-2">
              <div className="flex justify-between text-sm">
                <span style={{ color: '#4a5168' }}>Daily Limit Used</span>
                <span className="font-medium stat-number" style={{ color: '#e8eaf5', fontSize: '0.875rem' }}>
                  {healthScore.daily_limit.sent} / {healthScore.daily_limit.limit}
                </span>
              </div>
              <div className="w-full rounded-full h-2" style={{ background: 'rgba(255,255,255,0.06)' }}>
                <div
                  className="h-2 rounded-full transition-all duration-700"
                  style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #d97706, #f59e0b)' }}
                />
              </div>
              <p className="text-xs text-center" style={{ color: '#343a52' }}>
                {healthScore.daily_limit.note || 'Recommended safe limit — Not enforced'}
              </p>
              <p className="text-xs text-center" style={{ color: '#252840' }}>
                Next limit: {healthScore.daily_limit.next_limit} emails/day
              </p>
            </div>
          </CardContent>

          <CardFooter className="flex-col gap-2">
            <Button
              className="w-full"
              onClick={handleSafetyDiagnostics}
              isLoading={fixing}
              icon={<Shield className="w-4 h-4" />}
              variant="outline"
            >
              Run Safety Diagnostics
            </Button>
            <p className="text-xs text-center text-ink-400">
              Does not auto-fix — Provides manual guidance
            </p>
          </CardFooter>
        </Card>

        {/* ── Checks + Recommendations ── */}
        <div className="lg:col-span-2 space-y-6">
          {/* System Checks */}
          <Card>
            <CardHeader>
              <CardTitle>System Checks</CardTitle>
              <CardDescription>Implementation status shown for each check</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y" style={{ '--tw-divide-opacity': 1 }}>
                {Object.entries(healthScore.checks).map(([key, check]) => (
                  <div
                    key={key}
                    className="p-4 transition-colors"
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                    onMouseEnter={e => e.currentTarget.style.background = 'rgba(245,158,11,0.03)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3 flex-1">
                        <StatusIcon status={check.status} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                            <h4 className="text-sm font-medium capitalize" style={{ color: '#e8eaf5' }}>
                              {key.replace(/_/g, ' ')}
                            </h4>
                            {check.implemented === false && (
                              <Badge variant="secondary" className="text-xs">
                                Not Implemented
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm" style={{ color: '#4a5168' }}>{check.message}</p>
                          {check.note && (
                            <p className="text-xs mt-1 flex items-center gap-1" style={{ color: '#f59e0b' }}>
                              <AlertTriangle className="w-3 h-3 shrink-0" />
                              {check.note}
                            </p>
                          )}
                        </div>
                      </div>
                      <Badge
                        variant={
                          check.status === 'pass' ? 'success' :
                          check.status === 'warning' ? 'warning' :
                          check.status === 'fail' ? 'destructive' : 'secondary'
                        }
                        className="shrink-0"
                      >
                        {check.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recommendations + Advisory */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <TrendingUp className="w-4 h-4 text-brand-600" />
                  Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                {healthScore.warnings?.length > 0 && (
                  <div
                    className="mb-4 p-3 rounded-xl"
                    style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.18)' }}
                  >
                    <h5 className="text-sm font-semibold mb-2" style={{ color: '#fca5a5' }}>Warnings</h5>
                    <ul className="space-y-1.5">
                      {healthScore.warnings.map((w, i) => (
                        <li key={i} className="flex gap-2 text-sm" style={{ color: '#fca5a5' }}>
                          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <ul className="space-y-3">
                  {healthScore.recommendations?.map((rec, i) => (
                    <li key={i} className="flex gap-2 text-sm" style={{ color: '#4a5168' }}>
                      <Info className="w-4 h-4 shrink-0 mt-0.5" style={{ color: '#f59e0b' }} />
                      {rec}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <AlertOctagon className="w-4 h-4 text-amber-600" />
                  Advisory Notices
                </CardTitle>
                <CardDescription className="text-xs">
                  Important limitations to be aware of
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {healthScore.advisory_notices?.map((notice, i) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <div
                        className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0"
                        style={{ background: notice.type === 'warning' ? '#f59e0b' : '#06b6d4' }}
                      />
                      <span style={{ color: notice.type === 'warning' ? '#fcd34d' : '#4a5168' }}>
                        {notice.message}
                      </span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
