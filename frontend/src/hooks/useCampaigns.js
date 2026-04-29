import { useState, useEffect, useCallback } from 'react'
import {
  getCampaigns,
  createCampaign,
  deleteCampaign,
  activateCampaign,
  pauseCampaign,
} from '../api/campaigns'
import axios from '../api/axios'

/**
 * Encapsulates campaign list state, CRUD operations, and email/warmup checks.
 *
 * @returns campaign state + action handlers
 */
export function useCampaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hasEmailProvider, setHasEmailProvider] = useState(true)
  const [warmupStatus, setWarmupStatus] = useState(null)

  /* ── Data fetching ────────────────────────────────────────── */

  const fetchCampaigns = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getCampaigns()
      setCampaigns(data)
      setError(null)
    } catch (err) {
      setError('Failed to load campaigns')
    } finally {
      setLoading(false)
    }
  }, [])

  const checkEmailProvider = useCallback(async () => {
    try {
      const response = await axios.get('/api/email-provider/me')
      setHasEmailProvider(response.data !== null && response.data !== undefined)
    } catch {
      setHasEmailProvider(false)
    }
  }, [])

  const fetchWarmupStatus = useCallback(async () => {
    try {
      const response = await axios.get('/api/deliverability/warmup/status')
      setWarmupStatus(response.data)
    } catch {
      // warmup status is non-critical — silently ignore
    }
  }, [])

  useEffect(() => {
    fetchCampaigns()
    checkEmailProvider()
    fetchWarmupStatus()
  }, [fetchCampaigns, checkEmailProvider, fetchWarmupStatus])

  /* ── CRUD ─────────────────────────────────────────────────── */

  const createNewCampaign = useCallback(async (payload) => {
    await createCampaign({ ...payload, status: 'draft' })
    await fetchCampaigns()
  }, [fetchCampaigns])

  const removeCampaign = useCallback(async (campaignId) => {
    await deleteCampaign(campaignId)
    await fetchCampaigns()
  }, [fetchCampaigns])

  const toggleCampaignStatus = useCallback(async (campaign) => {
    if (campaign.status === 'active') {
      await pauseCampaign(campaign.id)
    } else {
      await activateCampaign(campaign.id)
    }
    await fetchCampaigns()
  }, [fetchCampaigns])

  return {
    // state
    campaigns,
    loading,
    error,
    hasEmailProvider,
    warmupStatus,
    // actions
    setError,
    fetchCampaigns,
    createNewCampaign,
    removeCampaign,
    toggleCampaignStatus,
  }
}
