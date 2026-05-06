<script setup>
defineProps({
  msg: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div class="text-center md:text-left">
    <h1 class="mb-3 text-5xl font-black tracking-tight text-emerald-600 drop-shadow-sm">
      {{ msg }}
    </h1>
    <h3 class="max-w-lg text-lg leading-relaxed font-medium text-slate-600">
      You've successfully created a project with
      <a
        href="https://vite.dev/"
        target="_blank"
        rel="noopener"
        class="text-emerald-600 underline decoration-2 underline-offset-4 transition-colors hover:text-emerald-800"
        >Vite</a
      >
      +
      <a
        href="https://vuejs.org/"
        target="_blank"
        rel="noopener"
        class="text-emerald-600 underline decoration-2 underline-offset-4 transition-colors hover:text-emerald-800"
        >Vue 3</a
      >.
    </h3>
  </div>
</template>
