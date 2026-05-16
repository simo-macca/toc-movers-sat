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
  <div class="h-fit rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <h2 class="mb-6 flex items-center justify-between text-xl font-bold text-slate-800">
      <span>Problem Setup</span>
      <button
        type="button"
        @click="showAdvanced = !showAdvanced"
        class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600 transition-colors hover:bg-slate-200"
      >
        {{ showAdvanced ? 'Hide Advanced' : '⚙️ Advanced' }}
      </button>
    </h2>

    <form @submit.prevent="emit('submit')" class="space-y-5">
      <div>
        <label class="mb-1 block text-sm font-semibold text-slate-700">Task Type</label>
        <select
          v-model="localForm.task"
          class="w-full rounded-lg border border-slate-300 bg-slate-50 p-2.5 shadow-sm focus:ring-2 focus:ring-blue-500"
        >
          <option :value="1">Task 1: Movement Only</option>
          <option :value="2">Task 2: Movement + Items</option>
        </select>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="mb-1 block text-sm font-semibold text-slate-700">Total Floors</label>
          <input
            type="number"
            v-model.number="localForm.num_floors"
            min="1"
            class="w-full rounded-lg border border-slate-300 bg-slate-50 p-2.5 shadow-sm"
            required
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-semibold text-slate-700">Movers</label>
          <input
            type="number"
            v-model.number="localForm.num_persons"
            min="1"
            class="w-full rounded-lg border border-slate-300 bg-slate-50 p-2.5 shadow-sm"
            required
          />
        </div>
      </div>

      <div
        v-if="localForm.task === 2"
        class="max-h-80 overflow-scroll rounded-xl border border-slate-200 bg-slate-100 p-4"
      >
        <div class="mb-3 flex items-center justify-between">
          <label class="block text-sm font-bold text-slate-700">Items to Move</label>
          <button
            type="button"
            @click="addItem"
            class="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-50"
          >
            + Add Item
          </button>
        </div>
        <div v-for="(item, index) in localForm.items" :key="index" class="mb-2 flex items-center gap-2">
          <input
            type="text"
            v-model="item.name"
            :placeholder="`Item ${index}`"
            class="w-30 rounded-md border border-slate-300 p-2 text-sm"
            required
          />
          <input
            type="number"
            v-model.number="item.initial_floor"
            min="0"
            :max="localForm.num_floors - 1"
            placeholder="Floor"
            class="w-15 rounded-md border border-slate-300 p-2 text-sm"
            required
          />
          <button
            type="button"
            @click="removeItem(index)"
            class="p-1 text-xl font-bold text-slate-400 hover:text-red-500"
          >
            &times;
          </button>
        </div>
        <p v-if="localForm.items.length === 0" class="mt-2 text-xs text-slate-500 italic">
          Add items to transport them to floor 0.
        </p>
      </div>

      <div v-if="showAdvanced" class="space-y-4 rounded-xl border border-blue-200 bg-blue-50/50 p-4">
        <h3 class="border-b border-blue-200 pb-2 text-xs font-bold tracking-wide text-blue-800 uppercase">
          Advanced Engine Options
        </h3>

        <div class="max-h-80 overflow-scroll">
          <label class="mb-2 block text-sm font-semibold text-slate-700">Custom Mover Names</label>
          <div class="grid grid-cols-2 gap-2">
            <input
              v-for="(name, idx) in localForm.person_names"
              :key="idx"
              type="text"
              v-model="localForm.person_names[idx]"
              class="w-full rounded-md border border-slate-300 p-2 text-sm"
              placeholder="Name"
              required
            />
          </div>
        </div>

        <div v-if="localForm.task === 1" class="max-h-80 overflow-scroll">
          <label class="mb-2 block text-sm font-semibold text-slate-700">Target Floors (Goal)</label>
          <div class="grid grid-cols-2 gap-2">
            <div
              v-for="(name, idx) in localForm.person_names"
              :key="idx"
              class="flex items-center gap-2 rounded-md border border-slate-200 bg-white p-1.5"
            >
              <span class="w-full truncate px-1 text-xs font-medium text-slate-600">{{ name }}:</span>
              <input
                type="number"
                v-model.number="localForm.goal_floors[idx]"
                min="0"
                :max="localForm.num_floors - 1"
                class="w-16 rounded border border-slate-300 p-1 text-center text-sm"
                required
              />
            </div>
          </div>
        </div>

        <div class="border-t border-blue-200 pt-2">
          <label class="mb-1 block text-sm font-semibold text-slate-700">Solving Mode</label>
          <select v-model="localForm.solve_mode" class="mb-3 w-full rounded-md border border-slate-300 p-2 text-sm">
            <option value="optimal">Iterative Deepening (Find Shortest)</option>
            <option value="fixed">Fixed Horizon (Solve exact T)</option>
          </select>

          <div v-if="localForm.solve_mode === 'optimal'">
            <label class="mb-1 block text-sm font-semibold text-slate-700">Max Steps (Timeout)</label>
            <input
              type="number"
              v-model.number="localForm.max_steps"
              min="1"
              max="50"
              class="w-full rounded-md border border-slate-300 p-2 text-sm"
              required
            />
            <p class="mt-1 text-[10px] text-slate-500">
              Stop searching if optimal path requires more than this many steps.
            </p>
          </div>

          <div v-if="localForm.solve_mode === 'fixed'">
            <label class="mb-1 block text-sm font-semibold text-slate-700">Exact Time Horizon (T)</label>
            <input
              type="number"
              v-model.number="localForm.time_steps"
              min="1"
              max="50"
              class="w-full rounded-md border border-slate-300 p-2 text-sm"
              required
            />
            <p class="mt-1 text-[10px] text-slate-500">Only checks if a plan exists in exactly T steps.</p>
          </div>
        </div>
      </div>

      <button
        type="submit"
        :disabled="isLoading"
        class="flex w-full items-center justify-center rounded-xl bg-slate-800 px-4 py-3 font-bold text-white shadow-md transition-all hover:bg-slate-900 disabled:opacity-60"
      >
        <span v-if="isLoading">Solving...</span>
        <span v-else>Run SAT Solver</span>
      </button>
    </form>
  </div>
</template>
