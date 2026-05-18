const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const DEFAULT_TIMEOUT = 30000 // 30 seconds

export async function solveProblem(payload, timeout = DEFAULT_TIMEOUT) {
  try {
    const response = await fetch(`${API_BASE_URL}/solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(timeout),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `API Error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    if (error.name === 'TimeoutError' || error.name === 'AbortError') {
      throw new Error(`The solver timed out after ${timeout / 1000} seconds. Try reducing the problem complexity.`)
    }

    console.error('API call failed:', error)
    throw error
  }
}

export async function solveProblemFixed(payload, timeout = DEFAULT_TIMEOUT) {
  try {
    const response = await fetch(`${API_BASE_URL}/solve/fixed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(timeout),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `API Error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    if (error.name === 'TimeoutError' || error.name === 'AbortError') {
      throw new Error(`The solver timed out after ${timeout / 1000} seconds. Try reducing the problem complexity.`)
    }

    console.error('API call failed:', error)
    throw error
  }
}

export async function fetchCNF(solveId, timeout = 10000) {
  try {
    const response = await fetch(`${API_BASE_URL}/cnf/${solveId}`, {
      signal: AbortSignal.timeout(timeout),
    })

    if (!response.ok) throw new Error('Failed to fetch CNF')
    return await response.json()
  } catch (error) {
    if (error.name === 'TimeoutError' || error.name === 'AbortError') throw new Error('Download timed out')
    console.error('Download CNF failed:', error)
    throw error
  }
}

export async function fetchMapping(solveId, timeout = 10000) {
  try {
    const response = await fetch(`${API_BASE_URL}/mapping/${solveId}`, {
      signal: AbortSignal.timeout(timeout),
    })
    if (!response.ok) throw new Error('Failed to fetch Mapping')

    return await response.json()
  } catch (error) {
    if (error.name === 'TimeoutError' || error.name === 'AbortError') throw new Error('Download timed out')

    console.error('Download Mapping JSON failed:', error)
    throw error
  }
}
