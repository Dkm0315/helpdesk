<template>
  <div class="flex flex-col h-full">
    <div class="p-6 border-b">
      <h3 class="text-lg font-semibold text-gray-900">Resolution Details</h3>
      <p class="text-sm text-gray-600 mt-1">
        Provide detailed information about how this ticket was resolved.
      </p>
    </div>

    <div v-if="ticket.status === 'Resolved' || ticket.status === 'Closed'" class="flex-1 p-6">
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <div class="flex items-start">
          <TicketIcon class="h-5 w-5 text-green-600 mt-0.5 mr-3" />
          <div class="flex-1">
            <h4 class="text-sm font-medium text-green-800">
              {{ ticket.status === 'Closed' ? 'Ticket Closed' : 'Ticket Resolved' }}
            </h4>
            <div class="mt-2 text-sm text-green-700" v-html="ticket.resolution_details || 'No resolution details provided.'">
            </div>
            <div class="mt-3 text-xs text-green-600">
              {{ ticket.status === 'Closed' ? 'Closed' : 'Resolved' }} on {{ formatDate(ticket.resolution_date || ticket.modified) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="flex-1 overflow-hidden">
      <div class="h-full flex flex-col">
        <div class="flex-1 overflow-hidden">
          <TextEditor
            ref="editorRef"
            v-model="resolutionDetails"
            :editor-class="'prose-sm max-w-full mx-6 py-3 min-h-[20rem] max-h-[calc(100vh-300px)] overflow-y-auto'"
            placeholder="Provide detailed resolution information..."
            autofocus
            @change="resolutionDetails = $event"
          >
            <template #bottom-right>
              <Button
                label="Submit Resolution"
                variant="solid"
                theme="green"
                :loading="isSubmitting"
                :disabled="!resolutionDetails || resolutionDetails.trim() === '' || resolutionDetails.trim() === '<p></p>'"
                @click="submitResolution"
              />
            </template>
          </TextEditor>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, call, toast } from "frappe-ui";
import { TextEditor } from "@/components";
import { TicketIcon } from "@/components/icons";

interface Props {
  ticket: any;
  ticketId: string;
}

interface Emits {
  (event: "update"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const resolutionDetails = ref(`<h3>Resolution Summary</h3>

<p><strong>Issue:</strong> Brief description of the problem</p>

<p><strong>Solution:</strong></p>
<ul>
<li>Step 1: What was done</li>
<li>Step 2: Additional actions taken</li>
</ul>

<p><strong>Result:</strong> Issue resolved successfully</p>

<p><strong>Notes:</strong> Any additional information...</p>`);

const isSubmitting = ref(false);

async function submitResolution() {
  if (!resolutionDetails.value.trim() || resolutionDetails.value.trim() === '<p></p>') {
    toast.error("Resolution details are required");
    return;
  }

  try {
    isSubmitting.value = true;

    // First update the resolution_details field
    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketId,
      fieldname: "resolution_details",
      value: resolutionDetails.value,
    });

    // Then update the status to Resolved
    await call("frappe.client.set_value", {
      doctype: "HD Ticket",
      name: props.ticketId,
      fieldname: "status",
      value: "Resolved",
    });

    toast.success("Ticket marked as resolved");
    emit("update");
  } catch (err) {
    toast.error(err.message || "Failed to resolve ticket");
  } finally {
    isSubmitting.value = false;
  }
}

function formatDate(dateString: string) {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString();
}
</script>