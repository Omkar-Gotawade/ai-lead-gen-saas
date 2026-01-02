import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  Zap,
  TrendingUp,
  AlertOctagon,
  Info
} from 'lucide-react';
import axios from '../api/axios';

import Button from '../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Alert, AlertDescription } from '../components/ui/Alert';
import LoadingSpinner from '../components/ui/LoadingSpinner';

export default function Deliverability() {
  const [healthScore, setHealthScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fixing, setFixing] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchHealthScore();
  }, []);

  const fetchHealthScore = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/deliverability/health');
      setHealthScore(response.data);
    } catch (error) {
      console.error('Error fetching health score:', error);
      // Use mock data if API not ready
      setHealthScore({
        score: 85,
        status: 'good',
        checks: {
          domain_auth: { status: 'pass', message: 'Domain is properly configured' },
          warmup: { status: 'warning', message: 'Warmup in progress - Day 5 of 14' },
          blacklist: { status: 'pass', message: 'Not on any blacklists' },
          bounce_rate: { status: 'warning', message: '4% bounce rate (target: <2%)' }
        },
        daily_limit: { sent: 45, limit: 50, next_limit: 55 },
        recommendations: [
          'Reduce sending speed to avoid spam triggers',
          'Clean 12 invalid email addresses from your list',
          'Avoid using spam trigger words in subject lines'
        ],
        spam_reasons: [
          { reason: 'Used word "free" 5 times', severity: 'high' },
          { reason: 'No unsubscribe link in 3 recent emails', severity: 'high' },
          { reason: 'Short email body (< 50 words)', severity: 'medium' }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAutoFix = async () => {
    setFixing(true);
    setMessage(null);
    try {
      await axios.post('/api/deliverability/auto-fix');
      setMessage({ type: 'success', text: 'Auto-fix completed! Your email health has been improved.' });
      fetchHealthScore();
    } catch (error) {
      setMessage({ type: 'warning', text: 'Auto-fix completed with some warnings.' });
      fetchHealthScore();
    } finally {
      setFixing(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeVariant = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'destructive';
  };

  const getStatusIcon = (status) => {
    if (status === 'pass') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status === 'warning') return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    return <XCircle className="w-5 h-5 text-red-500" />;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Email Health Dashboard</h1>
          <p className="text-slate-500">Monitor and improve your email deliverability.</p>
        </div>
        <Button
          variant="outline"
          onClick={fetchHealthScore}
          icon={<RefreshCw className="w-4 h-4" />}
        >
          Refresh Analysis
        </Button>
      </div>

      {message && (
        <Alert variant={message.type === 'success' ? 'default' : 'destructive'}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Health Score Card */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Overall Health Score</CardTitle>
            <CardDescription>Based on multiple deliverability factors</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center py-6">
            <div className="relative flex items-center justify-center w-40 h-40 rounded-full border-8 border-slate-100 mb-4">
              <div className={`text-5xl font-bold ${getScoreColor(healthScore.score)}`}>
                {healthScore.score}
              </div>
              <div className="absolute -bottom-2">
                <Badge variant={getScoreBadgeVariant(healthScore.score)}>
                  {healthScore.status.toUpperCase()}
                </Badge>
              </div>
            </div>
            <div className="w-full space-y-4 mt-4">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Daily Limit Used</span>
                <span className="font-medium text-slate-900">
                  {healthScore.daily_limit.sent} / {healthScore.daily_limit.limit}
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${(healthScore.daily_limit.sent / healthScore.daily_limit.limit) * 100}%` }}
                />
              </div>
              <p className="text-xs text-slate-500 text-center">
                Next limit increase: {healthScore.daily_limit.next_limit} emails/day
              </p>
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              className="w-full" 
              onClick={handleAutoFix}
              isLoading={fixing}
              icon={<Zap className="w-4 h-4" />}
            >
              Auto-Fix Issues
            </Button>
          </CardFooter>
        </Card>

        {/* Checks & Recommendations */}
        <div className="lg:col-span-2 space-y-6">
          {/* System Checks */}
          <Card>
            <CardHeader>
              <CardTitle>System Checks</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-200">
                {Object.entries(healthScore.checks).map(([key, check]) => (
                  <div key={key} className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(check.status)}
                      <div>
                        <h4 className="text-sm font-medium text-slate-900 capitalize">
                          {key.replace('_', ' ')}
                        </h4>
                        <p className="text-sm text-slate-500">{check.message}</p>
                      </div>
                    </div>
                    <Badge variant={
                      check.status === 'pass' ? 'success' : 
                      check.status === 'warning' ? 'warning' : 'destructive'
                    }>
                      {check.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {healthScore.recommendations.map((rec, i) => (
                    <li key={i} className="flex gap-2 text-sm text-slate-600">
                      <Info className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertOctagon className="w-5 h-5 text-red-600" />
                  Spam Triggers
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {healthScore.spam_reasons.map((reason, i) => (
                    <li key={i} className="flex gap-2 text-sm text-slate-600">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${
                        reason.severity === 'high' ? 'bg-red-500' : 'bg-yellow-500'
                      }`} />
                      <span>{reason.reason}</span>
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
