import { describe, expect, it } from 'vitest'
import { buildPayload } from '../src/utils/payload'

const base = {
  num_floors: 3,
  num_persons: 2,
  person_names: ['Joe', 'Mia'],
  items: [{ name: 'chair', initial_floor: 2 }],
  goal_floors: [2, 1],
  max_steps: 20,
  time_steps: 5,
}

describe('buildPayload', () => {
  it('task 1 sends goal floors keyed by person index and no items', () => {
    const p = buildPayload({ ...base, task: 1, solve_mode: 'optimal' })
    expect(p.items).toEqual([])
    expect(p.goal_floors).toEqual({ 0: 2, 1: 1 })
    expect(p.max_steps).toBe(20)
    expect(p).not.toHaveProperty('time_steps')
  })

  it('task 2 sends items and no goal floors', () => {
    const p = buildPayload({ ...base, task: 2, solve_mode: 'fixed' })
    expect(p.items).toHaveLength(1)
    expect(p.goal_floors).toBeNull()
    expect(p.time_steps).toBe(5)
    expect(p).not.toHaveProperty('max_steps')
  })
})
