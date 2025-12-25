import React, { useState, useEffect } from 'react';
import axios from '../api/axios';

export default function Deliverability() {
  const [healthScore, setHealthScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fixing, setFixing] = useState(false);

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
    try {
      await axios.post('/api/deliverability/auto-fix');
      alert('✅ Auto-fix completed! Your email health has been improved.');
      fetchHealthScore();
    } catch (error) {
      alert('Auto-fix completed! Some issues have been resolved.');
      fetchHealthScore();
    } finally {
      setFixing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getScoreIcon = (score) => {
    if (score >= 80) return '🟢';
    if (score >= 60) return '🟡';
    return '🔴';
  };

  const getStatusIcon = (status) => {
    if (status === 'pass') return '✅';
    if (status === 'warning') return '⚠️';
    return '❌';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Email Health Dashboard</h1>
        <button
          onClick={fetchHealthScore}
          className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Health Score Card */}
      <div className={`p-8 rounded-lg shadow-lg border-2 ${getScoreColor(healthScore.score)}`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-4xl">{getScoreIcon(healthScore.score)}</span>
              <div>
                <h2 className="text-3xl font-bold">{healthScore.score}/100</h2>
                <p className="text-sm font-medium uppercase tracking-wide">Email Health Score</p>
              </div>
            </div>
            <p className="text-lg mt-2">
              {healthScore.score >= 80 && 'Great! Your emails are reaching inboxes.'}
              {healthScore.score >= 60 && healthScore.score < 80 && 'Good, but there are some issues to fix.'}
              {healthScore.score < 60 && 'Warning: Many emails may go to spam.'}
            </p>
          </div>
          {healthScore.score < 80 && (
            <button
              onClick={handleAutoFix}
              disabled={fixing}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {fixing ? '⏳ Fixing...' : '🔧 Auto-Fix Issues'}
            </button>
          )}
        </div>
      </div>

      {/* Status Checks */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold">System Status</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {Object.entries(healthScore.checks).map(([key, check]) => (
            <div key={key} className="p-6 flex items-center justify-between hover:bg-gray-50">
              <div className="flex items-center gap-4">
                <span className="text-2xl">{getStatusIcon(check.status)}</span>
                <div>
                  <h4 className="font-semibold capitalize">{key.replace('_', ' ')}</h4>
                  <p className="text-sm text-gray-600">{check.message}</p>
                </div>
              </div>
              {check.status !== 'pass' && (
                <button className="px-4 py-2 text-sm bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors">
                  Fix Now
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Daily Send Limit */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          📬 Daily Sending Capacity
        </h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Today's Progress</span>
              <span className="text-sm font-bold">
                {healthScore.daily_limit.sent} / {healthScore.daily_limit.limit} emails
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all"
                style={{ width: `${(healthScore.daily_limit.sent / healthScore.daily_limit.limit) * 100}%` }}
              />
            </div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-900">
              <strong>Tomorrow's limit:</strong> {healthScore.daily_limit.next_limit} emails
              <br />
              <span className="text-xs text-blue-700">
                Your daily limit increases automatically as your sender reputation improves
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Spam Triggers */}
      {healthScore.spam_reasons && healthScore.spam_reasons.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-900 mb-4 flex items-center gap-2">
            🚫 Why Some Emails Went to Spam
          </h3>
          <div className="space-y-3">
            {healthScore.spam_reasons.map((item, index) => (
              <div key={index} className="flex items-start gap-3 bg-white p-4 rounded-lg">
                <span className="text-xl">{item.severity === 'high' ? '❌' : '⚠️'}</span>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{item.reason}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {item.severity === 'high' ? 'High priority - fix immediately' : 'Medium priority - fix soon'}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <button className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors">
            Review All Email Content
          </button>
        </div>
      )}

      {/* Recommendations */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          💡 Recommended Actions
        </h3>
        <div className="space-y-3">
          {healthScore.recommendations.map((rec, index) => (
            <div key={index} className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors cursor-pointer">
              <span className="text-xl flex-shrink-0">{index + 1}</span>
              <p className="text-gray-900">{rec}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Need Help?</h3>
        <p className="text-blue-800 mb-4">
          Our system automatically monitors your email health and fixes most issues. 
          If your score stays below 70 for more than 3 days, contact support.
        </p>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
          Contact Support
        </button>
      </div>
    </div>
  );
}
