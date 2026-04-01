import { useState, useCallback } from 'react'

interface UseApiOptions {
  onSuccess?: (data: any) => void
  onError?: (error: string) => void
}

export function useApi<T = any>(options?: UseApiOptions) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const request = useCallback(
    async (method: string, endpoint: string, body?: any) => {
      setLoading(true)
      setError(null)

      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(`/api${endpoint}`, {
          method,
          headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
          },
          body: body ? JSON.stringify(body) : undefined,
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || `HTTP ${response.status}`)
        }

        const result = await response.json()
        setData(result)
        options?.onSuccess?.(result)
        return result
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        setError(message)
        options?.onError?.(message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [options]
  )

  return { data, loading, error, request }
}

export function useGet<T = any>(endpoint: string, options?: UseApiOptions) {
  const api = useApi<T>(options)
  const [fetched, setFetched] = useState(false)

  const fetch = useCallback(async () => {
    if (!fetched) {
      await api.request('GET', endpoint)
      setFetched(true)
    }
  }, [api, endpoint, fetched])

  return { ...api, fetch }
}
