<template>
  <div v-if="ticket.doc?.name" class="flex-1">
    <TicketHeader
      :viewers="viewers"
      @open-ai="openAIFromComposer('reply')"
      @send-to-gameplan="onSendToGameplanEvent"
    />
    <div class="h-full flex overflow-hidden">
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Tabs & Communication Area -->
        <TicketActivityPanel ref="ticketActivityPanelRef" @open-ai="openAIFromComposer" />
      </div>

      <!-- Sidepanel with Resizer -->
      <TicketSidebar />
    </div>
    <!-- Floating launcher for the NextAI drawer. The drawer itself lives
         inside CommunicationArea as a teleported sibling so it can talk
         directly to the reply/comment editors via existing refs. Hidden
         while the drawer is open so the corner stays uncluttered. -->
    <OpenClawLauncher
      :hidden="aiDrawerOpen"
      tooltip="Ask NextAI"
      @toggle="toggleAIDrawer"
    />
    <SendToGameplanModal
      v-if="showHandoffModal"
      v-model="showHandoffModal"
      :ticket-name="props.ticketId"
      :ticket-subject="handoffSubject"
      @success="onHandoffSuccess"
    />
    <SetContactPhoneModal
      v-model="showPhoneModal"
      :name="ticket.data?.contact?.name"
      @onUpdate="ticket.reload"
    />
  </div>
</template>

<script setup lang="ts">
import TicketActivityPanel from "@/components/ticket-agent/TicketActivityPanel.vue";
import TicketHeader from "@/components/ticket-agent/TicketHeader.vue";
import TicketSidebar from "@/components/ticket-agent/TicketSidebar.vue";
import SetContactPhoneModal from "@/components/ticket/SetContactPhoneModal.vue";
import OpenClawLauncher from "@/components/openclaw/OpenClawLauncher.vue";
import SendToGameplanModal from "@/components/openclaw/SendToGameplanModal.vue";
import { useActiveViewers } from "@/composables/realtime";
import { reloadTicket, useTicket } from "@/composables/useTicket";
import { ticketsToNavigate } from "@/composables/useTicketNavigation";
import { globalStore } from "@/stores/globalStore";
import { useTelephonyStore } from "@/stores/telephony";
import {
  ActivitiesSymbol,
  AssigneeSymbol,
  Customizations,
  CustomizationSymbol,
  RecentSimilarTicketsSymbol,
  Resource,
  TicketContactSymbol,
  TicketSymbol,
} from "@/types";
import { createResource, toast, usePageMeta } from "frappe-ui";
import { computed, onBeforeUnmount, onMounted, provide, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { showCommentBox, showEmailBox } from "./modalStates";
const telephonyStore = useTelephonyStore();

const { $socket } = globalStore();

const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
});
const route = useRoute();
const showPhoneModal = ref(false);
const ticketActivityPanelRef = ref(null);

const ticketComposable = computed(() => useTicket(props.ticketId));
const ticket = computed(() => ticketComposable.value.ticket);
const customizations: Resource<Customizations> = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.get_ticket_customizations",
  cache: ["HD Ticket", "customizations"],
  auto: true,
});

provide(TicketSymbol, ticket);

provide(
  AssigneeSymbol,
  computed(() => ticketComposable.value.assignees)
);
provide(
  TicketContactSymbol,
  computed(() => ticketComposable.value.contact)
);
provide(
  CustomizationSymbol,
  computed(() => customizations)
);
provide(
  RecentSimilarTicketsSymbol,
  computed(() => ticketComposable.value.recentSimilarTickets)
);
provide(
  ActivitiesSymbol,
  computed(() => ticketComposable.value.activities)
);
provide("makeCall", () => {
  if (
    !ticketComposable.value.contact.data?.mobile_no &&
    !ticketComposable.value.contact.data?.phone
  ) {
    showPhoneModal.value = true;
    return;
  }
  telephonyStore.makeCall({
    number:
      ticketComposable.value.contact.data?.phone ||
      ticketComposable.value.contact.data?.mobile_no,
    doctype: "HD Ticket",
    docname: props.ticketId,
  });
});
const viewerComposable = computed(() => useActiveViewers(ticket.value.name));
const viewers = computed(
  () => viewerComposable.value.currentViewers[props.ticketId] || []
);
const { startViewing, stopViewing } = viewerComposable.value;

function openAIFromComposer(mode: "reply" | "comment") {
  // The inline NextAI panel handles its own opening from inside CommunicationArea.
  // Forward the request so the reply/comment box becomes visible.
  ticketActivityPanelRef.value?.openAIFromComposer?.(mode);
}

// Floating-launcher → drawer toggle. The drawer state lives inside
// CommunicationArea so it can talk directly to the reply/comment editors.
const aiDrawerOpen = computed(() => {
  const exposed = ticketActivityPanelRef.value?.aiDrawerOpen;
  // exposed is a ComputedRef forwarded from TicketActivityPanel.
  return !!(exposed && typeof exposed === "object" && "value" in exposed
    ? (exposed as any).value
    : exposed);
});
function toggleAIDrawer() {
  ticketActivityPanelRef.value?.toggleAIDrawer?.();
}

// Send-to-Gameplan modal — opened via a window CustomEvent dispatched by
// TicketHeader.  Mount lives here on TicketAgent because CommunicationArea is
// lazy-loaded (only after Reply/Comment click) so the window listener would
// otherwise miss events on a fresh ticket open.
const showHandoffModal = ref(false);
const handoffSubject = ref<string | undefined>(undefined);

function onSendToGameplanEvent(e: Event) {
  const detail = (e as CustomEvent<{ ticketName: string; subject?: string }>).detail || ({} as any);
  if (detail.ticketName && detail.ticketName !== props.ticketId) return;
  handoffSubject.value = detail.subject;
  showHandoffModal.value = true;
}

function onHandoffSuccess(_p: { gp_task: string; handoff: string }) {
  // Modal shows its own toast.
}

// handling for faster navigation between tickets
watch(
  () => route.params.ticketId,
  (newTicketId, oldTicketId) => {
    if (newTicketId === oldTicketId) return;

    if (oldTicketId) stopViewing(oldTicketId as string);
    startViewing(newTicketId as string);
  },
  { immediate: true }
);

type TicketUpdateData = {
  ticket_id: string;
  user: string;
  field: string;
  value: string;
};

onMounted(() => {
  window.addEventListener(
    "openclaw:send-to-gameplan",
    onSendToGameplanEvent as EventListener,
  );

  ticketsToNavigate.update({
    params: {
      ticket: props.ticketId,
      current_view: route.query.view as string,
    },
  });
  ticketsToNavigate.reload();
  ticket.value.markSeen.reload();

  $socket.on("ticket_update", (data: TicketUpdateData) => {
    if (data.ticket_id === ticket.value?.name) {
      // Notify the user about the update
      toast.info(`User ${data.user} updated ${data.field} to ${data.value}`);
    }
  });

  $socket.on("helpdesk:ticket-comment", (data: { ticket_id: string }) => {
    if (data.ticket_id == props.ticketId) {
      ticketComposable.value.activities.reload();
    }
  });

  $socket.on("helpdesk:ticket-update", (data: { ticket_id: string }) => {
    if (data.ticket_id == props.ticketId) {
      reloadTicket(props.ticketId);
    }
  });
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "openclaw:send-to-gameplan",
    onSendToGameplanEvent as EventListener,
  );

  stopViewing(props.ticketId);
  showEmailBox.value = false;
  showCommentBox.value = false;

  $socket.off("ticket_update");
  $socket.off("helpdesk:ticket-comment");
  $socket.off("helpdesk:ticket-update");
});

usePageMeta(() => {
  return {
    title: props.ticketId,
  };
});
</script>

<style>
.breadcrumbs button {
  background-color: inherit !important;
  &:hover,
  &:focus {
    background-color: inherit !important;
  }
}
</style>
