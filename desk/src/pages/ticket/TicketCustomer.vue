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
          v-if="isRaiser && ticket.data.status !== 'Closed'"
          label="Close"
          theme="gray"
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
          variant="subtle"
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
import { LayoutHeader } from "@/components";
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
    message: "Provide resolution notes before closing.",
    actions: [],
    render: ({ close }) => {
      const notes = ref("");
      return h("div", { class: "flex flex-col gap-3" }, [
        h(FormControl, {
          type: "textarea",
          placeholder: "Resolution notes",
          modelValue: notes.value,
          "onUpdate:modelValue": (v: string) => (notes.value = v),
        }),
        h(
          Button,
          {
            variant: "solid",
            label: "Confirm Close",
            onClick: async () => {
              await call("pw_helpdesk.customizations.ticket_closure_workflow.mark_as_resolved", {
                ticket_id: props.ticketId,
                resolution_notes: notes.value || "",
              });
              toast.success("Ticket closed");
              ticket.reload();
              close();
            },
          },
          {}
        ),
      ]);
    },
  });
}

function triggerRequestClosure() {
  $dialog({
    title: "Request Closure",
    message: "Provide resolution notes to request closure.",
    actions: [],
    render: ({ close }) => {
      const notes = ref("");
      return h("div", { class: "flex flex-col gap-3" }, [
        h(FormControl, {
          type: "textarea",
          placeholder: "Resolution notes",
          modelValue: notes.value,
          "onUpdate:modelValue": (v: string) => (notes.value = v),
        }),
        h(
          Button,
          {
            variant: "solid",
            label: "Send Request",
            onClick: async () => {
              await call("pw_helpdesk.customizations.ticket_closure_workflow.request_closure", {
                ticket_id: props.ticketId,
                resolution_notes: notes.value || "",
              });
              toast.success("Closure requested");
              ticket.reload();
              close();
            },
          },
          {}
        ),
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
