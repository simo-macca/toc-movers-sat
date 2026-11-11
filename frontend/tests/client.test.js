import { afterEach, describe, expect, it, vi } from 'vitest'
import { formatErrorDetail, request, SOLVE_TIMEOUT_MS } from '../src/api/client'

describe('formatErrorDetail', () => {
  it('formats FastAPI 422 validation errors', () => {
    const detail = [{ loc: ['body', 'items', 0, 'initial_floor'], msg: 'Value error, out of range' }]
    expect(formatErrorDetail(detail, 422)).toBe('items.0.initial_floor: out of range')
  })

  it('passes string details through and falls back to the status', () => {
    expect(formatErrorDetail('Solver timeout', 504)).toBe('Solver timeout')
    expect(formatErrorDetail(undefined, 500)).toBe('API Error: 500')
  })
})

describe('request', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('uses a 2 minute solve timeout', () => {
    expect(SOLVE_TIMEOUT_MS).toBe(120000)
  })

  it('throws a readable error for non-OK responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 404, json: async () => ({ detail: 'Solve ID not found' }) }),
    )
    vi.spyOn(console, 'error').mockImplementation(() => {})
    await expect(request('/cnf/x')).rejects.toThrow('Solve ID not found')
  })

  it('returns parsed JSON on success', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ status: 'ok' }) }))
    await expect(request('/health')).resolves.toEqual({ status: 'ok' })
  })
})
