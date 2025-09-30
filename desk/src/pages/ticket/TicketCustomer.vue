<template>
  <div v-if="ticket.data" class="flex flex-col">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
      <template #right-header>
        <CustomActions
          v-if="ticket.data._customActions"
          :actions="ticket.data._customActions"
        />
        <Button
          v-if="ticket.data.status === 'Replied'"
          label="Resolve"
          theme="green"
          variant="solid"
          @click="triggerResolve()"
        >
          <template #prefix>
            <Icon icon="lucide:check-circle" />
          </template>
        </Button>
        <Button
          v-else-if="isRaiser && ticket.data.status !== 'Closed'"
          label="Close"
          theme="red"
          variant="solid"
          @click="triggerClose()"
        >
          <template #prefix>
            <Icon icon="lucide:check" />
          </template>
        </Button>
        <Button
          v-else-if="!isRaiser && ticket.data.status !== 'Closed'"
          label="Request Closure"
          theme="gray"
          variant="solid"
          @click="triggerRequestClosure()"
        />
      </template>
    </LayoutHeader>
    <div class="flex overflow-hidden h-full w-full">
      <!-- Main Ticket Comm -->
      <section class="flex flex-col flex-1 w-full md:max-w-[calc(100%-382px)]">
        <!-- show for only mobile -->
        <TicketCustomerTemplateFields v-if="isMobileView" />

        <TicketConversation class="grow" />
        <div
          class="w-full p-5"
          @keydown.ctrl.enter.capture.stop="sendEmail"
          @keydown.meta.enter.capture.stop="sendEmail"
        >
          <TicketTextEditor
            v-if="showEditor"
            ref="editor"
            v-model:attachments="attachments"
            v-model:content="editorContent"
            v-model:expand="isExpanded"
            placeholder="Type a message"
            autofocus
            @clear="() => (isExpanded = false)"
            :uploadFunction="(file:any)=>uploadFunction(file, 'HD Ticket', props.ticketId)"
          >
            <template #bottom-right>
              <Button
                label="Send"
                theme="gray"
                variant="solid"
                :disabled="$refs.editor?.editor.isEmpty || send.loading"
                :loading="send.loading"
                @click="sendEmail"
              />
            </template>
          </TicketTextEditor>
        </div>
      </section>
      <!-- Ticket Sidebar only for desktop view-->
      <TicketCustomerSidebar v-if="!isMobileView" @open="isExpanded = true" />
    </div>
    <TicketFeedback v-model:open="showFeedbackDialog" />
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader, TextEditor } from "@/components";
import TicketCustomerSidebar from "@/components/ticket/TicketCustomerSidebar.vue";
import { setupCustomizations } from "@/composables/formCustomisation";
import { useScreenSize } from "@/composables/screen";
import { socket } from "@/socket";
import { useConfigStore } from "@/stores/config";
import { globalStore } from "@/stores/globalStore";
import { isContentEmpty, uploadFunction } from "@/utils";
import { Icon } from "@iconify/vue";
import { Breadcrumbs, Button, FormControl, call, createResource, toast } from "frappe-ui";
import { computed, onMounted, onUnmounted, provide, ref } from "vue";
import { useRouter } from "vue-router";
import { useTicket } from "./data";
import { useAuthStore } from "@/stores/auth";
import { ITicket } from "./symbols";
import TicketCustomerTemplateFields from "./TicketCustomerTemplateFields.vue";
import TicketConversation from "./TicketConversation.vue";
import TicketFeedback from "./TicketFeedback.vue";
import TicketTextEditor from "./TicketTextEditor.vue";

interface P {
  ticketId: string;
}
const router = useRouter();

const props = defineProps<P>();
const ticket = useTicket(
  props.ticketId,
  true,
  null,
  (data) => {
    setupCustomizations(ticket, {
      doc: data,
      call,
      router,
      toast,
      $dialog,
      updateField,
      createToast: toast.create,
    });
  },
  () => {
    toast.error("Ticket not found");
    router.replace("/my-tickets");
  }
);
provide(ITicket, ticket);
const editor = ref(null);
const editorContent = ref("");
const attachments = ref([]);
const showFeedbackDialog = ref(false);
const isExpanded = ref(false);

const { isMobileView } = useScreenSize();
const { $dialog } = globalStore();
const { userId } = useAuthStore();

const send = createResource({
  url: "run_doc_method",
  debounce: 300,
  makeParams: () => ({
    dt: "HD Ticket",
    dn: props.ticketId,
    method: "create_communication_via_contact",
    args: {
      message: editorContent.value,
      attachments: attachments.value,
    },
  }),
  onSuccess: () => {
    editor.value.editor.commands.clearContent(true);
    attachments.value = [];
    isExpanded.value = false;
    ticket.reload();
  },
});

function updateField(name, value, callback = () => {}) {
  updateTicket(name, value);
  callback();
}

function sendEmail() {
  if (isContentEmpty(editorContent.value) || send.loading) {
    return;
  }
  send.submit();
}

function updateTicket(fieldname: string, value: string) {
  createResource({
    url: "frappe.client.set_value",
    params: {
      doctype: "HD Ticket",
      name: props.ticketId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      ticket.reload();
      toast.success("Ticket updated");
    },
  });
}

const isRaiser = computed(() => {
  if (!ticket.data) return false;
  return (userId as any).value === ticket.data.raised_by;
});

function triggerClose() {
  $dialog({
    title: "Close Ticket",
    message: "Please provide resolution details to close this ticket.",
    actions: [],
    render: ({ close }) => {
      const notes = ref("");
      const isLoading = ref(false);
      const error = ref("");

      return h("div", { class: "flex flex-col gap-3" }, [
        error.value && h("div", {
          class: "text-red-600 text-sm p-2 bg-red-50 border border-red-200 rounded"
        }, error.value),
        h(FormControl, {
          type: "textarea",
          placeholder: "Describe how this ticket was resolved...",
          rows: 4,
          modelValue: notes.value,
          "onUpdate:modelValue": (v: string) => {
            notes.value = v;
            error.value = "";
          },
        }),
        h("div", { class: "flex gap-2 justify-end" }, [
          h(
            Button,
            {
              variant: "subtle",
              label: "Cancel",
              onClick: close,
            },
            {}
          ),
          h(
            Button,
            {
              variant: "solid",
              theme: "red",
              label: "Close Ticket",
              loading: isLoading.value,
              onClick: async () => {
                if (!notes.value.trim()) {
                  error.value = "Resolution details are required";
                  return;
                }

                try {
                  isLoading.value = true;
                  await call("pw_helpdesk.customizations.ticket_closure_workflow.mark_as_resolved", {
                    ticket_id: props.ticketId,
                    resolution_notes: notes.value,
                  });
                  toast.success("Ticket closed successfully");
                  ticket.reload();
                  close();
                } catch (err) {
                  error.value = err.message || "Failed to close ticket";
                } finally {
                  isLoading.value = false;
                }
              },
            },
            {}
          ),
        ]),
      ]);
    },
  });
}

function triggerResolve() {
  $dialog({
    title: "Resolve Ticket",
    message: "Provide detailed resolution information below.",
    actions: [],
    render: ({ close }) => {
      const resolutionDetails = ref(`Resolution Summary

Issue: Brief description of the problem

Solution:
- Step 1: What was done
- Step 2: Additional actions taken

Result: Issue resolved successfully

Notes: Any additional information...`);
      const isLoading = ref(false);
      const error = ref("");

      return h("div", { class: "flex flex-col gap-3" }, [
        error.value && h("div", {
          class: "text-red-600 text-sm p-2 bg-red-50 border border-red-200 rounded"
        }, error.value),
        h("div", { class: "text-sm text-gray-600 mb-2" }, "Provide detailed resolution information."),
        h(FormControl, {
          type: "textarea",
          placeholder: "Provide detailed resolution information...",
          rows: 8,
          modelValue: resolutionDetails.value,
          "onUpdate:modelValue": (v: string) => {
            resolutionDetails.value = v;
            error.value = "";
          },
        }),
        h("div", { class: "flex gap-2 justify-end mt-4" }, [
          h(
            Button,
            {
              variant: "subtle",
              label: "Cancel",
              onClick: close,
            },
            {}
          ),
          h(
            Button,
            {
              variant: "solid",
              theme: "green",
              label: "Resolve Ticket",
              loading: isLoading.value,
              onClick: async () => {
                if (!resolutionDetails.value.trim() || resolutionDetails.value.trim() === "<p></p>") {
                  error.value = "Resolution details are required";
                  return;
                }

                try {
                  isLoading.value = true;
                  await call("pw_helpdesk.customizations.ticket_closure_workflow.mark_as_resolved", {
                    ticket_id: props.ticketId,
                    resolution_notes: resolutionDetails.value,
                  });
                  toast.success("Ticket resolved successfully");
                  ticket.reload();
                  close();
                } catch (err) {
                  error.value = err.message || "Failed to resolve ticket";
                } finally {
                  isLoading.value = false;
                }
              },
            },
            {}
          ),
        ]),
      ]);
    },
  });
}

function triggerRequestClosure() {
  $dialog({
    title: "Request Closure",
    message: "Request that this ticket be closed by providing resolution details.",
    actions: [],
    render: ({ close }) => {
      const notes = ref("");
      const isLoading = ref(false);
      const error = ref("");

      return h("div", { class: "flex flex-col gap-3" }, [
        error.value && h("div", {
          class: "text-red-600 text-sm p-2 bg-red-50 border border-red-200 rounded"
        }, error.value),
        h(FormControl, {
          type: "textarea",
          placeholder: "Describe how this ticket was resolved...",
          rows: 4,
          modelValue: notes.value,
          "onUpdate:modelValue": (v: string) => {
            notes.value = v;
            error.value = "";
          },
        }),
        h("div", { class: "flex gap-2 justify-end" }, [
          h(
            Button,
            {
              variant: "subtle",
              label: "Cancel",
              onClick: close,
            },
            {}
          ),
          h(
            Button,
            {
              variant: "solid",
              theme: "gray",
              label: "Request Closure",
              loading: isLoading.value,
              onClick: async () => {
                if (!notes.value.trim()) {
                  error.value = "Resolution details are required";
                  return;
                }

                try {
                  isLoading.value = true;
                  await call("pw_helpdesk.customizations.ticket_closure_workflow.request_closure", {
                    ticket_id: props.ticketId,
                    resolution_notes: notes.value,
                  });
                  toast.success("Closure request submitted successfully");
                  ticket.reload();
                  close();
                } catch (err) {
                  error.value = err.message || "Failed to submit closure request";
                } finally {
                  isLoading.value = false;
                }
              },
            },
            {}
          ),
        ]),
      ]);
    },
  });
}

const setValue = createResource({
  url: "frappe.client.set_value",
  debounce: 300,
  makeParams: (params) => {
    return {
      doctype: "HD Ticket",
      name: props.ticketId,
      fieldname: params.fieldname,
      value: params.value,
    };
  },
  onSuccess: () => {
    showFeedbackDialog.value = false;
    ticket.reload();
  },
});

const breadcrumbs = computed(() => {
  let items = [{ label: "Tickets", route: { name: "TicketsCustomer" } }];
  items.push({
    label: ticket.data?.subject,
    route: { name: "TicketCustomer" },
  });
  return items;
});

const showEditor = computed(() => ticket.data.status !== "Closed");

// this handles whether the ticket was raised and then was closed without any reply from the agent.
const { isFeedbackMandatory } = useConfigStore();
const showFeedback = computed(() => {
  const hasAgentCommunication = ticket.data?.communications?.some(
    (c) => c.sender !== ticket.data.raised_by
  );
  return hasAgentCommunication && isFeedbackMandatory;
});

onMounted(() => {
  document.title = props.ticketId;
  socket.on("helpdesk:ticket-update", (ticketID) => {
    if (ticketID === Number(props.ticketId)) {
      ticket.reload();
    }
  });
});

onUnmounted(() => {
  document.title = "Helpdesk";
  socket.off("helpdesk:ticket-update");
});
</script>
