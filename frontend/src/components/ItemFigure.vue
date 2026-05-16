<script setup>
defineProps({
  name: { type: String, required: true },
})
</script>

<template>
  <div class="flex flex-col items-center transition-transform hover:-translate-y-1">
    <div
      class="relative flex h-10 w-10 items-center justify-center overflow-hidden rounded border-2 border-amber-800 bg-linear-to-br from-amber-300 to-amber-600 shadow-md transition-colors duration-300 dark:border-amber-900 dark:from-amber-600 dark:to-amber-800"
    >
      <div class="absolute h-full w-2 bg-amber-900/10"></div>
      <span class="z-10 text-xl drop-shadow-sm">📦</span>
    </div>

    <span
      class="mt-1 w-14 truncate text-center text-[10px] font-bold tracking-wider text-amber-800 uppercase transition-colors duration-300 dark:text-amber-500"
      :title="name"
    >
      {{ name }}
    </span>
  </div>
</template>
