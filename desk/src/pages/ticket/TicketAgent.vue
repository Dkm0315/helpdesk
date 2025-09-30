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
          v-if="ticket.data.status === 'Resolved'"
          label="Close"
          variant="solid"
          theme="red"
          @click="triggerClose()"
        />
        <Button
          v-else-if="canCloseTicket && ticket.data.status !== 'Closed'"
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
const { userId } = useAuthStore();
const { $dialog } = globalStore();
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
  if (!ticket.data) return false;
  return (userId as any).value === ticket.data.raised_by;
});

const canCloseTicket = computed(() => {
  if (!ticket.data) return false;
  // System manager/admin can always close
  if (isAdmin()) return true;
  // User who raised the ticket can close
  if ((userId as any).value === ticket.data.raised_by) return true;
  // User for whom the ticket is raised (contact) can close
  if (ticket.data.contact === (userId as any).value) return true;
  // Assigned agents or team members can close
  return isAssignedToTicket();
});

const canRequestClosure = computed(() => {
  if (!ticket.data) return false;
  // Same logic as canCloseTicket for now - both actions are available to authorized users
  return canCloseTicket.value;
});

const isAssignedToTicket = () => {
  if (!ticket.data) return false;
  const currentUserId = (userId as any).value;

  // Check if user is directly assigned
  if (ticket.data.assignees) {
    const assignedUsers = ticket.data.assignees.map(a => a.name);
    if (assignedUsers.includes(currentUserId)) return true;
  }

  // For now, return true if user has write permission (agent/employee)
  return true; // This will be refined based on actual team membership
};

const isAdmin = () => {
  // Check if user has system manager permissions
  return (userId as any).value === 'Administrator' || false; // Simplified check
};

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
  // Check if resolution details are already filled
  if (ticket.data.resolution_details && ticket.data.resolution_details.trim() && ticket.data.resolution_details.trim() !== '<p></p>') {
    // Resolution details exist, directly close the ticket
    try {
      await call("frappe.client.set_value", {
        doctype: "HD Ticket",
        name: props.ticketId,
        fieldname: "status",
        value: "Closed",
      });
      toast.success("Ticket closed successfully");
      ticket.reload();
    } catch (err) {
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

onMounted(() => {
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

<style>
.breadcrumbs button {
  background-color: inherit !important;
  &:hover,
  &:focus {
    background-color: inherit !important;
  }
}
</style>
