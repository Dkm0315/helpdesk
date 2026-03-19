<template>
  <div class="flex flex-col overflow-y-auto">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
    </LayoutHeader>
    <div
      class="flex flex-col gap-6 py-6 self-center mx-auto w-full max-w-4xl px-5"
    >
      <!-- SLA Disclaimer -->
      <div
        v-if="pageContent.data?.sla_disclaimer"
        class="border border-gray-200 rounded-lg p-4 bg-gray-50 text-sm text-gray-500 italic"
      >
        {{ pageContent.data.sla_disclaimer }}
      </div>

      <!-- Support Metrics -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Response Commitments") }}</h2>
        <p class="text-sm text-gray-600 mt-1">
          {{ __("Standard response time targets based on environment classification.") }}
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
          <!-- Non-production -->
          <div class="border rounded-lg p-5 bg-gray-50">
            <h3 class="text-base font-medium text-gray-800">{{ __("Non-Production") }}</h3>
            <div class="mt-3 space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">{{ __("Response Time") }}</span>
                <span class="font-medium text-gray-900">{{ pageContent.data?.non_production_response_time || __("4 Hours") }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">{{ __("Availability") }}</span>
                <span class="font-medium text-gray-900">{{ pageContent.data?.non_production_availability || __("Business Hours") }}</span>
              </div>
            </div>
          </div>
          <!-- Production -->
          <div class="border rounded-lg p-5 bg-gray-50">
            <h3 class="text-base font-medium text-gray-800">{{ __("Production") }}</h3>
            <div class="mt-3 space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">{{ __("Response Time") }}</span>
                <span class="font-medium text-gray-900">{{ pageContent.data?.production_response_time || __("1 Hour") }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">{{ __("Availability") }}</span>
                <span class="font-medium text-gray-900">{{ pageContent.data?.production_availability || __("24/7") }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Supported Technologies -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Supported Technologies") }}</h2>
        <p class="text-sm text-gray-600 mt-1">
          {{ __("Select a technology to view the detailed support structure and service offerings.") }}
        </p>

        <div v-if="technologies.loading" class="flex justify-center py-8">
          <Spinner class="h-5 w-5 text-gray-500" />
        </div>

        <div
          v-else-if="technologies.data?.length"
          class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4"
        >
          <RouterLink
            v-for="tech in technologies.data"
            :key="tech.name"
            :to="{ name: detailRoute, params: { technologyId: tech.technology_name } }"
            class="border rounded-lg p-5 hover:shadow-md hover:border-gray-300 transition cursor-pointer block"
          >
            <div class="flex items-center gap-3 mb-3">
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center"
                :class="iconClasses(tech.icon_color)"
              >
                <span class="font-bold text-lg" :class="iconTextClass(tech.icon_color)">
                  {{ tech.icon_letter }}
                </span>
              </div>
              <h3 class="text-base font-medium text-gray-900">{{ tech.technology_name }}</h3>
            </div>
            <p class="text-sm text-gray-600">{{ tech.description }}</p>
            <span class="text-sm font-medium text-blue-600 mt-3 inline-block">{{ __("View Details") }} &rarr;</span>
          </RouterLink>
        </div>

        <div v-else class="text-sm text-gray-500 mt-4">
          {{ __("No supported technologies configured yet.") }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader } from "@/components";
import { __ } from "@/translation";
import { isCustomerPortal } from "@/utils";
import { Breadcrumbs, createResource, Spinner, usePageMeta } from "frappe-ui";
import { computed } from "vue";

const COLOR_MAP: Record<string, { bg: string; text: string }> = {
  Red: { bg: "bg-red-100", text: "text-red-600" },
  Orange: { bg: "bg-orange-100", text: "text-orange-600" },
  Green: { bg: "bg-green-100", text: "text-green-600" },
  Blue: { bg: "bg-blue-100", text: "text-blue-600" },
  Purple: { bg: "bg-purple-100", text: "text-purple-600" },
  Indigo: { bg: "bg-indigo-100", text: "text-indigo-600" },
};

function iconClasses(color: string) {
  return COLOR_MAP[color]?.bg || "bg-gray-100";
}

function iconTextClass(color: string) {
  return COLOR_MAP[color]?.text || "text-gray-600";
}

const pageContent = createResource({
  url: "helpdesk.api.services.get_services_page_content",
  auto: true,
});

const technologies = createResource({
  url: "helpdesk.api.services.get_supported_technologies",
  auto: true,
});

const detailRoute = computed(() =>
  isCustomerPortal.value ? "OurServicesTechnology" : "OurServicesTechnologyAgent"
);

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
