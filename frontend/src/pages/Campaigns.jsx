import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Plus, 
  Play, 
  Pause, 
  Edit, 
  Trash2, 
  Calendar, 
  Mail, 
  ArrowRight,
  MoreHorizontal,
  AlertTriangle,
  Info,
  Shield
} from 'lucide-react';
import { getCampaigns, createCampaign, deleteCampaign, activateCampaign, pauseCampaign } from '../api/campaigns';
import axios from '../api/axios';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/Alert';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import EmptyState from '../components/ui/EmptyState';

function Campaigns() {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [hasEmailProvider, setHasEmailProvider] = useState(true);
  const [warmupStatus, setWarmupStatus] = useState(null);
  
  // Form state for creating new campaign
  const [newCampaign, setNewCampaign] = useState({
    name: '',
    description: ''
  });

  useEffect(() => {
    fetchCampaigns();
    checkEmailProvider();
    fetchWarmupStatus();
  }, []);

  const checkEmailProvider = async () => {
    try {
      const response = await axios.get('/api/email-provider/me');
      // Backend returns null if no provider, or an object with configured=true if provider exists
      const hasProvider = response.data !== null && response.data !== undefined;
      setHasEmailProvider(hasProvider);
      console.log('Email provider check:', { hasProvider, data: response.data });
    } catch (err) {
      console.error('Error checking email provider:', err);
      setHasEmailProvider(false);
    }
  };

  const fetchWarmupStatus = async () => {
    try {
      const response = await axios.get('/api/deliverability/warmup/status');
      setWarmupStatus(response.data);
    } catch (err) {
      console.error('Error fetching warmup status:', err);
    }
  };

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const data = await getCampaigns();
      setCampaigns(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching campaigns:', err);
      setError('Failed to load campaigns');
    } finally {
      setLoading(false);
    }
  };

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

    if (isCreating) return; // Prevent double-submit

    try {
      setIsCreating(true);
      setError(null);
      await createCampaign({
        name: newCampaign.name,
        description: newCampaign.description,
        status: 'draft'
      });
      
      setNewCampaign({ name: '', description: '' });
      await fetchCampaigns();
    } catch (err) {
      console.error('Error creating campaign:', err);
      setError(err.response?.data?.detail || 'Failed to create campaign');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteCampaign = async (campaignId, campaignName) => {
    const confirmMessage = `Delete "${campaignName}" campaign? This cannot be undone.`;
    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      await deleteCampaign(campaignId);
      await fetchCampaigns();
    } catch (err) {
      console.error('Error deleting campaign:', err);
      setError(err.response?.data?.detail || 'Failed to delete campaign');
    }
  };

  const handleEditCampaign = (campaignId) => {
    navigate(`/campaigns/${campaignId}`);
  };

  const handleToggleCampaignStatus = async (campaign) => {
    const isActivating = campaign.status !== 'active';
    
    if (isActivating) {
      // Show confirmation with warmup info
      const confirmMessage = warmupStatus 
        ? `Activate "${campaign.name}"?\n\nWarmup Day ${warmupStatus.warmup_day}/21\nDaily Limit: ${warmupStatus.daily_limit} emails\nUsed Today: ${warmupStatus.used_today}/${warmupStatus.daily_limit}`
        : `Activate "${campaign.name}"?`;
      
      if (!window.confirm(confirmMessage)) {
        return;
      }
    }

    try {
      if (campaign.status === 'active') {
        await pauseCampaign(campaign.id);
      } else {
        await activateCampaign(campaign.id);
      }
      await fetchCampaigns();
    } catch (err) {
      console.error('Error updating campaign status:', err);
      setError(err.response?.data?.detail || 'Failed to update campaign status');
    }
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'paused':
        return 'warning';
      case 'draft':
        return 'secondary';
      case 'completed':
        return 'default';
      default:
        return 'secondary';
    }
  };

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

      {/* Create form */}
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
          <CardFooter className="gap-3 border-t border-ink-50 mt-0 pt-4">
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

      {/* Campaigns table */}
      <Card className="overflow-hidden">
        {loading ? (
          <LoadingSpinner size="md" text="Loading campaigns…" />
        ) : campaigns.length === 0 ? (
          <div className="py-16 flex flex-col items-center gap-3 text-center">
            <div className="w-12 h-12 rounded-full bg-ink-100 flex items-center justify-center">
              <Mail className="w-5 h-5 text-ink-400" />
            </div>
            <div>
              <p className="font-semibold text-ink-700">No campaigns yet</p>
              <p className="text-sm text-ink-400 mt-0.5">Create your first campaign above to get started</p>
            </div>
          </div>
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
                    <td className="font-medium text-ink-800">{campaign.name}</td>
                    <td className="text-ink-500 max-w-xs truncate">
                      {campaign.description || <span className="text-ink-300">—</span>}
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
                          onClick={() => handleToggleCampaignStatus(campaign)}
                          icon={<Play className="w-3 h-3" />}
                          className="border-success/30 text-emerald-700 hover:bg-success/8"
                        >
                          Activate
                        </Button>
                      ) : campaign.status === 'active' ? (
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={() => handleToggleCampaignStatus(campaign)}
                          icon={<Pause className="w-3 h-3" />}
                          className="border-warning/30 text-amber-700 hover:bg-warning/8"
                        >
                          Pause
                        </Button>
                      ) : (
                        <span className="text-ink-300 text-xs">—</span>
                      )}
                    </td>
                    <td className="text-ink-500 text-xs">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </td>
                    <td className="text-right pr-4">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          size="xs"
                          variant="ghost"
                          onClick={() => handleEditCampaign(campaign.id)}
                          className="text-brand-600 hover:bg-brand-50"
                        >
                          Edit
                          <ArrowRight className="w-3 h-3 ml-1" />
                        </Button>
                        <button
                          onClick={() => handleDeleteCampaign(campaign.id, campaign.name)}
                          className="p-1.5 rounded-md text-ink-400 hover:text-danger hover:bg-danger/8 transition-colors"
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
    </div>
  );
}

export default Campaigns;

