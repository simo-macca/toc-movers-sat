<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'
import { fetchCNF, fetchMapping } from '../api/client'
import BuildingVisualizer from './BuildingVisualizer.vue'
import ActionLog from './ActionLog.vue'

const props = defineProps({
  solveResponse: Object,
  isLoading: Boolean,
  error: String,
  form: Object,
})

// visualizer state
const currentStep = ref(0)
const isPlaying = ref(false)
let playInterval = null

watch(
  () => props.solveResponse,
  () => {
    pause()
    currentStep.value = 0
  },
)

const maxStep = computed(() => {
  if (!props.solveResponse?.result?.plan) return 0

  return props.solveResponse.result.plan.length - 1
})

const floorsReversed = computed(() => {
  return Array.from({ length: props.form.num_floors }, (_, i) => i).reverse()
})

const currentState = computed(() => {
  if (!props.solveResponse?.result?.plan) return null

  return props.solveResponse.result.plan[currentStep.value]
})

const playbackSpeed = ref(1)

const cycleSpeed = () => {
  playbackSpeed.value = playbackSpeed.value === 1 ? 2 : playbackSpeed.value === 2 ? 4 : 1

  if (isPlaying.value) {
    pause()
    togglePlay()
  }
}

const currentActions = computed(() => currentState.value?.actions || [])

const setStep = (step) => {
  if (step >= 0 && step <= maxStep.value) currentStep.value = step
}

const togglePlay = () => {
  if (isPlaying.value) {
    pause()
  } else {
    if (currentStep.value === maxStep.value) currentStep.value = 0

    isPlaying.value = true

    const intervalTime = 1000 / playbackSpeed.value

    playInterval = setInterval(() => {
      if (currentStep.value < maxStep.value) currentStep.value++
      else pause()
    }, intervalTime)
  }
}

const pause = () => {
  isPlaying.value = false

  if (playInterval) clearInterval(playInterval)
}

onUnmounted(() => pause())

// downloads Logic
const downloadData = async (type) => {
  try {
    const solveId = props.solveResponse.solve_id
    let data, filename, mime

    if (type === 'cnf') {
      const res = await fetchCNF(solveId)

      data = res.cnf
      filename = `movers_${solveId}.cnf`
      mime = 'text/plain'
    } else {
      const res = await fetchMapping(solveId)

      data = JSON.stringify(res.mapping, null, 2)
      filename = `mapping_${solveId}.json`
      mime = 'application/json'
    }

    const blob = new Blob([data], { type: mime })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    alert(`Failed to download ${type.toUpperCase()}: ${err.message}`)
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- error container from the api call -->
    <div
      v-if="error"
      class="rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-medium whitespace-pre-line text-red-700 transition-colors duration-300 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-400"
    >
      {{ error }}
    </div>

    <!-- start container before run the solver -->
    <div
      v-if="!solveResponse && !isLoading && !error"
      class="flex h-full min-h-125 flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-white text-slate-400 transition-colors duration-300 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-500"
    >
      <svg class="mb-4 h-16 w-16 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
        ></path>
      </svg>
      <p class="text-lg font-medium text-slate-500 dark:text-slate-400">Configure parameters and run the solver.</p>
    </div>

    <!-- loading container -->
    <div
      v-else-if="isLoading"
      class="flex h-full min-h-125 flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white shadow-sm transition-colors duration-300 dark:border-slate-800 dark:bg-slate-900"
    >
      <div class="mb-4 h-12 w-12 animate-spin rounded-full border-b-4 border-slate-800 dark:border-slate-400"></div>
      <p class="font-medium text-slate-600 dark:text-slate-400">Computing logic constraints...</p>
    </div>

    <!-- problem solved -->
    <template v-else-if="solveResponse">
      <div
        class="flex flex-col items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-colors duration-300 md:flex-row dark:border-slate-800 dark:bg-slate-900"
      >
        <!-- solution found or not title -->
        <div>
          <h2
            class="text-2xl font-black"
            :class="
              solveResponse.result.satisfiable
                ? 'text-emerald-600 dark:text-emerald-400'
                : 'text-rose-600 dark:text-rose-400'
            "
          >
            {{ solveResponse.result.satisfiable ? 'Solution Found' : 'Unsatisfiable' }}
          </h2>
          <p class="mt-1 font-mono text-xs text-slate-400 dark:text-slate-500">ID: {{ solveResponse.solve_id }}</p>
        </div>

        <!-- header container -->
        <div class="flex items-center gap-3 text-sm">
          <!-- general stats -->
          <div v-if="solveResponse.result.stats" class="mr-4 text-right">
            <p class="text-slate-500 dark:text-slate-400">
              Time:
              <span class="font-bold text-slate-800 dark:text-slate-200"
                >{{ solveResponse.result.stats.solve_time_ms.toFixed(1) }}ms</span
              >
            </p>
            <p class="text-slate-500 dark:text-slate-400">
              {{ solveResponse.result.satisfiable ? 'Steps:' : 'Tested up to T =' }}
              <span class="font-bold text-slate-800 dark:text-slate-200">{{
                solveResponse.result.num_time_steps
              }}</span>
            </p>
            <p class="text-slate-500 dark:text-slate-400">
              Vars / clauses:
              <span class="font-bold text-slate-800 dark:text-slate-200"
                >{{ solveResponse.result.stats.num_variables }} / {{ solveResponse.result.stats.num_clauses }}</span
              >
            </p>
          </div>
          <!-- cnf download button -->
          <button
            @click="downloadData('cnf')"
            class="rounded-lg border border-slate-300 bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            ⬇️ DIMACS CNF
          </button>
          <!-- mapping download button -->
          <button
            @click="downloadData('mapping')"
            class="rounded-lg border border-slate-300 bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            ⬇️ Mapping
          </button>
        </div>
      </div>

      <!-- building animation movers -->
      <div
        v-if="solveResponse.result.satisfiable && solveResponse.result.plan"
        class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-colors duration-300 dark:border-slate-800 dark:bg-slate-900"
      >
        <div
          class="sticky top-0 z-99 mb-8 flex items-center justify-between rounded-xl bg-slate-800 p-3 text-white shadow-inner transition-colors duration-300 dark:bg-slate-950 dark:shadow-black/50"
        >
          <div class="px-4 font-mono text-lg font-bold text-emerald-400">T = {{ currentStep }}</div>

          <!-- control speed panel -->
          <div class="flex items-center gap-2">
            <button
              @click="cycleSpeed"
              class="mr-4 rounded-lg bg-slate-700 px-3 py-1.5 font-mono text-sm font-bold text-emerald-400 transition-colors hover:bg-slate-600 dark:bg-slate-800 dark:hover:bg-slate-700"
              title="Playback Speed"
            >
              {{ playbackSpeed }}x
            </button>

            <button @click="setStep(0)" class="rounded-lg p-2 transition-colors hover:bg-slate-700" title="Reset">
              ⏮
            </button>
            <button
              @click="setStep(currentStep - 1)"
              :disabled="currentStep === 0"
              class="rounded-lg p-2 hover:bg-slate-700 disabled:opacity-50"
            >
              ⏪
            </button>
            <button
              @click="togglePlay"
              class="rounded-lg bg-emerald-500 px-6 py-2 font-bold text-slate-900 shadow-md transition-colors hover:bg-emerald-600"
            >
              {{ isPlaying ? '⏸ PAUSE' : '▶ PLAY' }}
            </button>
            <button
              @click="setStep(currentStep + 1)"
              :disabled="currentStep === maxStep"
              class="rounded-lg p-2 hover:bg-slate-700 disabled:opacity-50"
            >
              ⏩
            </button>
            <button @click="setStep(maxStep)" class="rounded-lg p-2 transition-colors hover:bg-slate-700" title="End">
              ⏭
            </button>
          </div>

          <div class="px-4 text-xs font-bold tracking-wider uppercase opacity-50">Timeline</div>
        </div>

        <!-- animation core container -->
        <BuildingVisualizer :floorsReversed="floorsReversed" :currentState="currentState" :task="form.task" />

        <!-- log about the movers -->
        <ActionLog :currentActions="currentActions" :currentStep="currentStep" :maxStep="maxStep" :task="form.task" />
      </div>

      <!-- unsatisfiable container -->
      <div
        v-else-if="!solveResponse.result.satisfiable"
        class="mt-6 flex h-full min-h-125 flex-col items-center justify-center rounded-2xl border-2 border-dashed border-rose-300 bg-rose-50 p-6 text-center transition-colors duration-300 dark:border-rose-900/50 dark:bg-rose-950/20"
      >
        <svg
          class="mb-4 h-16 w-16 text-rose-500 opacity-75 dark:text-rose-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          ></path>
        </svg>
        <h3 class="text-xl font-bold text-rose-700 dark:text-rose-400">This problem cannot be solved</h3>
        <p class="mt-2 text-rose-600/80 dark:text-rose-300/80">
          The constraints given are unsatisfiable. Try adjusting the parameters, reducing the goal complexity, or
          increasing the max/time steps.
        </p>
        <p class="mt-2 text-sm text-rose-600/70 dark:text-rose-300/70">
          You can still download the DIMACS CNF to verify the infeasibility in another SAT solver.
        </p>
      </div>
    </template>
  </div>
</template>
