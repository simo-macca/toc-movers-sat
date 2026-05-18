<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  form: { type: Object, required: true },
  isLoading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:form', 'submit'])

const localForm = ref(JSON.parse(JSON.stringify(props.form)))
const showAdvanced = ref(false)

// keep localForm in sync with parent automatically
watch(
  localForm,
  (newValue) => {
    emit('update:form', newValue)
  },
  { deep: true },
)

// watch for changes
watch(
  () => localForm.value.num_persons,
  (newCount) => {
    if (!newCount || newCount < 1) return

    // adjust person names array
    while (localForm.value.person_names.length < newCount)
      localForm.value.person_names.push(`Mover ${localForm.value.person_names.length + 1}`)

    if (localForm.value.person_names.length > newCount) localForm.value.person_names.splice(newCount)

    // adjust goal floors array
    while (localForm.value.goal_floors.length < newCount) localForm.value.goal_floors.push(0)

    if (localForm.value.goal_floors.length > newCount) localForm.value.goal_floors.splice(newCount)
  },
)

const addItem = () => {
  const nextItemNumber = localForm.value.items.length + 1

  localForm.value.items.push({
    name: `Item ${nextItemNumber}`,
    initial_floor: localForm.value.num_floors - 1,
  })
}

const removeItem = (index) => {
  localForm.value.items.splice(index, 1)
}
</script>

<template>
  <div
    class="h-fit rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-colors duration-300 dark:border-slate-800 dark:bg-slate-900"
  >
    <!-- title and advance toggle -->
    <h2 class="mb-6 flex items-center justify-between text-xl font-bold text-slate-800 dark:text-white">
      <span>Problem Setup</span>
      <button
        type="button"
        @click="showAdvanced = !showAdvanced"
        class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
      >
        {{ showAdvanced ? 'Hide Advanced' : '⚙️ Advanced' }}
      </button>
    </h2>

    <!-- form section -->
    <form @submit.prevent="emit('submit')" class="space-y-5">
      <!-- task type -->
      <div>
        <label class="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-300">Task Type</label>
        <select
          v-model="localForm.task"
          class="w-full rounded-lg border border-slate-300 bg-slate-50 p-2.5 shadow-sm focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        >
          <option :value="1">Task 1: Movement Only</option>
          <option :value="2">Task 2: Movement + Items</option>
        </select>
      </div>

      <!-- main movers setting -->
      <div class="grid grid-cols-2 gap-4">
        <!-- number of floor -->
        <div>
          <label class="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-300">Total Floors</label>
          <input
            type="number"
            v-model.number="localForm.num_floors"
            min="1"
            class="w-full rounded-lg border border-slate-300 bg-slate-50 p-2.5 shadow-sm focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            required
          />
        </div>

        <!-- number of movers -->
        <div>
          <label class="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-300">Movers</label>
          <input
            type="number"
            v-model.number="localForm.num_persons"
            min="1"
            class="w-full rounded-lg border border-slate-300 bg-slate-50 p-2.5 shadow-sm focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            required
          />
        </div>
      </div>

      <!-- main item setting for task 2 -->
      <div
        v-if="localForm.task === 2"
        class="max-h-80 overflow-scroll rounded-xl border border-slate-200 bg-slate-100 p-4 transition-colors duration-300 dark:border-slate-700 dark:bg-slate-800/50"
      >
        <div class="mb-3 flex items-center justify-between">
          <label class="block text-sm font-bold text-slate-700 dark:text-slate-200">Items to Move</label>
          <!-- add item button -->
          <button
            type="button"
            @click="addItem"
            class="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            + Add Item
          </button>
        </div>

        <!-- floor where the item are at start -->
        <div v-for="(item, index) in localForm.items" :key="index" class="mb-2 flex items-center gap-2">
          <input
            type="text"
            v-model="item.name"
            :placeholder="`Item ${index}`"
            class="w-30 rounded-md border border-slate-300 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none dark:border-slate-600 dark:bg-slate-700 dark:text-white"
            required
          />
          <input
            type="number"
            v-model.number="item.initial_floor"
            min="0"
            :max="localForm.num_floors - 1"
            placeholder="Floor"
            class="w-15 rounded-md border border-slate-300 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none dark:border-slate-600 dark:bg-slate-700 dark:text-white"
            required
          />
          <button
            type="button"
            @click="removeItem(index)"
            class="p-1 text-xl font-bold text-slate-400 transition-colors hover:text-red-500 dark:text-slate-500 dark:hover:text-red-400"
          >
            &times;
          </button>
        </div>
        <p v-if="localForm.items.length === 0" class="mt-2 text-xs text-slate-500 italic dark:text-slate-400">
          Add items to transport them to floor 0.
        </p>
      </div>

      <!-- advance settings -->
      <div
        v-if="showAdvanced"
        class="space-y-4 rounded-xl border border-blue-200 bg-blue-50/50 p-4 transition-colors duration-300 dark:border-blue-900/50 dark:bg-blue-900/20"
      >
        <h3
          class="border-b border-blue-200 pb-2 text-xs font-bold tracking-wide text-blue-800 uppercase dark:border-blue-900/50 dark:text-blue-400"
        >
          Advanced Engine Options
        </h3>

        <!-- change movers' name -->
        <div class="max-h-80 overflow-scroll">
          <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">Custom Mover Names</label>
          <div class="grid grid-cols-2 gap-2">
            <input
              v-for="(name, idx) in localForm.person_names"
              :key="idx"
              type="text"
              v-model="localForm.person_names[idx]"
              class="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              placeholder="Name"
              required
            />
          </div>
        </div>

        <!-- target floor for each movers for task 1 -->
        <div v-if="localForm.task === 1" class="max-h-80 overflow-scroll">
          <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300"
            >Target Floors (Goal)</label
          >
          <div class="grid grid-cols-2 gap-2">
            <div
              v-for="(name, idx) in localForm.person_names"
              :key="idx"
              class="flex items-center gap-2 rounded-md border border-slate-200 bg-white p-1.5 dark:border-slate-700 dark:bg-slate-800"
            >
              <span class="w-full truncate px-1 text-xs font-medium text-slate-600 dark:text-slate-400"
                >{{ name }}:</span
              >
              <input
                type="number"
                v-model.number="localForm.goal_floors[idx]"
                min="0"
                :max="localForm.num_floors - 1"
                class="w-16 rounded border border-slate-300 p-1 text-center text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none dark:border-slate-600 dark:bg-slate-700 dark:text-white"
                required
              />
            </div>
          </div>
        </div>

        <!-- solve mode selection -->
        <div class="border-t border-blue-200 pt-2 dark:border-blue-900/50">
          <label class="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-300">Solving Mode</label>
          <select
            v-model="localForm.solve_mode"
            class="mb-3 w-full rounded-md border border-slate-300 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
          >
            <option value="optimal">Iterative Deepening (Find Shortest)</option>
            <option value="fixed">Fixed Horizon (Solve exact T)</option>
          </select>

          <div v-if="localForm.solve_mode === 'optimal'">
            <label class="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-300"
              >Max Steps (Timeout)</label
            >
            <input
              type="number"
              v-model.number="localForm.max_steps"
              min="1"
              max="50"
              class="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              required
            />
            <p class="mt-1 text-[10px] text-slate-500 dark:text-slate-400">
              Stop searching if optimal path requires more than this many steps.
            </p>
          </div>

          <div v-if="localForm.solve_mode === 'fixed'">
            <label class="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-300"
              >Exact Time Horizon (T)</label
            >
            <input
              type="number"
              v-model.number="localForm.time_steps"
              min="1"
              max="50"
              class="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              required
            />
            <p class="mt-1 text-[10px] text-slate-500 dark:text-slate-400">
              Only checks if a plan exists in exactly T steps.
            </p>
          </div>
        </div>
      </div>

      <!-- run button -->
      <button
        type="submit"
        :disabled="isLoading"
        class="flex w-full items-center justify-center rounded-xl bg-slate-800 px-4 py-3 font-bold text-white shadow-md transition-all hover:bg-slate-900 disabled:opacity-60 dark:bg-blue-600 dark:hover:bg-blue-500"
      >
        <span v-if="isLoading">Solving...</span>
        <span v-else>Run SAT Solver</span>
      </button>
    </form>
  </div>
</template>
