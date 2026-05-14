<script setup>
const props = defineProps({
  floorsReversed: { type: Array, required: true },
  currentState: { type: Object, default: null },
  task: { type: Number, required: true },
})

const getMoversOnFloor = (floorNum) => {
  if (!props.currentState) return []

  return Object.entries(props.currentState.person_positions)
    .filter(([_, floor]) => floor === floorNum)
    .map(([person, _]) => person)
}

const getItemsOnFloor = (floorNum) => {
  if (!props.currentState || props.task === 1) return []

  return Object.entries(props.currentState.item_positions)
    .filter(([_, floor]) => floor === floorNum)
    .map(([item, _]) => item)
}
</script>

<template>
  <div
    class="relative max-h-125 overflow-x-hidden overflow-y-auto rounded-lg border-4 border-slate-800 bg-blue-50 shadow-inner"
  >
    <div
      v-for="floorNum in floorsReversed"
      :key="floorNum"
      class="relative flex h-24 items-end border-b-4 border-slate-300 px-16 pb-2"
      :class="floorNum === 0 ? 'border-b-0 bg-slate-200' : ''"
    >
      <div
        class="absolute top-0 bottom-0 left-0 z-10 flex w-12 items-center justify-center border-r-4 border-slate-900 bg-slate-800 text-xl font-black text-white"
      >
        {{ floorNum }}
      </div>
      <div class="flex w-full items-end gap-3 transition-all duration-300">
        <div
          v-for="person in getMoversOnFloor(floorNum)"
          :key="person"
          class="animate-bounce-short flex flex-col items-center"
        >
          <div
            class="flex h-12 w-8 items-center justify-center rounded-full border-2 border-slate-800 bg-blue-600 shadow-md"
          >
            <div class="mb-4 h-3 w-3 rounded-full bg-white"></div>
          </div>
          <span class="mt-1 text-[10px] font-bold text-slate-600 uppercase">{{
            person.replace('person_', 'P')
          }}</span>
        </div>
        <div class="w-8"></div>
        <div
          v-for="item in getItemsOnFloor(floorNum)"
          :key="item"
          class="flex flex-col items-center"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded border-2 border-amber-800 bg-amber-500 shadow-md"
          >
            <span class="text-xl">📦</span>
          </div>
          <span
            class="mt-1 w-12 truncate text-center text-[10px] font-bold text-amber-800 uppercase"
            >{{ item }}</span
          >
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes bounce-short {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}
.animate-bounce-short {
  animation: bounce-short 1.5s ease-in-out infinite;
}
</style>
