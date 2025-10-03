<template>
  <div class="flex flex-col">
    <LayoutHeader v-if="ticket.data">
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" class="breadcrumbs">
          <template #prefix="{ item }">
            <Icon
              v-if="item.icon"
              :icon="item.icon"
              class="mr-1 h-4 flex items-center justify-center self-center"
            />
          </template>
        </Breadcrumbs>
      </template>
      <template #right-header>
        <CustomActions
          v-if="ticket.data._customActions"
          :actions="ticket.data._customActions"
        />
        <div v-if="ticket.data.assignees?.length">
          <component :is="ticket.data.assignees.length == 1 ? 'Button' : 'div'">
            <MultipleAvatar
              :avatars="ticket.data.assignees"
              @click="showAssignmentModal = true"
            />
          </component>
        </div>
        <button
          v-else
          class="rounded bg-gray-100 px-2 py-1.5 text-base text-gray-800"
          @click="showAssignmentModal = true"
        >
          Assign
        </button>
        <Dropdown :options="dropdownOptions">
          <template #default="{ open }">
            <Button :label="ticket.data.status">
              <template #prefix>
                <IndicatorIcon
                  :class="ticketStatusStore.textColorMap[ticket.data.status]"
                />
              </template>
              <template #suffix>
                <FeatherIcon
                  :name="open ? 'chevron-up' : 'chevron-down'"
                  class="h-4"
                />
              </template>
            </Button>
          </template>
        </Dropdown>
        <Button
          v-if="canCloseTicket && ticket.data.status !== 'Closed'"
          label="Close"
          variant="solid"
          theme="red"
          @click="triggerClose()"
        />
        <Button
          v-else-if="canRequestClosure && ticket.data.status !== 'Closed'"
          label="Request Closure"
          variant="solid"
          theme="gray"
          @click="triggerRequestClosure()"
        />
      </template>
    </LayoutHeader>
    <div v-if="ticket.data" class="flex h-full overflow-hidden">
      <div class="flex flex-1 flex-col max-w-[calc(100%-382px)]">
        <!-- ticket activities -->
        <div class="overflow-y-hidden flex flex-1 !h-full flex-col">
          <Tabs v-model="tabIndex" :tabs="tabs">
            <TabList />
            <TabPanel v-slot="{ tab }" class="h-full">
              <TicketResolutionSection
                v-if="tab.name === 'resolution'"
                :ticket="ticket.data"
                :ticket-id="ticketId"
                @update="
                  () => {
                    ticket.reload();
                  }
                "
              />
              <TicketAgentActivities
                v-else
                ref="ticketAgentActivitiesRef"
                :activities="filterActivities(tab.name)"
                :title="tab.label"
                :ticket-status="ticket.data?.status"
                @update="
                  () => {
                    ticket.reload();
                  }
                "
                @email:reply="
                  (e) => {
                    communicationAreaRef.replyToEmail(e);
                  }
                "
              />
            </TabPanel>
          </Tabs>
        </div>
        <CommunicationArea
          ref="communicationAreaRef"
          v-model="ticket.data"
          :to-emails="[ticket.data?.raised_by]"
          :cc-emails="[]"
          :bcc-emails="[]"
          :key="ticket.data?.name"
          @update="
            () => {
              ticket.reload();
              ticketAgentActivitiesRef.scrollToLatestActivity();
            }
          "
        />
      </div>
      <TicketAgentSidebar
        :ticket="ticket.data"
        @update="({ field, value }) => updateTicket(field, value)"
        @email:open="(e) => communicationAreaRef.toggleEmailBox()"
        @reload="ticket.reload()"
      />
    </div>
    <AssignmentModal
      v-if="ticket.data && showAssignmentModal"
      v-model="showAssignmentModal"
      :assignees="ticket.data.assignees"
      :docname="ticketId"
      :team="ticket.data?.agent_group"
      doctype="HD Ticket"
      @update="
        () => {
          ticket.reload();
        }
      "
    />
    <!-- Rename Subject Dialog -->
    <Dialog v-model="showSubjectDialog" :options="{ title: 'Rename Subject' }">
      <template #body-content>
        <div class="flex flex-col flex-1 gap-3">
          <FormControl
            v-model="renameSubject"
            type="textarea"
            size="sm"
            variant="subtle"
            :disabled="false"
          />
          <Button
            variant="solid"
            :loading="isLoading"
            label="Rename"
            @click="handleRename"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import {
  Breadcrumbs,
  Button,
  Dialog,
  Dropdown,
  FormControl,
  TabList,
  TabPanel,
  Tabs,
  call,
  createResource,
  toast,
} from "frappe-ui";
import { computed, h, onMounted, onUnmounted, provide, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";

import {
  AssignmentModal,
  CommunicationArea,
  Icon,
  LayoutHeader,
  MultipleAvatar,
  TextEditor,
} from "@/components";
import {
  ActivityIcon,
  CommentIcon,
  EmailIcon,
  IndicatorIcon,
  TicketIcon,
} from "@/components/icons";
import { TicketAgentActivities, TicketAgentSidebar } from "@/components/ticket";
import TicketResolutionSection from "@/components/ticket/TicketResolutionSection.vue";
import { setupCustomizations } from "@/composables/formCustomisation";
import { useView } from "@/composables/useView";
import { socket } from "@/socket";
import { globalStore } from "@/stores/globalStore";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import { useUserStore } from "@/stores/user";
import { useAuthStore } from "@/stores/auth";
import { TabObject, TicketTab, View } from "@/types";
import { getIcon } from "@/utils";
import { ComputedRef } from "vue";
import { showAssignmentModal } from "./modalStates";
const route = useRoute();
const router = useRouter();

const ticketStatusStore = useTicketStatusStore();
const { getUser } = useUserStore();
const authStore = useAuthStore();
const { userId, isAdmin, isAgent } = storeToRefs(authStore);
const { $dialog } = globalStore();

// Fallback to session user from cookie if auth store not loaded yet
const sessionUser = computed(() => {
  const cookies = new URLSearchParams(document.cookie.split("; ").join("&"));
  let _sessionUser = cookies.get("user_id");
  if (_sessionUser === "Guest") {
    _sessionUser = null;
  }
  return _sessionUser;
});

const currentUserId = computed(() => userId.value || sessionUser.value);
const ticketAgentActivitiesRef = ref(null);
const communicationAreaRef = ref(null);
const renameSubject = ref("");
const isLoading = ref(false);

const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
});
watch(
  () => props.ticketId,
  () => {
    ticket.reload();
  }
);

const { findView } = useView("HD Ticket");

provide("communicationArea", communicationAreaRef);

const showSubjectDialog = ref(false);

const ticket = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.get_one",
  auto: true,
  makeParams: () => ({
    name: props.ticketId,
  }),
  transform: (data) => {
    if (data._assign) {
      data.assignees = JSON.parse(data._assign).map((assignee) => {
        return {
          name: assignee,
          image: getUser(assignee).user_image,
          label: getUser(assignee).full_name,
        };
      });
    }
    renameSubject.value = data.subject;
  },
  onSuccess: (data) => {
    document.title = data.subject;
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
});
function updateField(name: string, value: string, callback = () => {}) {
  updateTicket(name, value);
  callback();
}

const breadcrumbs = computed(() => {
  let items = [{ label: "Tickets", route: { name: "TicketsAgent" } }];
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
    label: ticket.data?.subject,
    onClick: () => {
      showSubjectDialog.value = true;
    },
  });
  return items;
});

const isRaiser = computed(() => {
  if (!ticket.data || !currentUserId.value) return false;
  return currentUserId.value === ticket.data.raised_by;
});

const isRaisedForCurrentUser = computed(() => {
  if (!ticket.data || !currentUserId.value) return false;
  // Check if ticket was raised for another employee and current user is that employee
  // Since custom_raise_for_employee stores Employee ID, we need to check if raised_by matches current user
  // The backend should have already set raised_by to the employee's user_id
  if (ticket.data.custom_raise_for_employee) {
    return ticket.data.raised_by === currentUserId.value;
  }
  return false;
});

const isAssignedAgent = () => {
  if (!ticket.data || !currentUserId.value) return false;

  // Check if user is directly assigned
  if (ticket.data.assignees && Array.isArray(ticket.data.assignees)) {
    const assignedUsers = ticket.data.assignees.map(a => a.name);
    if (assignedUsers.includes(currentUserId.value)) return true;
  }

  return false;
};

const canCloseTicket = computed(() => {
  if (!ticket.data || !currentUserId.value) return false;

  // Admin can always close any ticket
  if (isAdmin.value) {
    return true;
  }

  // User who raised the ticket can close if:
  // 1. They raised it for themselves (no custom_raise_for_employee)
  // 2. OR ticket is raised_by current user
  if (isRaiser.value) {
    // If there's no custom_raise_for_employee, or it's empty, raiser can close
    if (!ticket.data.custom_raise_for_employee) {
      return true;
    }
  }

  // If ticket was raised for someone else, check if current user is that person
  // The raised_by field should be set to the employee's user_id
  if (ticket.data.custom_raise_for_employee && ticket.data.raised_by === currentUserId.value) {
    return true;
  }

  return false;
});

const canRequestClosure = computed(() => {
  if (!ticket.data || !currentUserId.value) return false;

  // Ticket already closed - no action needed
  if (ticket.data.status === 'Closed') {
    return false;
  }

  // If user can close, they don't need to request
  if (canCloseTicket.value) {
    return false;
  }

  // Assigned agent can request closure
  if (isAssignedAgent()) {
    return true;
  }

  // Any agent can request closure (fallback for agents working on tickets)
  if (isAgent.value) {
    return true;
  }

  return false;
});

const handleRename = () => {
  if (renameSubject.value === ticket.data?.subject) return;
  updateTicket("subject", renameSubject.value);
  showSubjectDialog.value = false;
};

const dropdownOptions = computed(() =>
  ticketStatusStore.options.map((o) => ({
    label: o,
    value: o,
    onClick: () => updateTicket("status", o),
    icon: () =>
      h(IndicatorIcon, {
        class: ticketStatusStore.textColorMap[o],
      }),
  }))
);

// watch(
//   () => ticket.data,
//   (val) => {
//     console.log("CUSTOM ACTIONSSS");
//     // console.log(val._customActions);
//   },
//   { deep: true }
// );

const tabIndex = ref(0);
const tabs: TabObject[] = [
  {
    name: "activity",
    label: "Activity",
    icon: ActivityIcon,
  },
  {
    name: "email",
    label: "Emails",
    icon: EmailIcon,
  },
  {
    name: "comment",
    label: "Comments",
    icon: CommentIcon,
  },
  {
    name: "resolution",
    label: "Resolution",
    icon: TicketIcon,
  },
];

const activities = computed(() => {
  const emailProps = ticket.data.communications.map((email, idx: number) => {
    return {
      subject: email.subject,
      content: email.content,
      sender: { name: email.user.email, full_name: email.user.name },
      to: email.recipients,
      type: "email",
      key: email.creation,
      cc: email.cc,
      bcc: email.bcc,
      creation: email.communication_date || email.creation,
      attachments: email.attachments,
      name: email.name,
      deliveryStatus: email.delivery_status,
      isFirstEmail: idx === 0,
    };
  });

  const commentProps = ticket.data.comments.map((comment) => {
    return {
      name: comment.name,
      type: "comment",
      key: comment.creation,
      commentedBy: comment.commented_by,
      commenter: comment.user.name,
      creation: comment.creation,
      content: comment.content,
      attachments: comment.attachments,
    };
  });

  const historyProps = [...ticket.data.history, ...ticket.data.views].map(
    (h) => {
      return {
        type: "history",
        key: h.creation,
        content: h.action ? h.action : "viewed this",
        creation: h.creation,
        user: h.user.name + " ",
      };
    }
  );

  const sorted = [...emailProps, ...commentProps, ...historyProps].sort(
    (a, b) => new Date(a.creation) - new Date(b.creation)
  );

  const data = [];
  let i = 0;

  while (i < sorted.length) {
    const currentActivity = sorted[i];
    if (currentActivity.type === "history") {
      currentActivity.relatedActivities = [currentActivity];
      for (let j = i + 1; j < sorted.length + 1; j++) {
        const nextActivity = sorted[j];

        if (nextActivity && nextActivity.user === currentActivity.user) {
          currentActivity.relatedActivities.push(nextActivity);
        } else {
          data.push(currentActivity);
          i = j - 1;
          break;
        }
      }
    } else {
      data.push(currentActivity);
    }
    i++;
  }
  return data;
});

function filterActivities(eventType: TicketTab) {
  if (eventType === "activity") {
    return activities.value;
  }
  return activities.value.filter((activity) => activity.type === eventType);
}
const isErrorTriggered = ref(false);
function updateTicket(fieldname: string, value: string) {
  isErrorTriggered.value = false;
  if (value === ticket.data[fieldname]) return;
  updateOptimistic(fieldname, value);

  createResource({
    url: "frappe.client.set_value",
    params: {
      doctype: "HD Ticket",
      name: props.ticketId,
      fieldname,
      value,
    },
    debounce: 500,
    auto: true,
    onSuccess: () => {
      isLoading.value = false;
      isErrorTriggered.value = false;
      ticket.reload();
    },
    onError: (error) => {
      if (isErrorTriggered.value) return;
      isErrorTriggered.value = true;

      const text = error.exc_type
        ? (error.messages || error.message || []).join(", ")
        : error.message;
      toast.error(text);

      ticket.reload();
    },
  });
}

function updateOptimistic(fieldname: string, value: string) {
  ticket.data[fieldname] = value;
  toast.success("Ticket updated");
}

async function triggerClose() {
  console.log('[triggerClose] Called. Current status:', ticket.data.status);
  console.log('[triggerClose] Resolution details:', ticket.data.resolution_details);

  // Validate that resolution exists before allowing close
  const hasResolution = ticket.data.resolution_details &&
                       ticket.data.resolution_details.trim() &&
                       ticket.data.resolution_details.trim() !== '<p></p>';

  console.log('[triggerClose] hasResolution:', hasResolution);

  // Check if resolution details are already filled
  if (hasResolution) {
    // Resolution details exist, directly close the ticket
    console.log('[triggerClose] Has resolution, closing directly');
    try {
      await call("frappe.client.set_value", {
        doctype: "HD Ticket",
        name: props.ticketId,
        fieldname: "status",
        value: "Closed",
      });
      console.log('[triggerClose] Ticket closed successfully');
      toast.success("Ticket closed successfully");
      ticket.reload();
    } catch (err) {
      console.error('[triggerClose] Error closing ticket:', err);
      toast.error(err.message || "Failed to close ticket");
    }
    return;
  }

  // No resolution details, show modal to collect them
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

                  // Update resolution_details field
                  await call("frappe.client.set_value", {
                    doctype: "HD Ticket",
                    name: props.ticketId,
                    fieldname: "resolution_details",
                    value: notes.value,
                  });

                  // Update status to Closed
                  await call("frappe.client.set_value", {
                    doctype: "HD Ticket",
                    name: props.ticketId,
                    fieldname: "status",
                    value: "Closed",
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


async function triggerRequestClosure() {
  console.log('[triggerRequestClosure] Called');
  console.log('[triggerRequestClosure] Resolution details:', ticket.data.resolution_details);

  // Check if resolution already exists
  const hasResolution = ticket.data.resolution_details &&
                       ticket.data.resolution_details.trim() &&
                       ticket.data.resolution_details.trim() !== '<p></p>';

  // If resolution exists, directly request closure without asking for details again
  if (hasResolution) {
    console.log('[triggerRequestClosure] Resolution exists, requesting closure directly');
    try {
      const response = await call("pw_helpdesk.customizations.ticket_closure_workflow.request_closure", {
        ticket_id: props.ticketId,
        resolution_notes: ticket.data.resolution_details,
      });
      console.log('[triggerRequestClosure] Response:', response);
      console.log('[triggerRequestClosure] Email sent:', response?.email_sent);
      console.log('[triggerRequestClosure] Notification created:', response?.notification_created);

      toast.success(response?.message || "Closure request submitted successfully");
      ticket.reload();
    } catch (err) {
      console.error('[triggerRequestClosure] Error:', err);
      toast.error(err.message || "Failed to submit closure request");
    }
    return;
  }

  // No resolution exists, show modal to collect details
  console.log('[triggerRequestClosure] No resolution, showing modal');
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
                  console.log('[triggerRequestClosure] Calling request_closure API');
                  const response = await call("pw_helpdesk.customizations.ticket_closure_workflow.request_closure", {
                    ticket_id: props.ticketId,
                    resolution_notes: notes.value,
                  });
                  console.log('[triggerRequestClosure] Response:', response);
                  console.log('[triggerRequestClosure] Email sent:', response?.email_sent);
                  console.log('[triggerRequestClosure] Notification created:', response?.notification_created);

                  toast.success(response?.message || "Closure request submitted successfully");
                  ticket.reload();
                  close();
                } catch (err) {
                  console.error('[triggerRequestClosure] Error:', err);
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

onMounted(() => {
  socket.on("helpdesk:ticket-update", (ticketID) => {
    if (ticketID === Number(props.ticketId)) {
      ticket.reload();
    }
  });
});

// Debug button visibility
watch(
  () => ticket.data,
  (val) => {
    if (val) {
      console.log('=== TICKET AGENT DEBUG ===');
      console.log('userId (from store):', userId.value);
      console.log('sessionUser (from cookie):', sessionUser.value);
      console.log('currentUserId (computed):', currentUserId.value);
      console.log('Ticket raised_by:', val.raised_by);
      console.log('Ticket custom_raise_for_employee:', val.custom_raise_for_employee);
      console.log('Ticket status:', val.status);
      console.log('isRaiser:', isRaiser.value);
      console.log('isAdmin (from store):', isAdmin.value);
      console.log('isAgent (from store):', isAgent.value);
      console.log('isAssignedAgent:', isAssignedAgent());
      console.log('Assignees:', val.assignees);
      console.log('canCloseTicket:', canCloseTicket.value);
      console.log('canRequestClosure:', canRequestClosure.value);
      console.log('=========================');
    }
  },
  { deep: true, immediate: true }
);

onUnmounted(() => {
  document.title = "Helpdesk";
  socket.off("helpdesk:ticket-update");
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
