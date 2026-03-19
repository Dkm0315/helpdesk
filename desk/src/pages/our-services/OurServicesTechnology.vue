<template>
  <div class="flex flex-col overflow-y-auto">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
    </LayoutHeader>

    <div v-if="techDetail.loading" class="flex justify-center py-20">
      <Spinner class="h-5 w-5 text-gray-500" />
    </div>

    <div
      v-else-if="techDetail.data"
      class="flex flex-col gap-6 py-6 self-center mx-auto w-full max-w-4xl px-5"
    >
      <!-- Page Title -->
      <div>
        <h1 class="text-xl font-semibold text-gray-900">
          {{ techDetail.data.technology_name }} {{ __("Support Services") }}
        </h1>
        <p v-if="techDetail.data.detail_intro" class="text-sm text-gray-600 mt-1">
          {{ techDetail.data.detail_intro }}
        </p>
      </div>

      <!-- SLA Disclaimer -->
      <div
        v-if="pageContent.data?.sla_disclaimer"
        class="border border-gray-200 rounded-lg p-4 bg-gray-50 text-sm text-gray-500 italic"
      >
        {{ pageContent.data.sla_disclaimer }}
      </div>

      <!-- Service Tiers -->
      <div
        v-for="tier in techDetail.data.service_tiers"
        :key="tier.tier_name"
        class="border rounded-lg p-4 bg-gray-50"
      >
        <h2 class="text-lg font-semibold text-gray-900">{{ tier.tier_name }}</h2>
        <p v-if="tier.tier_description" class="text-sm text-gray-600 mt-2">
          <span class="font-medium text-gray-800">{{ __("Primary Role:") }}</span>
          {{ tier.tier_description }}
        </p>

        <h3 class="text-base font-medium text-gray-800 mt-4">{{ __("Responsibilities") }}</h3>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-2">
          <li v-for="(item, idx) in parseLines(tier.responsibilities)" :key="idx">
            {{ item }}
          </li>
        </ul>

        <div v-if="tier.tools_methods" class="mt-4">
          <h3 class="text-base font-medium text-gray-800">{{ __("Tools & Methods") }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ tier.tools_methods }}</p>
        </div>

        <div v-if="tier.out_of_scope" class="mt-4 pt-3 border-t border-gray-200">
          <p class="text-sm text-gray-600">
            <span class="font-medium text-gray-800">{{ __("Out of Scope:") }}</span>
            {{ tier.out_of_scope }}
          </p>
        </div>
      </div>
    </div>

    <div
      v-else
      class="flex flex-col items-center justify-center py-20 text-gray-500"
    >
      <p>{{ __("Technology not found") }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader } from "@/components";
import { __ } from "@/translation";
import { isCustomerPortal } from "@/utils";
import { Breadcrumbs, createResource, Spinner, usePageMeta } from "frappe-ui";
import { computed, watch } from "vue";

const props = defineProps<{
  technologyId: string;
}>();

const pageContent = createResource({
  url: "helpdesk.api.services.get_services_page_content",
  auto: true,
});

const techDetail = createResource({
  url: "helpdesk.api.services.get_technology_detail",
  params: { technology_name: props.technologyId },
  auto: true,
});

watch(
  () => props.technologyId,
  (newId) => {
    techDetail.update({ params: { technology_name: newId } });
    techDetail.reload();
  }
);

function parseLines(text: string): string[] {
  if (!text) return [];
  return text.split("\n").filter((line) => line.trim());
}

const breadcrumbs = computed(() => [
  {
    label: __("Our Services"),
    route: {
      name: isCustomerPortal.value ? "OurServices" : "OurServicesAgent",
    },
  },
  {
    label: techDetail.data?.technology_name || props.technologyId,
    route: {},
  },
]);

usePageMeta(() => ({
  title: techDetail.data
    ? `${techDetail.data.technology_name} ${__("Support Services")}`
    : __("Support Services"),
}));
</script>
