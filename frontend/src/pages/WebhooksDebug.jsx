import React, { useState, useEffect, useCallback } from 'react';
import {
  Inbox,
  Send,
  AlertCircle,
  CheckCircle,
  Reply,
  Eye,
  Ban,
  Filter,
  RefreshCw
} from 'lucide-react';
import api from '../api/axios';

import Button from '../components/ui/Button';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import EmptyState from '../components/ui/EmptyState';
import { SkeletonTable } from '../components/ui/Skeleton';

export default function WebhooksDebug() {
  const [events, setEvents] = useState([]);
  const [setupStatus, setSetupStatus] = useState(null);
  const [seeding, setSeeding] = useState(false);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState(null);

  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      params.append('limit', '100');
      if (filter !== 'all') params.append('event_type', filter);

      const [dbResponse, sendGridResponse] = await Promise.allSettled([
        api.get(`/api/webhooks/events?${params.toString()}`),
        api.get(`/api/webhooks/sendgrid/activity?${params.toString()}`),
      ]);

      let allEvents = [];
      if (dbResponse.status === 'fulfilled' && dbResponse.value?.data?.events) {
        allEvents = allEvents.concat(dbResponse.value.data.events);
      }
      if (sendGridResponse.status === 'fulfilled' && sendGridResponse.value?.data?.events) {
        allEvents = allEvents.concat(sendGridResponse.value.data.events);
      }

      const unique = Array.from(new Map(allEvents.map((e) => [e.id, e])).values());
      unique.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setEvents(unique);

      if (dbResponse.status === 'rejected' && sendGridResponse.status === 'rejected') {
        setError('Failed to load webhook events. Please try again.');
      }
    } catch {
      setError('Failed to load webhook events. Please try again.');
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  const fetchSetupStatus = useCallback(async () => {
    try {
      const response = await api.get('/api/webhooks/test');
      setSetupStatus(response.data);
    } catch {
      setSetupStatus(null);
    }
  }, []);

  const seedSampleEvents = async () => {
    try {
      setSeeding(true);
      await api.post('/api/webhooks/create-sample-events');
      await fetchEvents();
    } finally {
      setSeeding(false);
    }
  };

  useEffect(() => {
    fetchEvents();
    fetchSetupStatus();
  }, [fetchEvents, fetchSetupStatus]);

  const getEventIcon = (type) => {
    switch (type) {
      case 'sent':      return <Send         className="w-3.5 h-3.5" />;
      case 'delivered': return <CheckCircle  className="w-3.5 h-3.5" />;
      case 'reply':     return <Reply        className="w-3.5 h-3.5" />;
      case 'bounce':    return <AlertCircle  className="w-3.5 h-3.5" />;
      case 'spam':      return <Ban          className="w-3.5 h-3.5" />;
      case 'open':      return <Eye          className="w-3.5 h-3.5" />;
      default:          return <Inbox        className="w-3.5 h-3.5" />;
    }
  };

  const getEventBadgeVariant = (type) => {
    switch (type) {
      case 'delivered': return 'success';
      case 'reply':     return 'success';
      case 'open':      return 'default';
      case 'bounce':    return 'destructive';
      case 'spam':      return 'destructive';
      case 'sent':      return 'secondary';
      default:          return 'secondary';
    }
  };

  const FILTERS = [
    { id: 'all',       label: 'All Events', icon: Filter },
    { id: 'sent',      label: 'Sent',       icon: Send },
    { id: 'delivered', label: 'Delivered',  icon: CheckCircle },
    { id: 'reply',     label: 'Replies',    icon: Reply },
    { id: 'bounce',    label: 'Bounces',    icon: AlertCircle },
    { id: 'spam',      label: 'Spam',       icon: Ban },
    { id: 'open',      label: 'Opens',      icon: Eye },
  ];

  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="page-title">Email Events</h1>
          <p className="page-subtitle mt-0.5">Monitor real-time delivery events and webhooks</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchEvents}
          icon={<RefreshCw className="w-3.5 h-3.5" />}
          isLoading={loading}
        >
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold text-ink-900">Local Webhook Test</h2>
                <p className="text-sm text-ink-500 mt-0.5">
                  Localhost cannot receive provider webhooks directly. Use a tunnel like ngrok or Cloudflare Tunnel, then point SendGrid/Gmail to that public URL.
                </p>
              </div>
              <Badge variant={setupStatus ? 'success' : 'secondary'}>
                {setupStatus ? 'ready' : 'checking'}
              </Badge>
            </div>
            {setupStatus && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-ink-500">
                <div className="rounded-xl bg-ink-50 p-3">
                  <div className="text-xs uppercase tracking-wide text-ink-400">SendGrid</div>
                  <div>{setupStatus.sendgrid_configured ? 'Configured' : 'Not configured'}</div>
                </div>
                <div className="rounded-xl bg-ink-50 p-3">
                  <div className="text-xs uppercase tracking-wide text-ink-400">Gmail</div>
                  <div>{setupStatus.gmail_configured ? 'Configured' : 'Not configured'}</div>
                </div>
                <div className="rounded-xl bg-ink-50 p-3">
                  <div className="text-xs uppercase tracking-wide text-ink-400">Test status</div>
                  <div>{setupStatus.message}</div>
                </div>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchSetupStatus}
            icon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Check webhook setup
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={seedSampleEvents}
            isLoading={seeding}
            icon={<Reply className="w-3.5 h-3.5" />}
          >
            Seed sample reply event
          </Button>
          <div className="text-xs text-ink-400">
            Use this to verify the UI while your tunnel or provider setup is still being configured.
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="flex items-start gap-2.5 px-4 py-3 bg-danger/10 border border-danger/20 rounded-xl text-sm text-danger">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex flex-wrap gap-2">
            {FILTERS.map(({ id, label, icon: Icon }) => (
              <Button
                key={id}
                variant={filter === id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter(id)}
                icon={<Icon className="w-3.5 h-3.5" />}
                className={filter === id ? '' : 'text-ink-500'}
              >
                {label}
              </Button>
            ))}
          </div>
        </CardHeader>

        <CardContent className="p-0">
          {loading ? (
            <div className="p-6">
              <SkeletonTable rows={6} />
            </div>
          ) : events.length === 0 ? (
            <div className="py-16">
              <EmptyState
                icon={Inbox}
                title="No events found"
                description={
                  filter === 'all'
                    ? 'Events will appear here once your webhooks are configured.'
                    : `No ${filter} events found.`
                }
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Event Type</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Subject</th>
                    <th>Provider</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((event) => (
                    <tr key={event.id}>
                      <td className="whitespace-nowrap text-ink-400 text-xs">
                        {new Date(event.created_at).toLocaleString()}
                      </td>
                      <td className="whitespace-nowrap">
                        <Badge
                          variant={getEventBadgeVariant(event.event_type)}
                          className="flex items-center gap-1 w-fit"
                        >
                          {getEventIcon(event.event_type)}
                          <span className="capitalize">{event.event_type}</span>
                        </Badge>
                      </td>
                      <td
                        className="text-ink-900 max-w-[200px] truncate"
                        title={event.parsed_from}
                      >
                        {event.parsed_from}
                      </td>
                      <td
                        className="text-ink-900 max-w-[200px] truncate"
                        title={event.parsed_to}
                      >
                        {event.parsed_to}
                      </td>
                      <td
                        className="text-ink-500 max-w-[300px] truncate"
                        title={event.parsed_subject}
                      >
                        {event.parsed_subject || '—'}
                      </td>
                      <td className="whitespace-nowrap text-ink-400 text-xs capitalize">
                        {event.provider}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
