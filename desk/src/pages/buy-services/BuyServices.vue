<template>
  <div class="flex flex-col overflow-y-auto">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
    </LayoutHeader>
    <div class="flex flex-col gap-5 py-6 h-full flex-1 self-center overflow-auto mx-auto w-full max-w-4xl px-5">
      <!-- Page description -->
      <div>
        <h2 class="text-xl font-semibold text-gray-900">{{ __("Request a Service") }}</h2>
        <p class="text-sm text-gray-600 mt-1">
          {{ __("Select a service, provide details, and we will create a support ticket to track your request.") }}
        </p>
      </div>

      <!-- Form fields -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <!-- Service Type -->
        <div class="flex flex-col gap-2 sm:col-span-2">
          <span class="block text-sm text-gray-700">
            {{ __("Service Type") }}
            <span class="text-red-500"> * </span>
          </span>
          <FormControl
            v-model="serviceType"
            type="select"
            :options="serviceOptions"
            :placeholder="__('Select a service')"
          />
        </div>

        <!-- Tentative Hours -->
        <div class="flex flex-col gap-2">
          <span class="block text-sm text-gray-700">
            {{ __("Tentative Hours") }}
            <span class="text-red-500"> * </span>
          </span>
          <FormControl
            v-model="tentativeHours"
            type="number"
            :placeholder="__('e.g. 40')"
          />
        </div>

        <!-- Start Date -->
        <div class="flex flex-col gap-2">
          <span class="block text-sm text-gray-700">
            {{ __("Preferred Start Date") }}
            <span class="text-red-500"> * </span>
          </span>
          <FormControl
            v-model="startDate"
            type="date"
          />
        </div>

        <!-- Requirements -->
        <div class="flex flex-col gap-2 sm:col-span-2">
          <span class="block text-sm text-gray-700">
            {{ __("Requirements") }}
            <span class="text-red-500"> * </span>
          </span>
          <FormControl
            v-model="requirements"
            type="textarea"
            :placeholder="__('Describe your requirements in detail...')"
            :rows="6"
          />
        </div>
      </div>

      <!-- Submit button -->
      <div class="flex justify-end">
        <Button
          :label="__('Submit Request')"
          theme="gray"
          variant="solid"
          :disabled="!isFormValid || serviceTicket.loading"
          :loading="serviceTicket.loading"
          @click="serviceTicket.submit()"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader } from "@/components";
import { __ } from "@/translation";
import { isCustomerPortal } from "@/utils";
import { useAuthStore } from "@/stores/auth";
import {
  Breadcrumbs,
  Button,
  FormControl,
  createResource,
  usePageMeta,
} from "frappe-ui";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const serviceType = ref("");
const tentativeHours = ref("");
const startDate = ref("");
const requirements = ref("");

const serviceOptions = [
  { label: __("Solution Architect Consultancy"), value: "Solution Architect Consultancy" },
  { label: __("Professional Services"), value: "Professional Services" },
  { label: __("Support Hours"), value: "Support Hours" },
];

const isFormValid = computed(() => {
  return (
    serviceType.value &&
    tentativeHours.value &&
    startDate.value &&
    requirements.value.trim()
  );
});

function buildDescription() {
  return `<p><strong>Service Type:</strong> ${serviceType.value}</p>
<p><strong>Tentative Hours:</strong> ${tentativeHours.value}</p>
<p><strong>Preferred Start Date:</strong> ${startDate.value}</p>
<h4>Requirements</h4>
<p>${requirements.value.replace(/\n/g, "<br>")}</p>`;
}

const serviceTicket = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.new",
  makeParams: () => ({
    doc: {
      subject: `[Service Request] ${serviceType.value}`,
      description: buildDescription(),
      ticket_type: "Service Request",
    },
  }),
  onSuccess: (data: any) => {
    const { isAgent } = useAuthStore();
    router.push({
      name: isAgent ? "TicketAgent" : "TicketCustomer",
      params: { ticketId: data.name },
    });
  },
});

const breadcrumbs = computed(() => [
  {
    label: __("Buy Services"),
    route: {
      name: isCustomerPortal.value ? "BuyServices" : "BuyServicesAgent",
    },
  },
]);

usePageMeta(() => ({
  title: __("Buy Services"),
}));
</script>
