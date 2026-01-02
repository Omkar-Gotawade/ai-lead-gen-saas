import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Play, 
  Pause, 
  Edit, 
  Trash2, 
  Calendar, 
  Mail, 
  ArrowRight,
  MoreHorizontal
} from 'lucide-react';
import { getCampaigns, createCampaign, deleteCampaign, activateCampaign, pauseCampaign } from '../api/campaigns';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Alert, AlertDescription } from '../components/ui/Alert';
import LoadingSpinner from '../components/ui/LoadingSpinner';

function Campaigns() {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  
  // Form state for creating new campaign
  const [newCampaign, setNewCampaign] = useState({
    name: '',
    description: ''
  });

  useEffect(() => {
    fetchCampaigns();
  }, []);

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
    
    if (!newCampaign.name.trim()) {
      setError('Campaign name is required');
      return;
    }

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
      setError('Failed to create campaign');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteCampaign = async (campaignId, campaignName) => {
    if (!window.confirm(`Are you sure you want to delete "${campaignName}"?`)) {
      return;
    }

    try {
      await deleteCampaign(campaignId);
      await fetchCampaigns();
    } catch (err) {
      console.error('Error deleting campaign:', err);
      setError('Failed to delete campaign');
    }
  };

  const handleEditCampaign = (campaignId) => {
    navigate(`/campaigns/${campaignId}`);
  };

  const handleToggleCampaignStatus = async (campaign) => {
    try {
      if (campaign.status === 'active') {
        await pauseCampaign(campaign.id);
      } else {
        await activateCampaign(campaign.id);
      }
      await fetchCampaigns();
    } catch (err) {
      console.error('Error updating campaign status:', err);
      setError('Failed to update campaign status');
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
              icon={<Plus className="w-4 h-4" />}
            >
              Create Campaign
            </Button>
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
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 mb-4">
                <Mail className="w-6 h-6 text-slate-400" />
              </div>
              <h3 className="text-lg font-medium text-slate-900 mb-2">No campaigns yet</h3>
              <p className="text-slate-500 mb-6">Create your first campaign to get started with automated email sequences.</p>
            </div>
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
