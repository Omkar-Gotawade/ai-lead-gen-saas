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
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.3
      },
      {
        label: 'Delivered',
        data: timeline.data.map(d => d.delivered),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.3
      },
      {
        label: 'Replies',
        data: timeline.data.map(d => d.replies),
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        tension: 0.3
      },
      {
        label: 'Bounces',
        data: timeline.data.map(d => d.bounces),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.3
      }
    ]
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: '#f1f5f9'
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Alert className="bg-yellow-50 border-yellow-200 text-yellow-800">
          <AlertTriangle className="w-4 h-4 text-yellow-600" />
          <AlertDescription>
            <strong>Quick Fix:</strong> Click the "Logout" button (top right) and login again to refresh your session.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Analytics Dashboard</h1>
          <p className="text-slate-500">Track your campaign performance and engagement.</p>
        </div>
        
        {/* Date Range Picker */}
        <div className="flex flex-wrap gap-4 items-end bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
          <div className="w-full sm:w-auto">
            <label className="block text-xs font-medium text-slate-500 mb-1">From</label>
            <input
              type="date"
              value={dateRange.since}
              onChange={(e) => setDateRange({ ...dateRange, since: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="w-full sm:w-auto">
            <label className="block text-xs font-medium text-slate-500 mb-1">To</label>
            <input
              type="date"
              value={dateRange.until}
              onChange={(e) => setDateRange({ ...dateRange, until: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="w-full sm:w-auto">
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
        </div>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Emails Sent"
            value={overview.emails_sent}
            icon={Mail}
            color="blue"
          />
          <MetricCard
            title="Delivered"
            value={overview.emails_delivered}
            subtitle={`${((overview.emails_delivered / overview.emails_sent) * 100 || 0).toFixed(1)}% delivery rate`}
            icon={CheckCircle}
            color="green"
          />
          <MetricCard
            title="Replies"
            value={overview.replies}
            subtitle={`${overview.reply_rate}% reply rate`}
            icon={MessageSquare}
            color="purple"
          />
          <MetricCard
            title="Bounces"
            value={overview.bounces}
            subtitle={`${overview.bounce_rate}% bounce rate`}
            icon={AlertTriangle}
            color="red"
          />
        </div>
      )}

      {/* Additional Stats */}
      {overview && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Activity className="w-5 h-5 text-slate-500" />
              Additional Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <StatItem 
                label="Unique Leads Contacted" 
                value={overview.unique_leads_contacted} 
                icon={Users}
              />
              <StatItem 
                label="Avg Opens per Lead" 
                value="-" 
                icon={TrendingUp}
              />
              <StatItem 
                label="Best Performing Day" 
                value="-" 
                icon={Calendar}
              />
              <StatItem 
                label="Response Time (avg)" 
                value="-" 
                icon={Clock}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Timeline Chart */}
      {timelineChartData && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart2 className="w-5 h-5 text-slate-500" />
              Email Activity Timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div style={{ height: '400px' }}>
              <Line data={timelineChartData} options={chartOptions} />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Stats */}
      {timeline && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Period Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <p className="text-sm text-slate-500 mb-1">Total Sent</p>
                <p className="text-2xl font-bold text-slate-900">{timeline.total_sent}</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <p className="text-sm text-slate-500 mb-1">Total Replies</p>
                <p className="text-2xl font-bold text-slate-900">{timeline.total_replies}</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <p className="text-sm text-slate-500 mb-1">Total Bounces</p>
                <p className="text-2xl font-bold text-slate-900">{timeline.total_bounces}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function MetricCard({ title, value, subtitle, icon: Icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600',
  };

  const iconBgClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    red: 'bg-red-100 text-red-600',
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-medium text-slate-600">{title}</p>
          <div className={`p-2 rounded-lg ${iconBgClasses[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
        <p className="text-3xl font-bold text-slate-900">{value.toLocaleString()}</p>
        {subtitle && (
          <div className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium mt-2 ${colorClasses[color]}`}>
            {subtitle}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function StatItem({ label, value, icon: Icon }) {
  return (
    <div className="flex items-start gap-3">
      {Icon && <Icon className="w-5 h-5 text-slate-400 mt-0.5" />}
      <div>
        <p className="text-sm text-slate-500">{label}</p>
        <p className="text-xl font-semibold text-slate-900 mt-1">{value}</p>
      </div>
    </div>
  );
}
