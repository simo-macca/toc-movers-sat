const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export async function solveProblem(payload) {
  try {
    const response = await fetch(`${API_BASE_URL}/solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `API Error: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('API call failed:', error)
    throw error
  }
}

export async function solveProblemFixed(payload) {
  try {
    const response = await fetch(`${API_BASE_URL}/solve/fixed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `API Error: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('API call failed:', error)
    throw error
  }
}

export async function fetchCNF(solveId) {
  const response = await fetch(`${API_BASE_URL}/cnf/${solveId}`)
  if (!response.ok) throw new Error('Failed to fetch CNF')
  return await response.json()
}

export async function fetchMapping(solveId) {
  const response = await fetch(`${API_BASE_URL}/mapping/${solveId}`)
  if (!response.ok) throw new Error('Failed to fetch Mapping')
  return await response.json()
}
