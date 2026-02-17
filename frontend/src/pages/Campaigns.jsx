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
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Email Campaigns</h1>
        <p className="text-slate-500">Create and manage multi-step email sequences.</p>
      </div>

      {/* Email Provider Warning */}
      {!hasEmailProvider && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Email Provider Required</AlertTitle>
          <AlertDescription>
            You need to configure an email provider before creating campaigns.{' '}
            <Link to="/settings" className="font-medium underline">
              Go to Settings →
            </Link>
          </AlertDescription>
        </Alert>
      )}

      {/* Warmup Warning */}
      {warmupStatus && warmupStatus.warmup_day < 14 && warmupStatus.usage_percentage > 80 && (
        <Alert variant="warning">
          <Shield className="h-4 w-4" />
          <AlertTitle>Approaching Daily Limit</AlertTitle>
          <AlertDescription>
            You've sent {warmupStatus.used_today} of {warmupStatus.daily_limit} recommended emails today ({warmupStatus.usage_percentage}%).
            Consider pausing sends until tomorrow to protect your sender reputation.
          </AlertDescription>
        </Alert>
      )}

      {/* Warmup Info for New Users */}
      {warmupStatus && warmupStatus.warmup_day < 7 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Email Warmup in Progress (Day {warmupStatus.warmup_day}/21)</AlertTitle>
          <AlertDescription>
            Start slow to build sender reputation. Recommended limit today: {warmupStatus.daily_limit} emails.
            <Link to="/deliverability" className="ml-2 font-medium underline">
              View Deliverability Dashboard →
            </Link>
          </AlertDescription>
        </Alert>
      )}

      {/* Create Campaign Form */}
      <Card>
        <CardHeader>
          <CardTitle>Create New Campaign</CardTitle>
        </CardHeader>
        <form onSubmit={handleCreateCampaign}>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Campaign Name"
                placeholder="e.g., Q1 Outreach Campaign"
                value={newCampaign.name}
                onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                required
              />
              <Input
                label="Description"
                placeholder="Brief description of campaign goals"
                value={newCampaign.description}
                onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              type="submit" 
              isLoading={isCreating}
              disabled={isCreating || !hasEmailProvider}
              icon={<Plus className="w-4 h-4" />}
            >
              {isCreating ? 'Creating...' : 'Create Campaign'}
            </Button>
            {!hasEmailProvider && (
              <p className="text-sm text-slate-500 ml-4">
                Configure email provider in Settings first
              </p>
            )}
          </CardFooter>
        </form>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Campaigns List */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-12 flex justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : campaigns.length === 0 ? (
            <EmptyState
              icon={<Mail />}
              title="No campaigns yet"
              description="Create your first campaign to start sending personalized email sequences."
              actions={[
                { 
                  label: "Create Campaign", 
                  onClick: () => document.querySelector('input[placeholder*="Campaign Name"]')?.focus(),
                  variant: "primary",
                  icon: <Plus className="w-4 h-4" />,
                  disabled: !hasEmailProvider
                }
              ]}
              helpText="💡 Tip: Start with 5-10 highly relevant leads for your first campaign."
              warning={!hasEmailProvider ? "Email provider not configured - Go to Settings first" : null}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4 font-medium">Name</th>
                    <th className="px-6 py-4 font-medium">Description</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium">Control</th>
                    <th className="px-6 py-4 font-medium">Created</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {campaigns.map((campaign) => (
                    <tr key={campaign.id} className="bg-white hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900">
                        {campaign.name}
                      </td>
                      <td className="px-6 py-4 text-slate-600">
                        {campaign.description || <span className="text-slate-400">—</span>}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={getStatusVariant(campaign.status)} className="capitalize">
                          {campaign.status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        {campaign.status === 'draft' || campaign.status === 'paused' ? (
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-green-600 border-green-200 hover:bg-green-50 h-8"
                            onClick={() => handleToggleCampaignStatus(campaign)}
                            icon={<Play className="w-4 h-4" />}
                          >
                            Activate
                          </Button>
                        ) : campaign.status === 'active' ? (
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-yellow-600 border-yellow-200 hover:bg-yellow-50 h-8"
                            onClick={() => handleToggleCampaignStatus(campaign)}
                            icon={<Pause className="w-4 h-4" />}
                          >
                            Pause
                          </Button>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-slate-600">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-slate-400" />
                          {new Date(campaign.created_at).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleEditCampaign(campaign.id)}
                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                          >
                            Edit Sequence
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </Button>
                          <button
                            onClick={() => handleDeleteCampaign(campaign.id, campaign.name)}
                            className="p-2 text-slate-400 hover:text-red-600 transition-colors rounded-md hover:bg-red-50"
                            title="Delete Campaign"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
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

export default Campaigns;
