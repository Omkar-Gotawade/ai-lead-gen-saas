import api from './axios';

/**
 * Fetch all sequence steps for a campaign
 */
export const getSequenceSteps = async (campaignId) => {
  const response = await api.get(`/api/campaigns/${campaignId}/steps`);
  return response.data;
};

/**
 * Create a new sequence step
 */
export const createSequenceStep = async (stepData) => {
  const response = await api.post(`/api/campaigns/${stepData.campaign_id}/steps`, stepData);
  return response.data;
};

/**
 * Update an existing sequence step
 */
export const updateSequenceStep = async (stepId, stepData) => {
  const response = await api.put(`/api/sequence-steps/${stepId}`, stepData);
  return response.data;
};

/**
 * Delete a sequence step
 */
export const deleteSequenceStep = async (stepId) => {
  const response = await api.delete(`/api/sequence-steps/${stepId}`);
  return response.data;
};
