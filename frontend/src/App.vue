<script setup>
import { ref } from 'vue'
import { solveProblem, solveProblemFixed } from './api/client'
import ProblemSetup from './components/ProblemSetup.vue'
import ResultsPanel from './components/ResultsPanel.vue'

// global state
const isLoading = ref(false)
const error = ref(null)
const solveResponse = ref(null)

// initial form state
const form = ref({
  task: 2,
  num_floors: 4,
  num_persons: 2,
  person_names: ['Alice', 'Bob'],
  items: [
    { name: 'Sofa', initial_floor: 3 },
    { name: 'Desk', initial_floor: 2 },
  ],
  goal_floors: [0, 0],
  solve_mode: 'optimal',
  max_steps: 20,
  time_steps: 5,
})

const submitSolve = async () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })

  isLoading.value = true
  error.value = null
  solveResponse.value = null

  try {
    const goalFloorsDict = {}

    form.value.goal_floors.forEach((targetFloor, personIndex) => {
      goalFloorsDict[personIndex] = targetFloor
    })

    const payload = {
      task: form.value.task,
      num_floors: form.value.num_floors,
      num_persons: form.value.num_persons,
      person_names: form.value.person_names,
      // task 2 uses items, task 1 ignores them
      items: form.value.task === 2 ? form.value.items : [],
      // task 1 uses goal floors, task 2 ignores them
      goal_floors: form.value.task === 1 ? goalFloorsDict : null,
    }

    if (form.value.solve_mode === 'optimal') {
      payload.max_steps = form.value.max_steps
      solveResponse.value = await solveProblem(payload)
    } else {
      payload.time_steps = form.value.time_steps
      solveResponse.value = await solveProblemFixed(payload)
    }
  } catch (err) {
    error.value = err.message || 'Failed to connect to backend.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div
    class="min-h-screen bg-slate-50 p-4 font-sans text-slate-800 transition-colors duration-300 md:p-8 dark:bg-slate-950 dark:text-slate-100"
  >
    <div class="mx-auto">
      <!-- title -->
      <header
        class="mb-8 flex items-end justify-between border-b border-slate-200 pb-4 transition-colors duration-300 dark:border-slate-800"
      >
        <div>
          <h1 class="text-4xl font-extrabold tracking-tight text-slate-800 dark:text-white">Movers SAT Solver</h1>
          <p class="mt-2 text-lg text-slate-500 dark:text-slate-400">Optimal logistics planning using Glucose3</p>
        </div>
      </header>

      <!-- dynamic container -->
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-12">
        <!-- setup configuration -->
        <div class="lg:col-span-3">
          <ProblemSetup v-model:form="form" :isLoading="isLoading" @submit="submitSolve" />
        </div>

        <!-- animation container -->
        <div class="lg:col-span-9">
          <ResultsPanel :solveResponse="solveResponse" :isLoading="isLoading" :error="error" :form="form" />
        </div>
      </div>
    </div>
  </div>
</template>
