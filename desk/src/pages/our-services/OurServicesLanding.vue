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
      v-else-if="pageContent.data?.content"
      class="py-4 mx-auto w-full max-w-3xl px-5 flex flex-col"
    >
      <div
        class="services-content prose prose-sm max-w-none"
        v-html="pageContent.data.content"
      />
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
  url: "helpdesk.api.services.get_our_services_content",
  auto: true,
});

const breadcrumbs = computed(() => [
  {
    label: __("Our Services"),
    route: {
      name: isCustomerPortal.value ? "OurServices" : "OurServicesAgent",
    },
  },
]);

usePageMeta(() => ({
  title: __("Our Services"),
}));
</script>

<style>
.services-content h1 {
  @apply text-2xl font-bold mt-6 mb-3;
}
.services-content h2 {
  @apply text-xl font-semibold mt-5 mb-2;
}
.services-content h3 {
  @apply text-lg font-semibold mt-4 mb-2;
}
.services-content p {
  @apply my-2 leading-relaxed;
}
.services-content ul {
  @apply list-disc pl-6 my-2;
}
.services-content ol {
  @apply list-decimal pl-6 my-2;
}
.services-content li {
  @apply my-1;
}
.services-content code {
  @apply bg-gray-100 text-gray-800 rounded px-1 py-0.5 text-sm;
}
.services-content pre {
  @apply bg-gray-100 text-gray-800 rounded p-3 overflow-x-auto my-3;
}
.services-content pre code {
  @apply bg-transparent p-0;
}
.services-content blockquote {
  @apply border-l-4 border-gray-300 pl-4 my-3 text-gray-600;
}
.services-content a {
  @apply text-blue-600 hover:underline;
}
.services-content table {
  @apply border-collapse w-full my-3;
}
.services-content th,
.services-content td {
  @apply border border-gray-300 px-3 py-2 text-left;
}
.services-content th {
  @apply bg-gray-50 font-semibold;
}
.services-content img {
  @apply max-w-full rounded my-3;
}
</style>
