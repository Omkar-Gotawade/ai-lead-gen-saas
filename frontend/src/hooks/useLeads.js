import { useState, useEffect, useCallback } from 'react'
import { leadsAPI } from '../api'
import { getEmailProvider } from '../api/email'

/**
 * Encapsulates lead list state, pagination, and CRUD operations.
 *
 * @param {number} [initialPage=1]
 * @param {number} [pageSize=50]
 * @returns lead state + action handlers
 */
export function useLeads(initialPage = 1, pageSize = 50) {
  const [leads, setLeads] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(initialPage)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [emailProviderConfigured, setEmailProviderConfigured] = useState(false)
  const [enrichingLeads, setEnrichingLeads] = useState(new Set())

  const fetchLeads = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const response = await leadsAPI.getLeads(page, pageSize)
      setLeads(response.data.leads)
      setTotal(response.data.total)
    } catch {
      setError('Failed to fetch leads')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize])

  const checkEmailProvider = useCallback(async () => {
    try {
      await getEmailProvider()
      setEmailProviderConfigured(true)
    } catch {
      setEmailProviderConfigured(false)
    }
  }, [])

  useEffect(() => {
    fetchLeads()
    checkEmailProvider()
  }, [fetchLeads, checkEmailProvider])

  /* ── CRUD ─────────────────────────────────────────────────── */

  const createLead = useCallback(async (data) => {
    await leadsAPI.createLead(data)
    await fetchLeads()
  }, [fetchLeads])

  const updateLead = useCallback(async (id, data) => {
    await leadsAPI.updateLead(id, data)
    await fetchLeads()
  }, [fetchLeads])

  const deleteLead = useCallback(async (id) => {
    await leadsAPI.deleteLead(id)
    await fetchLeads()
  }, [fetchLeads])

  const uploadCSV = useCallback(async (file) => {
    await leadsAPI.uploadCSV(file)
    await fetchLeads()
  }, [fetchLeads])

  const enrichLead = useCallback(async (leadId) => {
    setEnrichingLeads((prev) => new Set(prev).add(leadId))
    try {
      await leadsAPI.enrichLead(leadId)
      setTimeout(() => {
        fetchLeads()
        setEnrichingLeads((prev) => {
          const next = new Set(prev)
          next.delete(leadId)
          return next
        })
      }, 3000)
    } catch (err) {
      setEnrichingLeads((prev) => {
        const next = new Set(prev)
        next.delete(leadId)
        return next
      })
      throw err
    }
  }, [fetchLeads])

  /* ── Pagination ───────────────────────────────────────────── */

  const totalPages = Math.ceil(total / pageSize)
  const canGoPrev = page > 1
  const canGoNext = page < totalPages

  return {
    // state
    leads,
    total,
    page,
    pageSize,
    loading,
    error,
    emailProviderConfigured,
    enrichingLeads,
    totalPages,
    canGoPrev,
    canGoNext,
    // actions
    setPage,
    fetchLeads,
    createLead,
    updateLead,
    deleteLead,
    uploadCSV,
    enrichLead,
  }
}
