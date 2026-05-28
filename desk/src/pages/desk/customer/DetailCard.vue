<template>
  <section class="rounded-2xl border bg-white p-4 shadow-sm">
    <div class="mb-3 flex items-center justify-between">
      <h3 class="text-sm font-semibold text-ink-gray-9">{{ title }}</h3>
      <Badge :label="String(rows?.length || 0)" theme="gray" />
    </div>
    <div v-if="rows?.length" class="space-y-2">
      <div
        v-for="row in rows"
        :key="row.name"
        class="rounded-xl border border-outline-gray-1 bg-surface-gray-1 p-3"
      >
        <slot name="row" :row="row" />
      </div>
    </div>
    <div v-else class="rounded-xl border border-dashed p-4 text-center text-sm text-ink-gray-5">
      No records yet.
    </div>
  </section>
</template>

<script setup lang="ts">
import { Badge } from "frappe-ui";

defineProps<{
  title: string;
  rows?: Array<Record<string, any>>;
}>();
</script>
