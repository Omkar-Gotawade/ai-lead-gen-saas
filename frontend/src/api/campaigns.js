import api from './axios';

/**
 * Fetch all campaigns for the current user
 */
export const getCampaigns = async () => {
  const response = await api.get('/api/campaigns');
  return response.data;
};

/**
 * Create a new campaign
 */
export const createCampaign = async (campaignData) => {
  const response = await api.post('/api/campaigns', campaignData);
  return response.data;
};

/**
 * Get a single campaign by ID
 */
export const getCampaign = async (campaignId) => {
  const response = await api.get(`/api/campaigns/${campaignId}`);
  return response.data;
};

/**
 * Update an existing campaign
 */
export const updateCampaign = async (campaignId, campaignData) => {
  const response = await api.put(`/api/campaigns/${campaignId}`, campaignData);
  return response.data;
};

/**
 * Delete a campaign
 */
export const deleteCampaign = async (campaignId) => {
  const response = await api.delete(`/api/campaigns/${campaignId}`);
  return response.data;
};

/**
 * Enqueue leads to a campaign
 */
export const enqueueLeadsToCampaign = async (campaignId, leadIds) => {
  const response = await api.post(`/api/${campaignId}/enqueue`, {
    lead_ids: leadIds
  });
  return response.data;
};
