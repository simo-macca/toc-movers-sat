const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// 2 minutes. The backend aborts the solver after 118 s, so its 504 arrives first.
export const SOLVE_TIMEOUT_MS = 120000
export const DOWNLOAD_TIMEOUT_MS = 10000

/**
 * Turn a FastAPI error body into a readable message.
 * Validation errors (422) arrive as `detail: [{ loc, msg }, ...]`.
 */
export function formatErrorDetail(detail, status) {
  if (Array.isArray(detail)) {
    return detail
      .map((e) => {
        const field = (e.loc || []).filter((p) => p !== 'body').join('.')
        const msg = String(e.msg || '').replace(/^Value error, /, '')
        return field ? `${field}: ${msg}` : msg
      })
      .join('\n')
  }
  if (typeof detail === 'string' && detail) return detail
  return `API Error: ${status}`
}

/**
 * Shared fetch wrapper: JSON body, timeout, and error normalisation.
 */
export async function request(path, { method = 'GET', body, timeout = DOWNLOAD_TIMEOUT_MS } = {}) {
  try {
    const options = { method, signal: AbortSignal.timeout(timeout) }
    if (body !== undefined) {
      options.headers = { 'Content-Type': 'application/json' }
      options.body = JSON.stringify(body)
    }
    const response = await fetch(`${API_BASE_URL}${path}`, options)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(formatErrorDetail(errorData.detail, response.status))
    }

    return await response.json()
  } catch (error) {
    if (error.name === 'TimeoutError' || error.name === 'AbortError') {
      throw new Error(`Request timed out after ${timeout / 1000} seconds. Try reducing the problem complexity.`, {
        cause: error,
      })
    }
    console.error(`API call ${method} ${path} failed:`, error)
    throw error
  }
}

export const solveProblem = (payload, timeout = SOLVE_TIMEOUT_MS) =>
  request('/solve', { method: 'POST', body: payload, timeout })

export const solveProblemFixed = (payload, timeout = SOLVE_TIMEOUT_MS) =>
  request('/solve/fixed', { method: 'POST', body: payload, timeout })

export const fetchCNF = (solveId, timeout = DOWNLOAD_TIMEOUT_MS) => request(`/cnf/${solveId}`, { timeout })

export const fetchMapping = (solveId, timeout = DOWNLOAD_TIMEOUT_MS) => request(`/mapping/${solveId}`, { timeout })
