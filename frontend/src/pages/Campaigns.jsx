import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Plus,
  Play,
  Pause,
  Trash2,
  Calendar,
  Mail,
  ArrowRight,
} from 'lucide-react';

import { useCampaigns } from '../hooks/useCampaigns';
import { useToast } from '../context/ToastContext';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/Alert';
import EmptyState from '../components/ui/EmptyState';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import AISequenceBuilder from '../components/AISequenceBuilder';
import { Sparkles, PenTool } from 'lucide-react';

function Campaigns() {
  const navigate = useNavigate();
  const toast = useToast();
  const {
    campaigns,
    loading,
    error,
    hasEmailProvider,
    warmupStatus,
    setError,
    createNewCampaign,
    removeCampaign,
    toggleCampaignStatus,
  } = useCampaigns();

  /* ── Create form state ────────────────────────────────────── */
  const [newCampaign, setNewCampaign] = useState({ name: '', description: '' });
  const [isCreating, setIsCreating] = useState(false);
  const [showManualBuilder, setShowManualBuilder] = useState(false);
  const [showAiBuilder, setShowAiBuilder] = useState(false);

  /* ── Confirm delete dialog state ──────────────────────────── */
  const [pendingDelete, setPendingDelete] = useState(null); // { id, name }
  const [isDeleting, setIsDeleting] = useState(false);

  /* ── Handlers ─────────────────────────────────────────────── */
  const handleCreateCampaign = async (e) => {
    e.preventDefault();

    if (!hasEmailProvider) {
      setError('Email provider must be configured before creating campaigns');
      return;
    }
    if (!newCampaign.name.trim()) {
      setError('Campaign name is required');
      return;
    }
    if (newCampaign.name.trim().length < 3) {
      setError('Campaign name must be at least 3 characters');
      return;
    }
    if (isCreating) return;

    try {
      setIsCreating(true);
      setError(null);
      await createNewCampaign(newCampaign);
      setNewCampaign({ name: '', description: '' });
      toast.success('Campaign created.', 'Success');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create campaign');
    } finally {
      setIsCreating(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!pendingDelete) return;
    setIsDeleting(true);
    try {
      await removeCampaign(pendingDelete.id);
      toast.success(`"${pendingDelete.name}" deleted.`);
      setPendingDelete(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete campaign');
      setPendingDelete(null);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleToggleStatus = async (campaign) => {
    try {
      await toggleCampaignStatus(campaign);
      const action = campaign.status === 'active' ? 'paused' : 'activated';
      toast.success(`Campaign ${action}.`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update campaign status');
    }
  };

  /* ── Render ───────────────────────────────────────────────── */
  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="page-title">Campaigns</h1>
          <p className="page-subtitle mt-0.5">Create and manage multi-step email sequences</p>
        </div>
      </div>

      {/* Alerts */}
      {!hasEmailProvider && (
        <Alert variant="destructive">
          <AlertTitle>Email provider required</AlertTitle>
          <AlertDescription>
            Configure your SMTP or email provider in{' '}
            <Link to="/settings" className="font-semibold underline">Settings</Link>{' '}
            before creating campaigns.
          </AlertDescription>
        </Alert>
      )}
      {warmupStatus && warmupStatus.warmup_day < 14 && warmupStatus.usage_percentage > 80 && (
        <Alert variant="warning">
          <AlertTitle>Approaching daily limit</AlertTitle>
          <AlertDescription>
            {warmupStatus.used_today}/{warmupStatus.daily_limit} emails sent today ({warmupStatus.usage_percentage}%).
            Pause sends to protect sender reputation.
          </AlertDescription>
        </Alert>
      )}
      {warmupStatus && warmupStatus.warmup_day < 7 && (
        <Alert variant="info">
          <AlertTitle>Warmup in progress — Day {warmupStatus.warmup_day}/21</AlertTitle>
          <AlertDescription>
            Recommended limit: <strong>{warmupStatus.daily_limit}</strong> emails today.{' '}
            <Link to="/deliverability" className="font-semibold underline">View Deliverability →</Link>
          </AlertDescription>
        </Alert>
      )}

      {/* Create Campaign */}
      <Card>
        <CardHeader>
          <CardTitle>New Campaign</CardTitle>
        </CardHeader>
        <form onSubmit={handleCreateCampaign}>
          <CardContent className="pt-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Campaign Name"
                placeholder="e.g., Q1 Outreach"
                value={newCampaign.name}
                onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                required
              />
              <Input
                label="Description (optional)"
                placeholder="Brief description of campaign goals"
                value={newCampaign.description}
                onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
              />
            </div>
          </CardContent>
          <CardFooter className="gap-3 mt-0 pt-4" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
            <Button
              type="submit"
              size="sm"
              loading={isCreating}
              disabled={isCreating || !hasEmailProvider}
              icon={<Plus className="w-3.5 h-3.5" />}
            >
              {isCreating ? 'Creating…' : 'Create Campaign'}
            </Button>
            {!hasEmailProvider && (
              <p className="text-xs text-ink-400">Configure email provider in Settings first</p>
            )}
          </CardFooter>
        </form>
      </Card>

      {/* Error */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Campaigns table / empty state */}
      <Card className="overflow-hidden">
        {loading ? (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th><th>Description</th>
                  <th>Status</th><th>Control</th>
                  <th>Created</th><th className="text-right pr-5">Actions</th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i} className="border-b border-ink-50">
                    <td className="px-4 py-3"><div className="skeleton h-4 w-32 rounded" /></td>
                    <td className="px-4 py-3"><div className="skeleton h-4 w-48 rounded" /></td>
                    <td className="px-4 py-3"><div className="skeleton h-5 w-16 rounded-full" /></td>
                    <td className="px-4 py-3"><div className="skeleton h-8 w-20 rounded-lg" /></td>
                    <td className="px-4 py-3"><div className="skeleton h-4 w-24 rounded" /></td>
                    <td className="px-4 py-3 text-right pr-4"><div className="skeleton h-4 w-20 rounded ml-auto" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : campaigns.length === 0 ? (
          <EmptyState
            icon={<Mail />}
            title="No campaigns yet"
            description="Create your first email campaign above to start reaching your leads."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th>Control</th>
                  <th>Created</th>
                  <th className="text-right pr-5">Actions</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map((campaign) => (
                  <tr key={campaign.id}>
                    <td className="font-medium" style={{ color: '#e8eaf5' }}>{campaign.name}</td>
                    <td className="max-w-xs truncate" style={{ color: '#4a5168' }}>
                      {campaign.description || <span style={{ color: '#252840' }}>—</span>}
                    </td>
                    <td>
                      <Badge
                        variant={
                          campaign.status === 'active' ? 'success'
                            : campaign.status === 'paused' ? 'warning'
                            : campaign.status === 'completed' ? 'info'
                            : 'default'
                        }
                        dot
                        size="xs"
                        className="capitalize"
                      >
                        {campaign.status}
                      </Badge>
                    </td>
                    <td>
                      {campaign.status === 'draft' || campaign.status === 'paused' ? (
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={() => handleToggleStatus(campaign)}
                          icon={<Play className="w-3 h-3" />}
                        >
                          Activate
                        </Button>
                      ) : campaign.status === 'active' ? (
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={() => handleToggleStatus(campaign)}
                          icon={<Pause className="w-3 h-3" />}
                        >
                          Pause
                        </Button>
                      ) : (
                        <span className="text-xs" style={{ color: '#252840' }}>—</span>
                      )}
                    </td>
                    <td className="text-xs" style={{ color: '#4a5168' }}>
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </td>
                    <td className="text-right pr-4">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          size="xs"
                          variant="ghost"
                          onClick={() => navigate(`/campaigns/${campaign.id}`)}
                          style={{ color: '#f59e0b' }}
                        >
                          Edit
                          <ArrowRight className="w-3 h-3 ml-1" />
                        </Button>
                        <button
                          onClick={() => setPendingDelete({ id: campaign.id, name: campaign.name })}
                          className="p-1.5 rounded-md transition-colors"
                          style={{ color: '#343a52' }}
                          onMouseEnter={e => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = 'rgba(239,68,68,0.08)'; }}
                          onMouseLeave={e => { e.currentTarget.style.color = '#343a52'; e.currentTarget.style.background = 'transparent'; }}
                          title="Delete"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Confirm delete dialog */}
      <ConfirmDialog
        isOpen={!!pendingDelete}
        onConfirm={handleConfirmDelete}
        onCancel={() => setPendingDelete(null)}
        title="Delete Campaign"
        message={`Are you sure you want to delete "${pendingDelete?.name}"? This cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        loading={isDeleting}
      />
    </div>
  );
}

export default Campaigns;
