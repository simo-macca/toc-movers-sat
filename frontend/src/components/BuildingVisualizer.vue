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
  <div class="relative max-h-170 overflow-auto rounded-lg border-4 border-slate-800 bg-blue-50 shadow-inner">
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

      <div class="flex w-full items-start gap-4 pt-3.5 transition-all duration-300">
        <MoverFigure v-for="person in getMoversOnFloor(floorNum)" :key="person" :name="person" />

        <div v-if="getMoversOnFloor(floorNum).length > 0 && getItemsOnFloor(floorNum).length > 0" class="w-4"></div>

        <ItemFigure v-for="item in getItemsOnFloor(floorNum)" :key="item" :name="item" />
      </div>
    </div>
  </div>
</template>
