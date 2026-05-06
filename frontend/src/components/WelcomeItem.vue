<template>
  <div
    class="group flex cursor-default flex-col items-start gap-4 rounded-xl border border-slate-200 bg-slate-50 p-6 transition-colors duration-300 hover:border-emerald-200 hover:bg-emerald-50 hover:shadow-md"
  >
    <i
      class="flex h-12 w-12 items-center justify-center rounded-full border border-slate-100 bg-white text-emerald-600 shadow-sm transition-transform group-hover:scale-110 group-hover:rotate-3"
    >
      <slot name="icon"></slot>
    </i>

    <div class="w-full flex-1">
      <h3 class="mb-2 text-xl font-bold text-slate-800">
        <slot name="heading"></slot>
      </h3>
      <div
        class="text-sm leading-relaxed text-slate-600 [&>a]:font-semibold [&>a]:text-emerald-600 [&>a:hover]:underline"
      >
        <slot></slot>
      </div>
    </div>
  </div>
</template>
