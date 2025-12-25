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
import { Line, Bar } from 'react-chartjs-2';

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
        beginAtZero: true
      }
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="ml-4 text-gray-600">{authLoading ? 'Loading user info...' : 'Loading analytics...'}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          <p className="font-semibold">Error loading analytics</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          <p className="font-semibold">Quick Fix:</p>
          <p className="text-sm mt-1">Click the "Logout" button (top right) and login again to refresh your session.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
        
        {/* Date Range Picker */}
        <div className="flex gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
            <input
              type="date"
              value={dateRange.since}
              onChange={(e) => setDateRange({ ...dateRange, since: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
            <input
              type="date"
              value={dateRange.until}
              onChange={(e) => setDateRange({ ...dateRange, until: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="mt-6">
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
            icon="📧"
            color="blue"
          />
          <MetricCard
            title="Delivered"
            value={overview.emails_delivered}
            subtitle={`${((overview.emails_delivered / overview.emails_sent) * 100 || 0).toFixed(1)}% delivery rate`}
            icon="✅"
            color="green"
          />
          <MetricCard
            title="Replies"
            value={overview.replies}
            subtitle={`${overview.reply_rate}% reply rate`}
            icon="💬"
            color="purple"
          />
          <MetricCard
            title="Bounces"
            value={overview.bounces}
            subtitle={`${overview.bounce_rate}% bounce rate`}
            icon="⚠️"
            color="red"
          />
        </div>
      )}

      {/* Additional Stats */}
      {overview && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Additional Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatItem label="Unique Leads Contacted" value={overview.unique_leads_contacted} />
            <StatItem label="Avg Opens per Lead" value="-" />
            <StatItem label="Best Performing Day" value="-" />
            <StatItem label="Response Time (avg)" value="-" />
          </div>
        </div>
      )}

      {/* Timeline Chart */}
      {timelineChartData && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Email Activity Timeline</h3>
          <div style={{ height: '400px' }}>
            <Line data={timelineChartData} options={chartOptions} />
          </div>
        </div>
      )}

      {/* Summary Stats */}
      {timeline && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Period Summary</h3>
          <div className="grid grid-cols-3 gap-4">
            <StatItem label="Total Sent" value={timeline.total_sent} />
            <StatItem label="Total Replies" value={timeline.total_replies} />
            <StatItem label="Total Bounces" value={timeline.total_bounces} />
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, subtitle, icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600',
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-gray-900">{value.toLocaleString()}</p>
      {subtitle && (
        <p className={`text-sm mt-1 ${colorClasses[color]}`}>{subtitle}</p>
      )}
    </div>
  );
}

function StatItem({ label, value }) {
  return (
    <div>
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}
