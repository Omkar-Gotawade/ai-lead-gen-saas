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
 * Generate AI Sequence (creates campaign + steps)
 */
export const generateAISequence = async (payload) => {
  const response = await api.post('/api/campaigns/generate-sequence', payload);
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

/**
 * Activate a campaign - sets status to active and schedules all pending leads
 */
export const activateCampaign = async (campaignId) => {
  const response = await api.post(`/api/${campaignId}/activate`);
  return response.data;
};

/**
 * Pause a campaign - sets status to paused
 */
export const pauseCampaign = async (campaignId) => {
  const response = await api.post(`/api/${campaignId}/pause`);
  return response.data;
};

/**
 * Get enrolled leads for a campaign
 */
export const getCampaignLeads = async (campaignId) => {
  const response = await api.get(`/api/campaigns/${campaignId}/leads`);
  return response.data;
};
