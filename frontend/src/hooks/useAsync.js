import { useState, useCallback } from 'react'

/**
 * Custom hook that wraps async operations with unified loading/error state.
 * Follows the Async Data Fetching Hook pattern from cc-skill-frontend-patterns.
 *
 * @example
 * const { loading, error, execute } = useAsync()
 * const data = await execute(() => leadsAPI.getLeads(page, pageSize), {
 *   onSuccess: (result) => setLeads(result.data.leads),
 *   onError:   (err)    => console.error(err),
 * })
 */
export function useAsync() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(async (asyncFn, { onSuccess, onError } = {}) => {
    setLoading(true)
    setError(null)
    try {
      const result = await asyncFn()
      onSuccess?.(result)
      return result
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        (Array.isArray(err?.response?.data?.detail)
          ? err.response.data.detail.map((e) => e.msg || e).join(', ')
          : null) ||
        err?.message ||
        'An unexpected error occurred'
      setError(message)
      onError?.(err, message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const reset = useCallback(() => setError(null), [])

  return { loading, error, execute, reset }
}
