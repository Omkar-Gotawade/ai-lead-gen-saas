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
          font: { size: 12, family: 'Inter, sans-serif' },
          color: '#64748b',
        },
      },
      title: { display: false },
      tooltip: {
        backgroundColor: '#0f1117',
        borderColor: '#1e293b',
        borderWidth: 1,
        cornerRadius: 10,
        titleFont: { size: 12, family: 'Inter, sans-serif' },
        bodyFont: { size: 12, family: 'Inter, sans-serif' },
        padding: 10,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: '#f1f5f9' },
        ticks: { font: { size: 11, family: 'Inter, sans-serif' }, color: '#94a3b8' },
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 11, family: 'Inter, sans-serif' }, color: '#94a3b8' },
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
        <div className="flex flex-wrap items-end gap-3 bg-surface border border-ink-100 rounded-xl px-4 py-3 shadow-soft">
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium text-ink-400 uppercase tracking-wide">From</label>
            <input
              type="date"
              value={dateRange.since}
              onChange={(e) => setDateRange({ ...dateRange, since: e.target.value })}
              className="text-sm border border-ink-200 rounded-lg px-3 py-1.5 bg-surface text-ink-800 focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium text-ink-400 uppercase tracking-wide">To</label>
            <input
              type="date"
              value={dateRange.until}
              onChange={(e) => setDateRange({ ...dateRange, until: e.target.value })}
              className="text-sm border border-ink-200 rounded-lg px-3 py-1.5 bg-surface text-ink-800 focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium text-ink-400 uppercase tracking-wide">Granularity</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="text-sm border border-ink-200 rounded-lg px-3 py-1.5 bg-surface text-ink-800 focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500"
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
    </div>
  );
}

function MetricCard({ title, value, sub, icon: Icon, accent = 'brand' }) {
  const accentMap = {
    brand:   { bg: 'bg-brand-50',   icon: 'text-brand-600',   badge: 'bg-brand-100 text-brand-700' },
    success: { bg: 'bg-success/8',  icon: 'text-emerald-600', badge: 'bg-success/10 text-emerald-700' },
    purple:  { bg: 'bg-purple-50',  icon: 'text-purple-600',  badge: 'bg-purple-100 text-purple-700' },
    danger:  { bg: 'bg-danger/8',   icon: 'text-red-600',     badge: 'bg-danger/10 text-red-700' },
  };
  const c = accentMap[accent] || accentMap.brand;

  return (
    <Card>
      <CardContent>
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-medium text-ink-500 uppercase tracking-wide">{title}</p>
          <div className={`w-8 h-8 rounded-lg ${c.bg} flex items-center justify-center`}>
            <Icon className={`w-4 h-4 ${c.icon}`} />
          </div>
        </div>
        <p className="text-3xl font-bold text-ink-900">{typeof value === 'number' ? value.toLocaleString() : '0'}</p>
        {sub && (
          <span className={`inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full ${c.badge}`}>{sub}</span>
        )}
      </CardContent>
    </Card>
  );
}

