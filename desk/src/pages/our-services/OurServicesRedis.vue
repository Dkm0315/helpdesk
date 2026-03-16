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
      <!-- Page Title -->
      <div>
        <h1 class="text-xl font-semibold text-gray-900">{{ __("Redis Support Services") }}</h1>
        <p class="text-sm text-gray-600 mt-1">
          {{ __("Comprehensive support structure for Redis environments including operations, expert support, advisory, and professional services.") }}
        </p>
      </div>

      <!-- SLA Disclaimer -->
      <div class="border border-gray-200 rounded-lg p-4 bg-gray-50 text-sm text-gray-500 italic">
        {{ __("The support services described herein are subject to the terms and conditions outlined in your service agreement. SLA commitments apply only to environments and technologies covered under your active contract. Response and resolution times are best-effort targets unless otherwise specified in a signed SLA document.") }}
      </div>

      <!-- L1 - Redis Operations -->
      <div class="border rounded-lg p-4 bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-900">{{ __("L1 - Redis Operations (Customer/Shared Ops Team)") }}</h2>
        <p class="text-sm text-gray-600 mt-2">
          <span class="font-medium text-gray-800">{{ __("Primary Role:") }}</span>
          {{ __("First-line monitoring and basic operations") }}
        </p>
        <h3 class="text-base font-medium text-gray-800 mt-4">{{ __("Responsibilities") }}</h3>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-2">
          <li>{{ __("Monitor Redis dashboards and alerts via OSS Manager") }}</li>
          <li>{{ __("Perform basic operational checks: Redis process status, disk space availability, node reachability") }}</li>
          <li>{{ __("Execute documented SOPs and runbooks") }}</li>
          <li>{{ __("Restart Redis services as per approved procedures") }}</li>
          <li>{{ __("Collect logs and diagnostics during incidents") }}</li>
          <li>{{ __("Escalate issues to L2 with relevant details") }}</li>
        </ul>
        <div class="mt-4 pt-3 border-t border-gray-200">
          <p class="text-sm text-gray-600">
            <span class="font-medium text-gray-800">{{ __("Out of Scope:") }}</span>
            {{ __("Configuration tuning, root cause analysis, architecture changes, version upgrades") }}
          </p>
        </div>
      </div>

      <!-- L2 - Redis OSS Expert Support -->
      <div class="border rounded-lg p-4 bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-900">{{ __("L2 - Redis OSS Expert Support (Provided by Us)") }}</h2>
        <p class="text-sm text-gray-600 mt-2">
          <span class="font-medium text-gray-800">{{ __("Primary Role:") }}</span>
          {{ __("Operational issue resolution and stability assurance") }}
        </p>
        <h3 class="text-base font-medium text-gray-800 mt-4">{{ __("Responsibilities") }}</h3>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-2">
          <li>
            {{ __("Incident analysis and resolution for:") }}
            <ul class="list-disc pl-5 mt-1 space-y-1">
              <li>{{ __("Redis availability issues") }}</li>
              <li>{{ __("Replication lag or replica sync failures") }}</li>
              <li>{{ __("Memory pressure or eviction issues") }}</li>
              <li>{{ __("Performance degradation") }}</li>
            </ul>
          </li>
          <li>{{ __("Redis configuration tuning and optimization") }}</li>
          <li>{{ __("Failover and recovery guidance") }}</li>
          <li>{{ __("Backup and restore advisory support") }}</li>
          <li>{{ __("Post-upgrade stabilization") }}</li>
          <li>{{ __("Proactive recommendations using OSS Manager insights") }}</li>
          <li>{{ __("Root cause analysis (RCA) and corrective action guidance") }}</li>
        </ul>
        <h3 class="text-base font-medium text-gray-800 mt-4">{{ __("Tools & Methods") }}</h3>
        <p class="text-sm text-gray-600 mt-1">
          {{ __("OSS Manager dashboards & alerts, Redis logs & metrics, configuration reviews, best-practice advisory") }}
        </p>
        <div class="mt-4 pt-3 border-t border-gray-200">
          <p class="text-sm text-gray-600">
            <span class="font-medium text-gray-800">{{ __("Out of Scope:") }}</span>
            {{ __("Redis source code changes, OSS bug fixes, product-level enhancements") }}
          </p>
        </div>
      </div>

      <!-- L3 - Advanced Redis Advisory -->
      <div class="border rounded-lg p-4 bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-900">{{ __("L3 - Advanced Redis Advisory (Best-Effort)") }}</h2>
        <p class="text-sm text-gray-600 mt-2">
          <span class="font-medium text-gray-800">{{ __("Primary Role:") }}</span>
          {{ __("Deep technical advisory and escalation support") }}
        </p>
        <h3 class="text-base font-medium text-gray-800 mt-4">{{ __("Responsibilities") }}</h3>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-2">
          <li>{{ __("Complex issue analysis and workaround identification") }}</li>
          <li>{{ __("Advanced performance and memory tuning advisory") }}</li>
          <li>{{ __("Redis internals-level guidance (best-effort)") }}</li>
          <li>{{ __("Upgrade path validation and risk assessment") }}</li>
          <li>{{ __("Support in engaging Redis OSS community or enterprise vendors if required") }}</li>
          <li>{{ __("Architecture re-evaluation recommendations") }}</li>
        </ul>
        <div class="mt-4 pt-3 border-t border-gray-200">
          <p class="text-sm text-gray-500 italic">
            {{ __("Note: L3 support is advisory and does not include ownership of OSS code fixes.") }}
          </p>
        </div>
      </div>

      <!-- Redis Professional Services -->
      <div class="border rounded-lg p-4 bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Redis Professional Services") }}</h2>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-3">
          <li>{{ __("Redis use-case solutioning and high-level architecture (under Solution Architect guidance)") }}</li>
          <li>{{ __("Proof-of-Concept (PoC) execution and validation") }}</li>
          <li>{{ __("Integration evaluation with applications and systems") }}</li>
          <li>{{ __("OSS Manager installation and checks") }}</li>
          <li>{{ __("Redis setup, configuration, and sanity testing") }}</li>
          <li>{{ __("Connector customization (if required)") }}</li>
          <li>{{ __("Data migration planning and execution") }}</li>
          <li>{{ __("Redis version upgrades and migration execution") }}</li>
          <li>{{ __("Performance benchmarking and validation") }}</li>
          <li>{{ __("Knowledge transfer to operations and development teams") }}</li>
        </ul>
        <h3 class="text-base font-medium text-gray-800 mt-4">{{ __("Deliverables") }}</h3>
        <p class="text-sm text-gray-600 mt-1">
          {{ __("Working Redis environments, configuration documentation, migration and validation reports, runbooks and SOPs") }}
        </p>
      </div>

      <!-- Redis Solution Architect -->
      <div class="border rounded-lg p-4 bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Redis Solution Architect") }}</h2>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-3">
          <li>{{ __("Architecture and design of Redis use cases") }}</li>
          <li>{{ __("Requirements assessment and solution definition") }}</li>
          <li>{{ __("Redis deployment topology recommendations") }}</li>
          <li>{{ __("Performance, scalability, and resilience design") }}</li>
          <li>{{ __("Redis best practices and design reviews") }}</li>
          <li>{{ __("Security and access pattern recommendations") }}</li>
          <li>{{ __("Upgrade and modernization strategy") }}</li>
          <li>{{ __("Redis developer training sessions") }}</li>
          <li>{{ __("Review and validation of PoCs and implementations") }}</li>
        </ul>
      </div>

      <!-- Hypercare Plan -->
      <div class="border rounded-lg p-4 bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Hypercare Plan (3 Months)") }}</h2>
        <div class="mt-3 space-y-4">
          <div>
            <h3 class="text-base font-medium text-gray-800">{{ __("Month 1") }}</h3>
            <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-1">
              <li>{{ __("High-touch support post go-live") }}</li>
              <li>{{ __("Daily monitoring and proactive checks") }}</li>
              <li>{{ __("Weekly review calls") }}</li>
            </ul>
          </div>
          <div>
            <h3 class="text-base font-medium text-gray-800">{{ __("Month 2") }}</h3>
            <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-1">
              <li>{{ __("Stability monitoring") }}</li>
              <li>{{ __("Performance tuning recommendations") }}</li>
              <li>{{ __("Fortnightly reviews") }}</li>
            </ul>
          </div>
          <div>
            <h3 class="text-base font-medium text-gray-800">{{ __("Month 3") }}</h3>
            <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-1">
              <li>{{ __("Operational maturity assessment") }}</li>
              <li>{{ __("Knowledge transfer and handover") }}</li>
              <li>{{ __("Final support summary") }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Responsibility Matrix -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Responsibility Matrix") }}</h2>
        <div class="mt-3 overflow-x-auto">
          <table class="w-full text-sm border border-gray-200 rounded-lg">
            <thead>
              <tr class="bg-gray-50">
                <th class="text-left p-3 border-b border-r border-gray-200 font-medium text-gray-800">{{ __("Area") }}</th>
                <th class="text-center p-3 border-b border-r border-gray-200 font-medium text-gray-800">{{ __("L1") }}</th>
                <th class="text-center p-3 border-b border-r border-gray-200 font-medium text-gray-800">{{ __("L2") }}</th>
                <th class="text-center p-3 border-b border-r border-gray-200 font-medium text-gray-800">{{ __("L3") }}</th>
                <th class="text-center p-3 border-b border-r border-gray-200 font-medium text-gray-800">{{ __("PS") }}</th>
                <th class="text-center p-3 border-b border-gray-200 font-medium text-gray-800">{{ __("SA") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="p-3 border-b border-r border-gray-200 text-gray-700">{{ __("Monitoring & Alerts") }}</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-gray-200 text-center text-red-400">&#10007;</td>
              </tr>
              <tr class="bg-gray-50">
                <td class="p-3 border-b border-r border-gray-200 text-gray-700">{{ __("Incident Resolution") }}</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-gray-200 text-center text-red-400">&#10007;</td>
              </tr>
              <tr>
                <td class="p-3 border-b border-r border-gray-200 text-gray-700">{{ __("Config Tuning") }}</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-gray-200 text-center text-red-400">&#10007;</td>
              </tr>
              <tr class="bg-gray-50">
                <td class="p-3 border-b border-r border-gray-200 text-gray-700">{{ __("Migration & Upgrade") }}</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-yellow-500 text-xs">{{ __("Advisory") }}</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-gray-200 text-center text-green-600">&#10003;</td>
              </tr>
              <tr>
                <td class="p-3 border-b border-r border-gray-200 text-gray-700">{{ __("Architecture Design") }}</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-yellow-500 text-xs">{{ __("Advisory") }}</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-gray-200 text-center text-green-600">&#10003;</td>
              </tr>
              <tr class="bg-gray-50">
                <td class="p-3 border-b border-r border-gray-200 text-gray-700">{{ __("PoC & Integrations") }}</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-b border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 border-b border-gray-200 text-center text-green-600">&#10003;</td>
              </tr>
              <tr>
                <td class="p-3 border-r border-gray-200 text-gray-700">{{ __("Training & KT") }}</td>
                <td class="p-3 border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-r border-gray-200 text-center text-red-400">&#10007;</td>
                <td class="p-3 border-r border-gray-200 text-center text-green-600">&#10003;</td>
                <td class="p-3 text-center text-green-600">&#10003;</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Communication & Escalation -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Communication & Escalation") }}</h2>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-3">
          <li>{{ __("Dedicated support channel (Email/Portal)") }}</li>
          <li>{{ __("Defined escalation matrix") }}</li>
          <li>{{ __("Incident tracking and RCA sharing") }}</li>
        </ul>
      </div>

      <!-- Deliverables -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ __("Deliverables") }}</h2>
        <ul class="list-disc pl-5 text-sm text-gray-600 space-y-1 mt-3">
          <li>{{ __("Support runbooks and SOPs") }}</li>
          <li>{{ __("Hypercare reports") }}</li>
          <li>{{ __("RCA documentation") }}</li>
          <li>{{ __("Knowledge transfer materials") }}</li>
        </ul>
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

const breadcrumbs = computed(() => [
  {
    label: __("Our Services"),
    route: {
      name: isCustomerPortal.value ? "OurServices" : "OurServicesAgent",
    },
  },
  {
    label: __("Redis"),
    route: {
      name: isCustomerPortal.value
        ? "OurServicesRedis"
        : "OurServicesRedisAgent",
    },
  },
]);

usePageMeta(() => ({
  title: __("Redis Support Services"),
}));
</script>
