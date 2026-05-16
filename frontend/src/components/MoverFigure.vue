<script setup>
defineProps({
  name: { type: String, required: true },
})
</script>

<template>
  <div class="animate-bounce-short flex flex-col items-center transition-transform hover:scale-110">
    <div class="relative flex flex-col items-center">
      <div
        class="z-10 h-4 w-4 rounded-full border-2 border-slate-800 bg-amber-100 shadow-sm transition-colors duration-300 dark:border-slate-900 dark:bg-amber-200"
      ></div>

      <div
        class="-mt-1 flex h-8 w-6 justify-center rounded-t-lg rounded-b-sm border-2 border-slate-800 bg-blue-600 shadow-md transition-colors duration-300 dark:border-slate-900 dark:bg-blue-500"
      >
        <div class="h-full w-0.5 bg-slate-800/30"></div>
      </div>
    </div>

    <span
      class="mt-1 truncate text-center text-[10px] font-bold tracking-wider text-slate-600 uppercase transition-colors duration-300 dark:text-slate-400"
    >
      {{ name.replace('person_', 'P') }}
    </span>
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
