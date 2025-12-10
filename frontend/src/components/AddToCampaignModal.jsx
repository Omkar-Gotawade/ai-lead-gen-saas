import { useState, useEffect } from 'react';
import { getCampaigns, enqueueLeadsToCampaign } from '../api/campaigns';

function AddToCampaignModal({ isOpen, onClose, selectedLeadIds, onSuccess }) {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchCampaigns();
    }
  }, [isOpen]);

  const fetchCampaigns = async () => {
    try {
      const data = await getCampaigns();
      // Filter to only show active or draft campaigns
      const availableCampaigns = data.filter(c => c.status === 'active' || c.status === 'draft');
      setCampaigns(availableCampaigns);
    } catch (err) {
      console.error('Error fetching campaigns:', err);
      setError('Failed to load campaigns');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedCampaignId) {
      alert('Please select a campaign');
      return;
    }

    if (selectedLeadIds.length === 0) {
      alert('No leads selected');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const result = await enqueueLeadsToCampaign(selectedCampaignId, selectedLeadIds);
      
      alert(`Successfully added ${result.enqueued_count} lead(s) to campaign. ${result.skipped_count > 0 ? `${result.skipped_count} already enrolled.` : ''}`);
      
      setSelectedCampaignId('');
      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error adding leads to campaign:', err);
      setError(err.response?.data?.detail || 'Failed to add leads to campaign');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Add to Campaign
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-4">
              Selected leads: <strong>{selectedLeadIds.length}</strong>
            </p>

            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Campaign
            </label>
            
            {campaigns.length === 0 ? (
              <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
                <p className="text-sm">No campaigns available. Create a campaign first.</p>
              </div>
            ) : (
              <select
                value={selectedCampaignId}
                onChange={(e) => setSelectedCampaignId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Choose a campaign...</option>
                {campaigns.map((campaign) => (
                  <option key={campaign.id} value={campaign.id}>
                    {campaign.name} ({campaign.status})
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || campaigns.length === 0}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Adding...' : 'Add to Campaign'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddToCampaignModal;
