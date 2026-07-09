import React, { useState, useEffect } from 'react';
import axios from '../api/axios';
import { useAuth } from '../context/AuthContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { 
  Calendar, 
  BarChart2, 
  Mail, 
  CheckCircle, 
  MessageSquare, 
  AlertTriangle,
  TrendingUp,
  Users,
  Clock,
  Activity
} from 'lucide-react';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Alert, AlertDescription } from '../components/ui/Alert';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Badge from '../components/ui/Badge';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function MetricsDashboard() {
  const { user, loading: authLoading } = useAuth();
  const [overview, setOverview] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [repliedLeads, setRepliedLeads] = useState([]);
  const [period, setPeriod] = useState('daily');
  const [dateRange, setDateRange] = useState({
    since: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    until: new Date().toISOString().split('T')[0]
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    if (!user?.id) {
      console.error('No user.id found. User object:', user);
      setError('Unable to load user information. Please logout and login again.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const orgId = user.id;

      // Fetch overview metrics
      const overviewRes = await axios.get(`/api/metrics/org/${orgId}/overview`, {
        params: dateRange
      });
      setOverview(overviewRes.data);

      // Fetch timeline data
      const timelineRes = await axios.get(`/api/metrics/org/${orgId}/timeline`, {
        params: { ...dateRange, period }
      });
      setTimeline(timelineRes.data);

      const repliedLeadsRes = await axios.get(`/api/metrics/org/${orgId}/replied-leads`, {
        params: { ...dateRange, limit: 10 }
      });
      setRepliedLeads(repliedLeadsRes.data?.leads || []);
    } catch (err) {
      console.error('Error fetching metrics:', err);
      setError(err.response?.data?.detail || 'Failed to load metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Wait for auth to finish loading
    if (authLoading) {
      return;
    }
    
    if (user?.id) {
      fetchMetrics();
    } else {
      setError('Unable to load user information. Please logout and login again.');
      setLoading(false);
    }
  }, [dateRange, period, user, authLoading]);

  const timelineChartData = timeline ? {
    labels: timeline.data.map(d => d.date),
    datasets: [
      {
        label: 'Emails Sent',
        data: timeline.data.map(d => d.sent),
        borderColor: '#7c3aed',
        backgroundColor: 'rgba(124, 58, 237, 0.08)',
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
      {
        label: 'Delivered',
        data: timeline.data.map(d => d.delivered),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.08)',
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
      {
        label: 'Replies',
        data: timeline.data.map(d => d.replies),
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.08)',
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
      {
        label: 'Bounces',
        data: timeline.data.map(d => d.bounces),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.08)',
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
    ]
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 16,
          font: { size: 12, family: 'DM Sans, sans-serif' },
          color: '#4a5168',
        },
      },
      title: { display: false },
      tooltip: {
        backgroundColor: '#0a0b0f',
        borderColor: 'rgba(245,158,11,0.2)',
        borderWidth: 1,
        cornerRadius: 10,
        titleFont: { size: 12, family: 'DM Sans, sans-serif' },
        bodyFont: { size: 12, family: 'DM Sans, sans-serif' },
        padding: 10,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255,255,255,0.04)' },
        ticks: { font: { size: 11, family: 'DM Sans, sans-serif' }, color: '#343a52' },
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 11, family: 'DM Sans, sans-serif' }, color: '#343a52' },
      },
    },
  };

  if (authLoading || loading) {
    return (
      <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
        <div>
          <div className="skeleton h-8 w-32 rounded mb-2" />
          <div className="skeleton h-4 w-56 rounded" />
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-surface border border-ink-100 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="skeleton h-3 w-24 rounded" />
                <div className="skeleton w-8 h-8 rounded-lg" />
              </div>
              <div className="skeleton h-9 w-20 rounded mb-3" />
              <div className="skeleton h-5 w-16 rounded-full" />
            </div>
          ))}
        </div>
        <div className="bg-surface border border-ink-100 rounded-xl p-5">
          <div className="skeleton h-6 w-40 rounded mb-4" />
          <div className="skeleton h-64 w-full rounded-lg" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-3 max-w-xl">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Alert variant="warning">
          <AlertDescription>
            <strong>Quick fix:</strong> Sign out and back in to refresh your session.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        <div>
          <h1 className="page-title">Analytics</h1>
          <p className="page-subtitle mt-0.5">Track campaign performance and engagement</p>
        </div>

        {/* Filters */}
        <div
          className="flex flex-wrap items-end gap-3 rounded-xl px-4 py-3"
          style={{ background: '#111220', border: '1px solid rgba(255,255,255,0.06)' }}
        >
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium uppercase tracking-wide" style={{ color: '#343a52' }}>From</label>
            <input
              type="date"
              value={dateRange.since}
              onChange={(e) => setDateRange({ ...dateRange, since: e.target.value })}
              className="text-sm rounded-lg px-3 py-1.5 focus:outline-none transition-colors"
              style={{ background: '#0d0e18', border: '1px solid rgba(255,255,255,0.07)', color: '#c8cce0' }}
              onFocus={e => e.target.style.borderColor = '#d97706'}
              onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.07)'}
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium uppercase tracking-wide" style={{ color: '#343a52' }}>To</label>
            <input
              type="date"
              value={dateRange.until}
              onChange={(e) => setDateRange({ ...dateRange, until: e.target.value })}
              className="text-sm rounded-lg px-3 py-1.5 focus:outline-none transition-colors"
              style={{ background: '#0d0e18', border: '1px solid rgba(255,255,255,0.07)', color: '#c8cce0' }}
              onFocus={e => e.target.style.borderColor = '#d97706'}
              onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.07)'}
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium uppercase tracking-wide" style={{ color: '#343a52' }}>Granularity</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="text-sm rounded-lg px-3 py-1.5 focus:outline-none transition-colors"
              style={{ background: '#0d0e18', border: '1px solid rgba(255,255,255,0.07)', color: '#c8cce0' }}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
        </div>
      </div>

      {/* KPI cards */}
      {overview && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard title="Emails Sent"  value={overview.emails_sent}            icon={Mail}          accent="brand"   />
          <MetricCard title="Delivered"    value={overview.emails_delivered}        icon={CheckCircle}   accent="success"
            sub={`${((overview.emails_delivered / overview.emails_sent) * 100 || 0).toFixed(1)}% rate`} />
          <MetricCard title="Replies"      value={overview.replies}                 icon={MessageSquare} accent="purple"
            sub={`${overview.reply_rate}% reply rate`} />
          <MetricCard title="Bounces"      value={overview.bounces}                 icon={AlertTriangle} accent="danger"
            sub={`${overview.bounce_rate}% bounce rate`} />
        </div>
      )}

      {/* Secondary stats */}
      {overview && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-ink-400" />
              Engagement Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { label: 'Unique Leads Contacted', value: overview.unique_leads_contacted, icon: Users, isReal: true },
                { label: 'Avg Opens per Lead',      value: null, icon: TrendingUp },
                { label: 'Best Performing Day',     value: null, icon: Calendar },
                { label: 'Avg Response Time',       value: null, icon: Clock },
              ].map(({ label, value, icon: Icon, isReal }) => (
                <div key={label} className="flex items-start gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-ink-50 flex items-center justify-center shrink-0">
                    <Icon className="w-4 h-4 text-ink-400" />
                  </div>
                  <div>
                    <p className="text-xs text-ink-400">{label}</p>
                    {isReal ? (
                      <p className="text-lg font-semibold text-ink-800 mt-0.5">
                        {typeof value === 'number' ? value.toLocaleString() : value}
                      </p>
                    ) : (
                      <span className="coming-soon mt-0.5">coming soon</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Timeline chart */}
      {timelineChartData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-ink-400" />
              Email Activity Timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div style={{ height: '320px' }}>
              <Line data={timelineChartData} options={chartOptions} />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Period summary */}
      {timeline && (
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Total Sent',    value: timeline.total_sent },
            { label: 'Total Replies', value: timeline.total_replies },
            { label: 'Total Bounces', value: timeline.total_bounces },
          ].map(({ label, value }) => (
            <div key={label} className="stat-card">
              <p className="text-xs font-medium text-ink-400">{label}</p>
              <p className="text-3xl font-bold text-ink-900 mt-2">{value?.toLocaleString() ?? 0}</p>
            </div>
          ))}
        </div>
      )}

      {/* Replied leads */}
      {repliedLeads && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-ink-400" />
                Replied Leads
              </span>
              <Badge variant={repliedLeads.length > 0 ? 'success' : 'secondary'}>
                {repliedLeads.length} shown
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {repliedLeads.length === 0 ? (
              <div className="rounded-xl border border-dashed border-ink-200 p-6 text-sm text-ink-500">
                No replied leads found for this date range. Once webhooks are working, replies will appear here.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Lead</th>
                      <th>Email</th>
                      <th>Campaign</th>
                      <th>Replied At</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {repliedLeads.map((lead) => (
                      <tr key={`${lead.lead_id}-${lead.reply_message_id || lead.replied_at}`}>
                        <td className="text-ink-900">
                          {lead.first_name} {lead.last_name}
                        </td>
                        <td className="text-ink-500">{lead.email}</td>
                        <td className="text-ink-500">
                          <div className="font-medium text-ink-800">{lead.campaign_name}</div>
                          {lead.company && <div className="text-xs text-ink-400">{lead.company}</div>}
                        </td>
                        <td className="whitespace-nowrap text-ink-400 text-xs">
                          {new Date(lead.replied_at).toLocaleString()}
                        </td>
                        <td>
                          <Badge variant="success">replied</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function MetricCard({ title, value, sub, icon: Icon, accent = 'brand' }) {
  const accentMap = {
    brand:   { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.2)',  badgeBg: 'rgba(245,158,11,0.12)', badgeText: '#f59e0b' },
    success: { color: '#10b981', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)', badgeBg: 'rgba(16,185,129,0.12)', badgeText: '#10b981' },
    purple:  { color: '#06b6d4', bg: 'rgba(6,182,212,0.1)',  border: 'rgba(6,182,212,0.2)',  badgeBg: 'rgba(6,182,212,0.12)',  badgeText: '#06b6d4' },
    danger:  { color: '#ef4444', bg: 'rgba(239,68,68,0.1)',  border: 'rgba(239,68,68,0.2)',  badgeBg: 'rgba(239,68,68,0.12)',  badgeText: '#ef4444' },
  };
  const c = accentMap[accent] || accentMap.brand;

  return (
    <Card>
      <CardContent>
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#343a52' }}>{title}</p>
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: c.bg, border: `1px solid ${c.border}` }}
          >
            <Icon className="w-4 h-4" style={{ color: c.color }} />
          </div>
        </div>
        <p
          className="text-3xl stat-number"
          style={{ color: '#f0f2ff' }}
        >
          {typeof value === 'number' ? value.toLocaleString() : '0'}
        </p>
        {sub && (
          <span
            className="inline-flex items-center mt-2 text-xs font-medium px-2 py-0.5 rounded-full"
            style={{ background: c.badgeBg, color: c.badgeText }}
          >{sub}</span>
        )}
      </CardContent>
    </Card>
  );
}

