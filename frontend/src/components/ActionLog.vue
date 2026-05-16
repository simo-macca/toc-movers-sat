<script setup>
defineProps({
  currentActions: { type: Array, required: true },
  currentStep: { type: Number, required: true },
  maxStep: { type: Number, required: true },
  task: { type: Number, required: true },
})
</script>

<template>
  <div class="mt-6 px-3">
    <h3 class="mb-2 text-sm font-bold tracking-wide text-slate-500 uppercase">
      Actions occurring at T={{ currentStep }}
    </h3>
    <div
      v-if="currentActions.length === 0"
      class="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500 italic"
    >
      <span v-if="currentStep === maxStep">
        {{
          task === 1
            ? 'Goal reached! Everyone has arrived at their destination. 🎉'
            : 'Goal reached! Everyone and everything is on the ground floor. 🎉'
        }}
      </span>
      <span v-else>No movements occurring.</span>
    </div>
    <div v-else class="grid grid-cols-1 gap-2.5">
      <div
        v-for="(act, idx) in currentActions"
        :key="idx"
        class="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm shadow-sm"
      >
        <span class="w-1/3 text-left font-bold text-slate-700 capitalize">{{ act.person.replace('_', ' ') }}</span>
        <span class="rounded border border-slate-200 bg-white px-2 py-1 font-mono text-xs">
          {{ act.from_floor }} ➡️ {{ act.to_floor }}
        </span>
        <span
          class="w-1/3 text-right font-semibold"
          :class="act.action === 'carries' ? 'text-purple-600' : 'text-blue-600'"
        >
          {{ act.action.toUpperCase() }} {{ act.item ? `(${act.item})` : '' }}
        </span>
      </div>
    </div>
  </div>
</template>
