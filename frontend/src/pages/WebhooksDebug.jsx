import React, { useState, useEffect } from 'react';
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
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Alert, AlertDescription } from '../components/ui/Alert';

export default function WebhooksDebug() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, [filter]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      params.append('limit', '100');
      if (filter !== 'all') {
        params.append('event_type', filter);
      }
      
      // Fetch from both sources simultaneously
      const [dbResponse, sendGridResponse] = await Promise.allSettled([
        api.get(`/api/webhooks/events?${params.toString()}`),
        api.get(`/api/webhooks/sendgrid/activity?${params.toString()}`)
      ]);
      
      let allEvents = [];
      
      // Add database events
      if (dbResponse.status === 'fulfilled' && dbResponse.value?.data?.events) {
        allEvents = allEvents.concat(dbResponse.value.data.events);
      }
      
      // Add SendGrid API events
      if (sendGridResponse.status === 'fulfilled' && sendGridResponse.value?.data?.events) {
        allEvents = allEvents.concat(sendGridResponse.value.data.events);
      }
      
      // Remove duplicates based on id and sort by created_at
      const uniqueEvents = Array.from(
        new Map(allEvents.map(event => [event.id, event])).values()
      );
      
      uniqueEvents.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      
      setEvents(uniqueEvents);
      
      // Show error only if both failed
      if (dbResponse.status === 'rejected' && sendGridResponse.status === 'rejected') {
        setError('Failed to load webhook events. Please try again.');
      }
    } catch (error) {
      console.error('Error fetching webhook events:', error);
      setError('Failed to load webhook events. Please try again.');
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (type) => {
    switch (type) {
      case 'sent': return <Send className="w-4 h-4" />;
      case 'delivered': return <CheckCircle className="w-4 h-4" />;
      case 'reply': return <Reply className="w-4 h-4" />;
      case 'bounce': return <AlertCircle className="w-4 h-4" />;
      case 'spam': return <Ban className="w-4 h-4" />;
      case 'open': return <Eye className="w-4 h-4" />;
      default: return <Inbox className="w-4 h-4" />;
    }
  };

  const getEventBadgeVariant = (type) => {
    switch (type) {
      case 'delivered': return 'success';
      case 'reply': return 'success';
      case 'open': return 'info';
      case 'bounce': return 'destructive';
      case 'spam': return 'destructive';
      case 'sent': return 'default';
      default: return 'secondary';
    }
  };

  const filters = [
    { id: 'all', label: 'All Events', icon: Filter },
    { id: 'sent', label: 'Sent', icon: Send },
    { id: 'delivered', label: 'Delivered', icon: CheckCircle },
    { id: 'reply', label: 'Replies', icon: Reply },
    { id: 'bounce', label: 'Bounces', icon: AlertCircle },
    { id: 'spam', label: 'Spam', icon: Ban },
    { id: 'open', label: 'Opens', icon: Eye },
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
          loading={loading}
        >
          Refresh
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <div className="flex flex-wrap gap-2">
            {filters.map((f) => {
              const IconComponent = f.icon;
              return (
                <Button
                  key={f.id}
                  variant={filter === f.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter(f.id)}
                  icon={<IconComponent className="w-4 h-4" />}
                  className={filter === f.id ? '' : 'text-slate-600'}
                >
                  {f.label}
                </Button>
              );
            })}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <LoadingSpinner size="lg" />
            </div>
          ) : events.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Inbox className="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p className="text-lg font-medium mb-1">No events found</p>
              <p className="text-sm">
                {filter === 'all' 
                  ? 'Events will appear here once your webhooks are configured.' 
                  : `No ${filter} events found.`}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3 font-medium">Time</th>
                    <th className="px-6 py-3 font-medium">Event Type</th>
                    <th className="px-6 py-3 font-medium">From</th>
                    <th className="px-6 py-3 font-medium">To</th>
                    <th className="px-6 py-3 font-medium">Subject</th>
                    <th className="px-6 py-3 font-medium">Provider</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {events.map((event) => (
                    <tr key={event.id} className="bg-white hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-slate-500">
                        {new Date(event.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant={getEventBadgeVariant(event.event_type)} className="flex items-center gap-1 w-fit">
                          {getEventIcon(event.event_type)}
                          <span className="capitalize">{event.event_type}</span>
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-slate-900 max-w-[200px] truncate" title={event.parsed_from}>
                        {event.parsed_from}
                      </td>
                      <td className="px-6 py-4 text-slate-900 max-w-[200px] truncate" title={event.parsed_to}>
                        {event.parsed_to}
                      </td>
                      <td className="px-6 py-4 text-slate-600 max-w-[300px] truncate" title={event.parsed_subject}>
                        {event.parsed_subject || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-500">
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
