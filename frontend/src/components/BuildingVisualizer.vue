<script setup>
import MoverFigure from './MoverFigure.vue'
import ItemFigure from './ItemFigure.vue'

const props = defineProps({
  floorsReversed: { type: Array, required: true },
  currentState: { type: Object, default: null },
  task: { type: Number, required: true },
})

const getMoversOnFloor = (floorNum) => {
  if (!props.currentState) return []

  return Object.entries(props.currentState.person_positions)
    .filter(([, floor]) => floor === floorNum)
    .map(([person]) => person)
}

const getItemsOnFloor = (floorNum) => {
  if (!props.currentState || props.task === 1) return []

  return Object.entries(props.currentState.item_positions)
    .filter(([, floor]) => floor === floorNum)
    .map(([item]) => item)
}
</script>

<template>
  <div
    class="relative max-h-170 overflow-auto rounded-lg border-4 border-slate-800 bg-blue-50 shadow-inner transition-colors duration-300 dark:border-slate-700 dark:bg-slate-950"
  >
    <div class="flex min-w-max flex-col">
      <!-- floor container -->
      <div
        v-for="floorNum in floorsReversed"
        :key="floorNum"
        class="flex h-24 w-full border-b-4 border-slate-300 transition-colors duration-300 dark:border-slate-700"
        :class="floorNum === 0 ? 'border-b-0 bg-slate-200 dark:bg-slate-900' : ''"
      >
        <div
          class="sticky left-0 z-20 flex w-12 shrink-0 items-center justify-center border-r-4 border-slate-900 bg-slate-800 text-xl font-black text-white transition-colors duration-300 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
        >
          {{ floorNum }}
        </div>

        <div class="flex flex-1 items-end gap-4 pt-3.5 pr-16 pb-2 pl-4 transition-all duration-300">
          <!-- mover icon -->
          <MoverFigure v-for="person in getMoversOnFloor(floorNum)" :key="person" :name="person" />

          <!-- seperator -->
          <div v-if="getMoversOnFloor(floorNum).length > 0 && getItemsOnFloor(floorNum).length > 0"></div>

          <!-- item icon -->
          <ItemFigure v-for="item in getItemsOnFloor(floorNum)" :key="item" :name="item" />
        </div>
      </div>
    </div>
  </div>
</template>
