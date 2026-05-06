<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div class="min-h-screen bg-slate-50 font-sans text-slate-800 selection:bg-emerald-200">
    <header
      class="mx-auto flex max-w-7xl flex-col items-center gap-8 border-b border-slate-200 px-4 py-12 md:flex-row"
    >
      <img
        alt="Vue logo"
        class="h-32 w-32 drop-shadow-xl transition-transform hover:scale-105"
        src="@/assets/logo.svg"
      />

      <div class="flex flex-col items-center gap-6 md:items-start">
        <HelloWorld msg="You did it!" />

        <nav class="flex gap-2 rounded-lg border border-slate-200 bg-white p-1.5 shadow-sm">
          <RouterLink
            to="/"
            class="rounded-md px-5 py-2 font-semibold text-slate-500 transition-all hover:bg-slate-100 hover:text-emerald-600 focus:ring-2 focus:ring-emerald-500 focus:outline-none active:bg-slate-200"
            exact-active-class="bg-emerald-50 text-emerald-700 shadow-sm border border-emerald-100"
          >
            Home
          </RouterLink>
          <RouterLink
            to="/about"
            class="rounded-md px-5 py-2 font-semibold text-slate-500 transition-all hover:bg-slate-100 hover:text-emerald-600 focus:ring-2 focus:ring-emerald-500 focus:outline-none active:bg-slate-200"
            exact-active-class="bg-emerald-50 text-emerald-700 shadow-sm border border-emerald-100"
          >
            About
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-4 py-12">
      <RouterView />
    </main>
  </div>
</template>
