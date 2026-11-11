/**
 * Convert the UI form state into the request body expected by the backend.
 *
 * - Task 1 sends `goal_floors` as `{ personIndex: floor }` and no items.
 * - Task 2 sends `items` and no goal floors.
 * - Optimal mode sends `max_steps`; fixed mode sends `time_steps`.
 */
export function buildPayload(form) {
  const isTask1 = form.task === 1

  const payload = {
    task: form.task,
    num_floors: form.num_floors,
    num_persons: form.num_persons,
    person_names: form.person_names,
    items: isTask1 ? [] : form.items,
    goal_floors: isTask1 ? Object.fromEntries(form.goal_floors.map((floor, idx) => [idx, floor])) : null,
  }

  if (form.solve_mode === 'optimal') payload.max_steps = form.max_steps
  else payload.time_steps = form.time_steps

  return payload
}
