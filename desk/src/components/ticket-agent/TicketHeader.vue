<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex flex-col truncate">
        <Breadcrumbs :items="breadcrumbs" class="breadcrumbs">
          <template #prefix="{ item }">
            <Icon
              v-if="item.icon"
              :icon="item.icon"
              class="mr-1 h-4 flex items-center justify-center self-center"
            />
          </template>
        </Breadcrumbs>
        <TicketSLA />
      </div>
    </template>
    <template #right-header>
      <div class="flex gap-2 items-center">
        <MultipleAvatar
          :avatars="JSON.stringify(viewers)"
          size="md"
          :hide-name="true"
        />
        <Button
          label="Send to Gameplan"
          variant="subtle"
          :disabled="!canHandoff"
          :title="canHandoff ? 'Draft a Gameplan task from this ticket' : 'You need Gameplan write access to hand off tickets.'"
          @click="onSendToGameplanClick"
        >
          <template #prefix>
            <Send class="h-4 w-4" />
          </template>
        </Button>
        <!-- Navigation -->
        <TicketNavigation :key="ticket.name" />
        <!-- Custom Actions -->
        <div v-if="normalActions.length" class="flex gap-2">
          <Button v-for="action in normalActions" v-bind="action">
            <template v-if="action.icon" #prefix>
              <FeatherIcon :name="action.icon" class="h-4 w-4" />
            </template>
          </Button>
        </div>
        <div v-if="groupedWithLabelActions.length">
          <div v-for="g in groupedWithLabelActions" :key="g.label">
            <Dropdown v-slot="{ open }" :options="g.action">
              <Button :label="g.label">
                <template #suffix>
                  <FeatherIcon
                    :name="open ? 'chevron-up' : 'chevron-down'"
                    class="h-4"
                  />
                </template>
              </Button>
            </Dropdown>
          </div>
        </div>
        <!-- Reject -->
        <Button
          v-if="canReject"
          label="Reject"
          theme="red"
          variant="solid"
          @click="rejectTicket"
        />
        <Button
          v-if="isRejected"
          label="View Rejection Reason"
          variant="outline"
          @click="viewRejectionReason"
        />
        <!-- Status -->
        <Dropdown :options="statusDropdown" placement="right">
          <template #default="{ open }">
            <Button :label="ticket.doc.status" ref="statusRef">
              <template #prefix>
                <IndicatorIcon
                  :class="
                    ticketStatusStore.getStatus(ticket.doc.status)?.parsed_color
                  "
                />
              </template>
            </Button>
          </template>
        </Dropdown>
        <!-- Core Actions + Custom Actions -->
        <Dropdown
          v-if="groupedActions.length"
          :options="groupedActions"
          placement="right"
        >
          <Button icon="more-horizontal" />
        </Dropdown>
      </div>
    </template>
  </LayoutHeader>
  <TicketMergeModal
    :ticket="ticket.doc"
    v-if="showMergeModal"
    v-model="showMergeModal"
    @update="ticket.reload()"
  />
  <TicketSubjectModal v-if="showSubjectDialog" v-model="showSubjectDialog" />
</template>

<script setup lang="ts">
import { MultipleAvatar } from "@/components";
import LayoutHeader from "@/components/LayoutHeader.vue";
import TicketMergeModal from "@/components/ticket/TicketMergeModal.vue";
import { setupCustomizations } from "@/composables/formCustomisation";
import { useNotifyTicketUpdate } from "@/composables/realtime";
import { useShortcut } from "@/composables/shortcuts";
import { useView } from "@/composables/useView";
import { useAuthStore } from "@/stores/auth";
import { globalStore } from "@/stores/globalStore";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import {
  ActivitiesSymbol,
  CustomizationSymbol,
  TicketSymbol,
  View,
} from "@/types";
import { HDTicketStatus } from "@/types/doctypes";
import { getIcon } from "@/utils";
import { Breadcrumbs, call, Dropdown, toast } from "frappe-ui";
import { __ } from "@/translation";
import {
  computed,
  ComputedRef,
  h,
  inject,
  onMounted,
  PropType,
  ref,
  useTemplateRef,
  watchEffect,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import LucideMerge from "~icons/lucide/merge";
import Send from "~icons/lucide/send";
import { IndicatorIcon } from "../icons";
import TicketNavigation from "./TicketNavigation.vue";
import TicketSLA from "./TicketSLA.vue";
import TicketSubjectModal from "./TicketSubjectModal.vue";

defineProps({
  viewers: {
    type: Array as PropType<string[]>,
    required: true,
  },
});
const emit = defineEmits(["open-ai", "send-to-gameplan"]);

// Gameplan handoff gate — Helpdesk SPA doesn't expose window.frappe, so use
// the existing auth store.  Any admin/agent/manager can initiate the handoff;
// the backend re-checks Gameplan write permission on send_to_gameplan and
// rejects if needed.
const authStore = useAuthStore();
const canHandoff = computed(() => Boolean(
  authStore.isAdmin || authStore.isAgent || authStore.isManager,
));

function onSendToGameplanClick() {
  if (!ticket?.value?.doc?.name) return;
  const payload = {
    ticketName: ticket.value.doc.name,
    ticketDoctype: "HD Ticket",
    subject: ticket.value.doc.subject,
  };
  // Emit for tests / direct parent wiring.
  emit("send-to-gameplan", payload);
  // Dispatch a window event so CommunicationArea (deep in the tree, mounts the
  // modal as a teleported sibling of the drawer) can pick it up without
  // prop-drilling through TicketActivityPanel.
  window.dispatchEvent(
    new CustomEvent("openclaw:send-to-gameplan", { detail: payload }),
  );
}

const route = useRoute();
const router = useRouter();
const { findView } = useView("HD Ticket");
const ticketStatusStore = useTicketStatusStore();

const ticket = inject(TicketSymbol);
const customizations = inject(CustomizationSymbol);
const activities = inject(ActivitiesSymbol);

const REJECT_REASONS = [
  "Duplicate Ticket",
  "Out of Scope",
  "Insufficient Information",
  "Invalid Request",
  "Already Resolved",
  "Not Supported",
  "Configuration / How-to (Refer KB)",
  "Spam / Test Ticket",
];

const isRejected = computed(
  () =>
    Boolean(ticket.value.doc.custom_is_rejected) ||
    ticket.value.doc.status === "Rejected"
);

const canReject = computed(
  () => ticket.value.doc.status !== "Open" && !isRejected.value
);

const showSubjectDialog = ref(false);

const { notifyTicketUpdate } = useNotifyTicketUpdate(ticket.value?.name);
const statusDropdown = computed(() => {
  const statuses =
    ticketStatusStore.statuses.data?.filter((s) => s.enabled) || [];
  return statuses.map((o: HDTicketStatus) => ({
    label: o.label_agent,
    value: o.label_agent,
    onClick: () => {
      notifyTicketUpdate("Status", o.label_agent);
      if (ticket.value.doc.status === o.label_agent) return;
      ticket.value.setValue.submit(
        { status: o.label_agent },
        {
          onSuccess() {
            activities.value.reload();
          },
        }
      );
    },
    icon: () =>
      h(IndicatorIcon, {
        class: o.parsed_color,
      }),
  }));
});
const breadcrumbs = computed(() => {
  let items = [{ label: __("Tickets"), route: { name: "TicketsAgent" } }];
  if (route.query.view) {
    const currView: ComputedRef<View> = findView(route.query.view as string);
    if (currView) {
      items.push({
        label: currView.value?.label,
        icon: getIcon(currView.value?.icon),
        route: { name: "TicketsAgent", query: { view: currView.value?.name } },
      });
    }
  }
  items.push({
    label: ticket.value.doc?.subject,
    onClick: () => {
      showSubjectDialog.value = true;
    },
  });
  return items;
});

function updateField(fieldname: string, value: string, callback = () => {}) {
  const doc = ticket.value;
  doc.setValue.submit({
    [fieldname]: value,
  });
  callback();
}

const showMergeModal = ref(false);
const showMergeOption = computed(() => {
  return (
    !ticket.value.doc.is_merged &&
    ["Open", "Paused"].includes(ticket.value.doc.status_category)
  );
});
function rejectTicket() {
  const optionsHtml = REJECT_REASONS.map(
    (r) => `<option value="${r}">${__(r)}</option>`
  ).join("");

  globalStore().$dialog({
    title: __("Reject Ticket"),
    html: `<div class="flex flex-col gap-3">
      <div class="flex flex-col gap-1.5">
        <label class="text-sm font-medium text-gray-700">${__("Reason")}</label>
        <select id="reject-reason-select" class="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm focus:border-gray-500 focus:outline-none">
          <option value="" disabled selected>${__("Select a reason")}</option>
          ${optionsHtml}
        </select>
      </div>
      <div class="flex flex-col gap-1.5">
        <label class="text-sm font-medium text-gray-700">${__("Description")}</label>
        <textarea id="reject-reason-description" class="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none" rows="3" placeholder="${__("Optional description...")}"></textarea>
      </div>
    </div>`,
    actions: [
      {
        label: __("Reject"),
        variant: "solid",
        theme: "red",
        onClick: ({ close }: { close: () => void }) => {
          const selectEl = document.getElementById(
            "reject-reason-select"
          ) as HTMLSelectElement;
          const textareaEl = document.getElementById(
            "reject-reason-description"
          ) as HTMLTextAreaElement;
          const selectedReason = selectEl?.value || "";
          const description = textareaEl?.value || "";

          if (!selectedReason) {
            toast.create({
              title: __("Please select a rejection reason"),
              icon: "x",
              iconClasses: "text-red-600",
            });
            return;
          }
          ticket.value.setValue.submit(
            {
              custom_is_rejected: 1,
              custom_reason: selectedReason,
              custom_reason_description: description,
              status: "Rejected",
            },
            {
              onSuccess() {
                activities.value.reload();
                toast.create({
                  title: __("Ticket rejected successfully"),
                  icon: "check",
                  iconClasses: "text-green-600",
                });
              },
            }
          );
          close();
        },
      },
      {
        label: __("Cancel"),
      },
    ],
  });
}

function escapeHtml(str: string) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function viewRejectionReason() {
  const reason = escapeHtml(
    ticket.value.doc.custom_reason || __("N/A")
  );
  const desc = escapeHtml(
    ticket.value.doc.custom_reason_description || __("N/A")
  );

  globalStore().$dialog({
    title: __("Rejection Reason"),
    html: `<div class="flex flex-col gap-3">
      <div class="flex flex-col gap-1">
        <span class="text-sm font-medium text-gray-700">${__("Reason")}</span>
        <span class="text-sm text-gray-900">${reason}</span>
      </div>
      <div class="flex flex-col gap-1">
        <span class="text-sm font-medium text-gray-700">${__("Description")}</span>
        <span class="text-sm text-gray-900">${desc}</span>
      </div>
    </div>`,
  });
}

const defaultActions = computed(() => {
  let items = [];

  if (showMergeOption.value) {
    items.push({
      label: __("Merge Ticket"),
      icon: LucideMerge,
      condition: () => !ticket.value.doc.is_merged,
      onClick: () => (showMergeModal.value = true),
    });
  }
  return [
    {
      group: __("Default actions"),
      hideLabel: true,
      items,
    },
  ];
});
const actions = ref([]);
const normalActions = computed(() => {
  return actions.value.filter((action) => !action.group);
});

const groupedWithLabelActions = computed(() => {
  let _actions = [];

  actions.value
    .filter((action) => action.buttonLabel && action.group)
    .forEach((action) => {
      let groupIndex = _actions.findIndex(
        (a) => a.label === action.buttonLabel
      );
      if (groupIndex > -1) {
        _actions[groupIndex].action.push(action);
      } else {
        _actions.push({
          label: action.buttonLabel,
          action: [action],
        });
      }
    });
  return _actions;
});

const groupedActions = computed(() => {
  let _actions = [];
  _actions = _actions.concat(
    actions.value.filter((action) => action.group && !action.buttonLabel)
  );
  return _actions;
});

const customizationCtx = computed(() => ({
  doc: ticket?.value?.doc,
  call,
  router,
  toast,
  $dialog: globalStore().$dialog,
  updateField,
  createToast: toast.create,
}));

// to manage the correct  customization context for actions, happens because of navigation between tickets using buttons
watchEffect(async () => {
  if (customizations.value?.data) {
    await setupCustomizations(
      customizations.value.data,
      customizationCtx.value
    );

    actions.value = [
      ...defaultActions.value,
      ...(customizations.value?.data?._customActions || []),
    ];
  }
});

const statusRef = useTemplateRef("statusRef");

onMounted(() => {
  useShortcut("s", () => {
    statusRef.value?.$el?.nextElementSibling?.click();
  });
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
