<template>
  <div class="flex flex-col overflow-y-auto">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
    </LayoutHeader>

    <div v-if="pageContent.loading" class="flex justify-center py-20">
      <Spinner class="h-5 w-5 text-gray-500" />
    </div>

    <div
      v-else-if="pageContent.data?.enabled && pageContent.data?.content"
      class="py-4 mx-auto w-full max-w-6xl px-5 flex flex-col"
    >
      <div class="mb-4">
        <h1 class="text-2xl font-semibold text-ink-gray-9">
          {{ pageContent.data.title || __("Support Plan") }}
        </h1>
      </div>
      <div class="support-plan-content prose prose-sm max-w-none" v-html="pageContent.data.content" />
    </div>

    <div
      v-else
      class="flex flex-col items-center justify-center py-20 text-gray-500"
    >
      <p>{{ __("No content has been added yet.") }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader } from "@/components";
import { __ } from "@/translation";
import { isCustomerPortal } from "@/utils";
import { Breadcrumbs, createResource, Spinner, usePageMeta } from "frappe-ui";
import { computed } from "vue";

const pageContent = createResource({
  url: "helpdesk.api.support_plan.get_support_plan_content",
  auto: true,
});

const breadcrumbs = computed(() => [
  {
    label: __("Support Plan"),
    route: {
      name: isCustomerPortal.value ? "SupportPlan" : "SupportPlanAgent",
    },
  },
]);

usePageMeta(() => ({
  title: __("Support Plan"),
}));
</script>

<style>
.support-plan-content table {
  @apply w-full border-collapse overflow-hidden rounded-lg;
}

.support-plan-content th,
.support-plan-content td {
  @apply border border-outline-gray-2 px-3 py-2 align-top text-p-sm text-ink-gray-7;
}

.support-plan-content th {
  @apply bg-surface-gray-2 font-semibold text-ink-gray-9;
}

.support-plan-content tbody tr:nth-child(even) {
  @apply bg-surface-gray-1;
}

.support-plan-content p {
  @apply my-2;
}
</style>
