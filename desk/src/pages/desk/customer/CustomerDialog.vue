<template>
  <Dialog :options="options">
    <template #body-main>
      <div class="max-h-[80vh] overflow-auto">
        <div class="flex flex-col items-center gap-4 p-6">
          <div class="text-xl font-medium text-gray-900">
            {{ customer.doc?.name }}
          </div>
          <Avatar
            size="lg"
            :label="customer.doc?.name"
            :image="customer.doc?.image"
            class="cursor-pointer hover:opacity-80"
          />
          <div class="flex gap-2">
            <FileUploader @success="(file) => updateImage(file)">
              <template #default="{ uploading, openFileSelector }">
                <Button
                  :label="customer.doc?.image ? 'Change photo' : 'Upload photo'"
                  :loading="uploading"
                  @click="openFileSelector"
                />
              </template>
            </FileUploader>
            <Button
              v-if="customer.doc?.image"
              label="Remove photo"
              @click="updateImage(null)"
            />
          </div>
          <form class="w-full" @submit.prevent="update">
            <Input v-model="domain" label="Domain" placeholder="example.com" />
          </form>
        </div>

        <section v-if="isSystemManager" class="border-t bg-surface-gray-1 p-5">
          <div class="mb-4 flex items-center justify-between gap-3">
            <div>
              <div class="text-base font-semibold text-ink-gray-9">
                Customer Intelligence
              </div>
              <p class="mt-1 text-sm text-ink-gray-5">
                System Manager-only lifecycle, sizing, hours, and credential metadata.
              </p>
            </div>
            <Button
              label="Refresh"
              theme="gray"
              size="sm"
              :loading="customerIntelligence.loading"
              @click="customerIntelligence.reload()"
            />
          </div>

          <ErrorMessage
            v-if="customerIntelligence.error"
            class="mb-3"
            :message="customerIntelligence.error.messages?.[0] || customerIntelligence.error.message"
          />
          <div
            v-if="customerIntelligence.loading"
            class="rounded-xl border bg-white p-4 text-sm text-ink-gray-5"
          >
            Loading customer intelligence...
          </div>

          <div v-else class="grid gap-4 lg:grid-cols-2">
            <DetailCard title="Licenses" :rows="customerIntelligence.data?.licenses">
              <template #row="{ row }">
                <div class="font-medium text-ink-gray-9">{{ row.product || row.name }}</div>
                <div class="text-xs text-ink-gray-5">
                  {{ row.license_type || 'License' }} · {{ row.status || 'Unknown' }} · expires {{ row.expires_on || 'not set' }}
                </div>
              </template>
            </DetailCard>

            <DetailCard title="Support Hours" :rows="customerIntelligence.data?.hours_ledgers">
              <template #row="{ row }">
                <div class="font-medium text-ink-gray-9">{{ row.agreement_label || row.name }}</div>
                <div class="text-xs text-ink-gray-5">
                  {{ row.hours_remaining ?? 0 }}h remaining of {{ row.opening_hours ?? 0 }}h · {{ row.status || 'Unknown' }}
                </div>
              </template>
            </DetailCard>

            <DetailCard title="Sizing Profiles" :rows="customerIntelligence.data?.sizing_profiles">
              <template #row="{ row }">
                <div class="font-medium text-ink-gray-9">{{ row.environment_label || row.name }}</div>
                <div class="text-xs text-ink-gray-5">
                  {{ row.engine || 'Engine unknown' }} · {{ row.topology || 'Topology unknown' }} · {{ row.nodes || 0 }} nodes
                </div>
              </template>
            </DetailCard>

            <DetailCard title="Credentials" :rows="customerIntelligence.data?.credentials">
              <template #row="{ row }">
                <div class="font-medium text-ink-gray-9">{{ row.credential_label || row.name }}</div>
                <div class="text-xs text-ink-gray-5">
                  {{ row.credential_type || 'Credential' }} · {{ row.environment_label || 'No env' }} · secrets redacted
                </div>
              </template>
            </DetailCard>
          </div>
        </section>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import {
  Avatar,
  createDocumentResource,
  createResource,
  Dialog,
  ErrorMessage,
  FileUploader,
  toast,
} from "frappe-ui";
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import DetailCard from "./DetailCard.vue";

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["customer-updated"]);
const authStore = useAuthStore();
const isSystemManager = computed(() => authStore.isAdmin);

const domain = computed({
  get() {
    return customer.doc?.domain;
  },
  set(d: string) {
    customer.doc.domain = d;
  },
});

const customer = createDocumentResource({
  doctype: "HD Customer",
  name: props.name,
  auto: true,
  setValue: {
    onSuccess() {
      toast.success("Customer updated");
    },
    onError() {
      toast.error("Error updating customer");
    },
  },
});

const customerIntelligence = createResource({
  url: "quant_customizations.api.customer_lifecycle.get_customer_intelligence",
  makeParams() {
    return {
      customer: props.name,
    };
  },
  auto: isSystemManager.value,
});

const options = computed(() => ({
  title: customer.doc?.name,
  actions: [
    {
      label: "Save",
      theme: "gray",
      variant: "solid",
      onClick: () => update(),
    },
  ],
}));

async function update() {
  await customer.setValue.submit({
    domain: domain.value,
  });
  emit("customer-updated");
}

function updateImage(file) {
  customer.setValue.submit({
    image: file?.file_url || null,
  });
  emit("customer-updated");
}
</script>
