import { useState, useEffect } from 'react'

/**
 * Returns a debounced version of the value that only updates after `delay` ms.
 * Pattern from cc-skill-frontend-patterns — use for search inputs.
 *
 * @example
 * const [query, setQuery] = useState('')
 * const debouncedQuery = useDebounce(query, 400)
 * useEffect(() => { if (debouncedQuery) search(debouncedQuery) }, [debouncedQuery])
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}
