import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCampaigns, createCampaign, deleteCampaign, activateCampaign, pauseCampaign } from '../api/campaigns';

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
      alert('Campaign name is required');
      return;
    }

    try {
      setIsCreating(true);
      await createCampaign({
        name: newCampaign.name,
        description: newCampaign.description,
        status: 'draft'
      });
      
      setNewCampaign({ name: '', description: '' });
      await fetchCampaigns();
      alert('Campaign created successfully');
    } catch (err) {
      console.error('Error creating campaign:', err);
      alert('Failed to create campaign');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteCampaign = async (campaignId, campaignName) => {
    if (!confirm(`Are you sure you want to delete "${campaignName}"?`)) {
      return;
    }

    try {
      await deleteCampaign(campaignId);
      await fetchCampaigns();
      alert('Campaign deleted successfully');
    } catch (err) {
      console.error('Error deleting campaign:', err);
      alert('Failed to delete campaign');
    }
  };

  const handleEditCampaign = (campaignId) => {
    navigate(`/campaigns/${campaignId}`);
  };

  const handleToggleCampaignStatus = async (campaign) => {
    try {
      if (campaign.status === 'active') {
        await pauseCampaign(campaign.id);
        alert('Campaign paused successfully');
      } else {
        await activateCampaign(campaign.id);
        alert('Campaign activated successfully');
      }
      await fetchCampaigns();
    } catch (err) {
      console.error('Error updating campaign status:', err);
      alert('Failed to update campaign status');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Email Campaigns</h1>
        <p className="text-gray-600">Create and manage multi-step email sequences</p>
      </div>

        {/* Create Campaign Form */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Create New Campaign</h2>
          <form onSubmit={handleCreateCampaign} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Campaign Name *
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Q1 Outreach Campaign"
                  value={newCampaign.name}
                  onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of campaign goals"
                  value={newCampaign.description}
                  onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
                />
              </div>
            </div>
            <div>
              <button
                type="submit"
                disabled={isCreating}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isCreating ? 'Creating...' : 'Create Campaign'}
              </button>
            </div>
          </form>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Campaigns List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading campaigns...</p>
          </div>
        ) : campaigns.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
            <p className="text-gray-600">Create your first campaign to get started with automated email sequences</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campaign Control
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {campaigns.map((campaign) => (
                  <tr key={campaign.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{campaign.name}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-600">{campaign.description || '—'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(campaign.status)}`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {campaign.status === 'draft' || campaign.status === 'paused' ? (
                        <button
                          onClick={() => handleToggleCampaignStatus(campaign)}
                          className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 font-medium"
                          title="Activate Campaign"
                        >
                          Activate
                        </button>
                      ) : campaign.status === 'active' ? (
                        <button
                          onClick={() => handleToggleCampaignStatus(campaign)}
                          className="px-3 py-1 bg-yellow-600 text-white text-xs rounded hover:bg-yellow-700 font-medium"
                          title="Pause Campaign"
                        >
                          Pause
                        </button>
                      ) : (
                        <span className="text-sm text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleEditCampaign(campaign.id)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        Edit Sequence
                      </button>
                      <button
                        onClick={() => handleDeleteCampaign(campaign.id, campaign.name)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
    </div>
  );
}

export default Campaigns;
