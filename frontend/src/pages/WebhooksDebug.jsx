import React, { useState, useEffect } from 'react';
import axios from '../api/axios';

export default function WebhooksDebug() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchEvents();
  }, [filter]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      params.append('limit', '100');
      if (filter !== 'all') {
        params.append('event_type', filter);
      }
      
      const response = await axios.get(`/api/webhooks/events?${params.toString()}`);
      setEvents(response.data.events || []);
    } catch (error) {
      console.error('Error fetching webhook events:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Email Events</h1>
      </div>

      {/* Filter */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex gap-2 flex-wrap">
          <FilterButton
            active={filter === 'all'}
            onClick={() => setFilter('all')}
            label="All Events"
          />
          <FilterButton
            active={filter === 'sent'}
            onClick={() => setFilter('sent')}
            label="📤 Sent"
          />
          <FilterButton
            active={filter === 'failed'}
            onClick={() => setFilter('failed')}
            label="❌ Failed"
          />
          <FilterButton
            active={filter === 'delivered'}
            onClick={() => setFilter('delivered')}
            label="✅ Delivered"
          />
          <FilterButton
            active={filter === 'reply'}
            onClick={() => setFilter('reply')}
            label="↩️ Replies"
          />
          <FilterButton
            active={filter === 'bounce'}
            onClick={() => setFilter('bounce')}
            label="⚠️ Bounces"
          />
          <FilterButton
            active={filter === 'spam'}
            onClick={() => setFilter('spam')}
            label="🚫 Spam"
          />
          <FilterButton
            active={filter === 'open'}
            onClick={() => setFilter('open')}
            label="👁️ Opens"
          />
        </div>
      </div>

      {/* Events List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : events.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg mb-2">No webhook events yet</p>
            <p className="text-sm">Events will appear here once your webhooks are configured</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Event Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  From
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  To
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Subject
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Provider
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {events.map((event) => (
                <tr key={event.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(event.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <EventTypeBadge type={event.event_type} />
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{event.parsed_from}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{event.parsed_to}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{event.parsed_subject}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {event.provider}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function FilterButton({ active, onClick, label }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
        active
          ? 'bg-blue-600 text-white'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      }`}
    >
      {label}
    </button>
  );
}

function EventTypeBadge({ type }) {
  const colors = {
    reply: 'bg-green-100 text-green-800',
    bounce: 'bg-red-100 text-red-800',
    delivered: 'bg-blue-100 text-blue-800',
    spam: 'bg-yellow-100 text-yellow-800',
    open: 'bg-purple-100 text-purple-800',
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[type] || 'bg-gray-100 text-gray-800'}`}>
      {type}
    </span>
  );
}
