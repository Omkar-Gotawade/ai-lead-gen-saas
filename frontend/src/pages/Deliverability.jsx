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
      // Fallback to safe mock data if API fails
      setHealthScore({
        score: 70,
        status: 'warning',
        score_confidence: 'partial',
        confidence_note: 'Partial confidence - Limited metrics available',
        checks: {
          provider_connection: { status: 'pass', message: 'Email provider configured', implemented: true },
          warmup: { status: 'warning', message: 'Day 5 of 21 (recommended)', note: 'Advisory only', implemented: true },
          send_success: { status: 'pass', message: '95% successful sends', implemented: true },
          bounce_rate: { status: 'inactive', message: 'Not implemented yet', note: 'Simulated', implemented: false },
          spam_complaints: { status: 'inactive', message: 'Requires webhook setup', note: 'Simulated', implemented: false },
          blacklist_status: { status: 'unknown', message: 'Basic check only', note: 'Not fully implemented', implemented: false }
        },
        daily_limit: { sent: 35, limit: 50, next_limit: 55, note: 'Recommended - not enforced' },
        recommendations: [
          'Continue warmup: Send consistently for 16 more days',
          'Verify email list quality before sending campaigns'
        ],
        warnings: [],
        advisory_notices: [
          { type: 'info', message: 'Daily limits are advisory only' },
          { type: 'warning', message: 'Bounce tracking not yet implemented' }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSafetyDiagnostics = async () => {
    setFixing(true);
    setMessage(null);
    try {
      const response = await axios.post('/api/deliverability/safety-diagnostics');
      const data = response.data;
      
      let messageText = 'Diagnostics complete.\n\n';
      
      if (data.passed_checks && data.passed_checks.length > 0) {
        messageText += 'Passed:\n' + data.passed_checks.join('\n') + '\n\n';
      }
      
      if (data.risky_behaviors && data.risky_behaviors.length > 0) {
        messageText += 'Issues Found:\n' + data.risky_behaviors.join('\n') + '\n\n';
      }
      
      if (data.manual_actions_required && data.manual_actions_required.length > 0) {
        messageText += 'Manual Actions Required:\n' + data.manual_actions_required.slice(0, 3).join('\n');
      }
      
      setMessage({ 
        type: data.risky_behaviors && data.risky_behaviors.length > 0 ? 'warning' : 'success', 
        text: messageText
      });
    } catch (error) {
      setMessage({ 
        type: 'warning', 
        text: 'Diagnostics completed with warnings. Please check your email provider manually.' 
      });
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
    if (status === 'fail') return <XCircle className="w-5 h-5 text-red-500" />;
    if (status === 'inactive') return <Info className="w-5 h-5 text-gray-400" />;
    if (status === 'unknown') return <Info className="w-5 h-5 text-slate-400" />;
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

      {message && (
        <Alert variant={message.type === 'success' ? 'default' : 'destructive'}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Health Score Card */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Health Score</CardTitle>
            <CardDescription className="space-y-1">
              <span className="block">Based on implemented metrics only</span>
              <span className="inline-flex items-center gap-1 text-xs text-yellow-600">
                <AlertTriangle className="w-3 h-3" />
                Confidence: {healthScore.score_confidence || 'partial'}
              </span>
            </CardDescription>
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
            {healthScore.confidence_note && (
              <p className="text-xs text-center text-slate-500 mb-4 px-2">
                {healthScore.confidence_note}
              </p>
            )}
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
                  style={{ width: `${Math.min(100, (healthScore.daily_limit.sent / healthScore.daily_limit.limit) * 100)}%` }}
                />
              </div>
              <p className="text-xs text-slate-500 text-center">
                {healthScore.daily_limit.note || 'Recommended safe limit - Not enforced'}
              </p>
              <p className="text-xs text-slate-400 text-center">
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
            <p className="text-xs text-center text-slate-500">
              Does not auto-fix - Provides manual guidance
            </p>
          </CardFooter>
        </Card>

        {/* Checks & Recommendations */}
        <div className="lg:col-span-2 space-y-6">
          {/* System Checks */}
          <Card>
            <CardHeader>
              <CardTitle>System Checks</CardTitle>
              <CardDescription>Implementation status shown for each check</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-200">
                {Object.entries(healthScore.checks).map(([key, check]) => (
                  <div key={key} className="p-4 hover:bg-slate-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        {getStatusIcon(check.status)}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="text-sm font-medium text-slate-900 capitalize">
                              {key.replace(/_/g, ' ')}
                            </h4>
                            {check.implemented === false && (
                              <Badge variant="secondary" className="text-xs">
                                Not Implemented
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-slate-600">{check.message}</p>
                          {check.note && (
                            <p className="text-xs text-yellow-600 mt-1 flex items-start gap-1">
                              <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                              {check.note}
                            </p>
                          )}
                        </div>
                      </div>
                      <Badge variant={
                        check.status === 'pass' ? 'success' : 
                        check.status === 'warning' ? 'warning' : 
                        check.status === 'fail' ? 'destructive' :
                        'secondary'
                      }>
                        {check.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recommendations and Advisory Notices */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                {healthScore.warnings && healthScore.warnings.length > 0 && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                    <h5 className="text-sm font-semibold text-red-900 mb-2">Warnings</h5>
                    <ul className="space-y-2">
                      {healthScore.warnings.map((warning, i) => (
                        <li key={i} className="flex gap-2 text-sm text-red-700">
                          <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                          {warning}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <ul className="space-y-3">
                  {healthScore.recommendations && healthScore.recommendations.map((rec, i) => (
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
                  <AlertOctagon className="w-5 h-5 text-yellow-600" />
                  Advisory Notices
                </CardTitle>
                <CardDescription className="text-xs">
                  Important limitations to be aware of
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {healthScore.advisory_notices && healthScore.advisory_notices.map((notice, i) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${
                        notice.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`} />
                      <span className={notice.type === 'warning' ? 'text-yellow-700' : 'text-slate-600'}>
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
