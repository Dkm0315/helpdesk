<template>
  <div class="flex flex-col overflow-y-auto">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
    </LayoutHeader>
    <div
      class="flex flex-col gap-6 py-6 h-full flex-1 self-center overflow-auto mx-auto w-full max-w-4xl px-5"
    >
      <!-- SLA Disclaimer -->
      <div class="border border-gray-200 rounded-lg p-4 bg-gray-50 text-sm text-gray-500 italic">
        {{ __("The support services described herein are subject to the terms and conditions outlined in your service agreement. SLA commitments apply only to environments and technologies covered under your active contract. Response and resolution times are best-effort targets unless otherwise specified in a signed SLA document.") }}
      </div>

      <!-- Support Metrics -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Support Metrics") }}</h2>
        <p class="text-sm text-gray-600 mt-1">
          {{ __("Our standard response time commitments based on environment type.") }}
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
          <!-- Non-production -->
          <div class="border rounded-lg p-5 bg-gray-50">
            <h3 class="text-base font-medium text-gray-800">{{ __("Non-Production") }}</h3>
            <div class="mt-3 space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">{{ __("Response Time") }}</span>
                <span class="font-medium text-gray-900">{{ __("4 Hours") }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">{{ __("Availability") }}</span>
                <span class="font-medium text-gray-900">{{ __("Business Hours") }}</span>
              </div>
            </div>
          </div>
          <!-- Production -->
          <div class="border rounded-lg p-5 bg-gray-50">
            <h3 class="text-base font-medium text-gray-800">{{ __("Production") }}</h3>
            <div class="mt-3 space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">{{ __("Response Time") }}</span>
                <span class="font-medium text-gray-900">{{ __("1 Hour") }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">{{ __("Availability") }}</span>
                <span class="font-medium text-gray-900">{{ __("24/7") }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Engagement Model -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Engagement Model") }}</h2>
        <p class="text-sm text-gray-600 mt-2">
          {{ __("Our support is structured across multiple tiers to ensure comprehensive coverage, from day-to-day operations through to advanced advisory and professional services.") }}
        </p>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-2">
          <li>{{ __("L1 - Operations: First-line monitoring, basic checks, and documented runbook execution (Customer/Shared Ops Team)") }}</li>
          <li>{{ __("L2 - Expert Support: Incident analysis, configuration tuning, failover guidance, and proactive recommendations (Provided by Us)") }}</li>
          <li>{{ __("L3 - Advanced Advisory: Deep technical advisory, complex issue analysis, and upgrade path validation (Best-Effort)") }}</li>
          <li>{{ __("Professional Services: Implementation, migration, benchmarking, and knowledge transfer engagements") }}</li>
          <li>{{ __("Solution Architect: Architecture design, requirements assessment, best practices reviews, and training") }}</li>
        </ul>
      </div>

      <!-- Technology Cards -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Supported Technologies") }}</h2>
        <p class="text-sm text-gray-600 mt-1">
          {{ __("Select a technology to view detailed support structure, responsibilities, and service descriptions.") }}
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
          <!-- Redis -->
          <RouterLink
            :to="{ name: redisRoute }"
            class="border rounded-lg p-5 hover:shadow-md hover:border-gray-300 transition cursor-pointer block"
          >
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
                <span class="text-red-600 font-bold text-lg">R</span>
              </div>
              <h3 class="text-base font-medium text-gray-900">{{ __("Redis") }}</h3>
            </div>
            <p class="text-sm text-gray-600">
              {{ __("In-memory data store support including replication, failover, memory management, and performance optimization.") }}
            </p>
            <span class="text-sm font-medium text-blue-600 mt-3 inline-block">{{ __("View Details") }} &rarr;</span>
          </RouterLink>

          <!-- Kafka -->
          <RouterLink
            :to="{ name: kafkaRoute }"
            class="border rounded-lg p-5 hover:shadow-md hover:border-gray-300 transition cursor-pointer block"
          >
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
                <span class="text-orange-600 font-bold text-lg">K</span>
              </div>
              <h3 class="text-base font-medium text-gray-900">{{ __("Kafka") }}</h3>
            </div>
            <p class="text-sm text-gray-600">
              {{ __("Distributed event streaming platform support including broker management, partition strategy, and KRaft migration.") }}
            </p>
            <span class="text-sm font-medium text-blue-600 mt-3 inline-block">{{ __("View Details") }} &rarr;</span>
          </RouterLink>

          <!-- MongoDB -->
          <RouterLink
            :to="{ name: mongoRoute }"
            class="border rounded-lg p-5 hover:shadow-md hover:border-gray-300 transition cursor-pointer block"
          >
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                <span class="text-green-600 font-bold text-lg">M</span>
              </div>
              <h3 class="text-base font-medium text-gray-900">{{ __("MongoDB") }}</h3>
            </div>
            <p class="text-sm text-gray-600">
              {{ __("Document database support including replica sets, WiredTiger tuning, sharding advisory, and security configuration.") }}
            </p>
            <span class="text-sm font-medium text-blue-600 mt-3 inline-block">{{ __("View Details") }} &rarr;</span>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader } from "@/components";
import { __ } from "@/translation";
import { isCustomerPortal } from "@/utils";
import { Breadcrumbs, usePageMeta } from "frappe-ui";
import { computed } from "vue";

const redisRoute = computed(() =>
  isCustomerPortal.value ? "OurServicesRedis" : "OurServicesRedisAgent"
);
const kafkaRoute = computed(() =>
  isCustomerPortal.value ? "OurServicesKafka" : "OurServicesKafkaAgent"
);
const mongoRoute = computed(() =>
  isCustomerPortal.value ? "OurServicesMongoDB" : "OurServicesMongoDBAgent"
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
