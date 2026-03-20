<template>
  <SettingsLayoutBase :description="__('Manage general settings of your app.')">
    <template #title>
      <div class="flex items-center gap-2">
        <h1 class="text-lg font-semibold text-ink-gray-8">
          {{ __("General") }}
        </h1>
        <Badge
          variant="subtle"
          theme="orange"
          size="sm"
          :label="__('Unsaved')"
          v-if="isDirty || isWebsiteSettingsChanged"
        />
      </div>
    </template>
    <template #header-actions>
      <Button
        :label="__('Save')"
        variant="solid"
        @click="saveSettings"
        :loading="
          saveSettingsResource.loading || saveWebsiteSettingsResource.loading
        "
        :disabled="!isDirty && !isWebsiteSettingsChanged"
      />
    </template>
    <template #content>
      <div
        v-if="settingsDataResource.loading && !settingsDataResource.data"
        class="flex items-center justify-center mt-12"
      >
        <LoadingIndicator class="w-4" />
      </div>
      <div v-else>
        <Branding />
        <hr class="my-8" />
        <TicketSettings />
        <hr class="my-8" />
        <WorkflowKnowledgebaseSettings />
        <hr class="my-8" />
        <div>
          <div class="text-base font-semibold text-gray-900">
            {{ __("User signup") }}
          </div>
          <div class="flex items-center justify-between mt-6">
            <div class="flex flex-col gap-1">
              <span class="text-base font-medium text-ink-gray-8">{{
                __("Disable signup")
              }}</span>
              <span class="text-p-sm text-ink-gray-6">{{
                __(
                  "New users will have to be manually registered by system managers."
                )
              }}</span>
            </div>
            <Switch v-model="disableSignup" />
          </div>
        </div>
        <hr class="my-8" />
        <div>
          <div class="text-base font-semibold text-gray-900">
            {{ __("Feature Flags") }}
          </div>
          <div class="flex items-center justify-between mt-6">
            <div class="flex flex-col gap-1">
              <span class="text-base font-medium text-ink-gray-8">{{
                __("Our Services")
              }}</span>
              <span class="text-p-sm text-ink-gray-6">{{
                __("Show the Our Services page and sidebar link.")
              }}</span>
            </div>
            <Switch v-model="settingsData.enableOurServices" />
          </div>
          <div class="flex items-center justify-between mt-6">
            <div class="flex flex-col gap-1">
              <span class="text-base font-medium text-ink-gray-8">{{
                __("Buy Services")
              }}</span>
              <span class="text-p-sm text-ink-gray-6">{{
                __("Show the Buy Services page and sidebar link.")
              }}</span>
            </div>
            <Switch v-model="settingsData.enableBuyServices" />
          </div>
          <div class="flex items-center justify-between mt-6">
            <div class="flex flex-col gap-1">
              <span class="text-base font-medium text-ink-gray-8">{{
                __("Wiki")
              }}</span>
              <span class="text-p-sm text-ink-gray-6">{{
                __("Show the Wiki section in the sidebar.")
              }}</span>
            </div>
            <Switch v-model="settingsData.enableWiki" />
          </div>
        </div>
        <template v-if="authStore.isAdmin">
          <hr class="my-8" />
          <div>
            <div class="text-base font-semibold text-gray-900">
              {{ __("Our Services Content") }}
            </div>
            <p class="text-p-sm text-ink-gray-6 mt-1">
              {{ __("Write the content displayed on the Our Services page. Supports Markdown formatting.") }}
            </p>
            <div class="mt-6">
              <TextEditor
                editor-class="!prose-sm max-w-full overflow-auto min-h-[300px] max-h-[600px] py-1.5 px-2 rounded-b border border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:shadow-sm focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors -mt-0.5"
                :bubble-menu="false"
                :content="settingsData.ourServicesContent"
                @change="settingsData.ourServicesContent = $event"
                :fixed-menu="editorMenu"
                :placeholder="__('Write about your services here...')"
              />
            </div>
          </div>
        </template>
      </div>
    </template>
  </SettingsLayoutBase>
</template>

<script setup lang="ts">
import {
  Badge,
  Button,
  createResource,
  LoadingIndicator,
  Switch,
  TextEditor,
  toast,
} from "frappe-ui";
import Branding from "./components/Branding.vue";
import TicketSettings from "./components/TicketSettings.vue";
import WorkflowKnowledgebaseSettings from "./components/WorkflowKnowledgebaseSettings.vue";
import { computed, provide, ref, watch } from "vue";
import { __ } from "@/translation";
import { disableSettingModalOutsideClick } from "../settingsModal";
import SettingsLayoutBase from "@/components/layouts/SettingsLayoutBase.vue";
import { HDSettings, HDSettingsSymbol } from "@/types";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

const editorMenu = [
  "Paragraph",
  ["Heading 2", "Heading 3", "Heading 4"],
  "Separator",
  "Bold",
  "Italic",
  "Bullet List",
  "Numbered List",
  "Separator",
  "Link",
  "Blockquote",
  "Code",
];

const isDirty = ref(false);
const initialData = ref<null | string>(null);
const settingsData = ref({
  brandName: "",
  brandLogo: "",
  favicon: "",
  autoCloseAfterDays: "",
  autoCloseStatus: "",
  autoCloseTickets: "",
  assignWithinTeam: false,
  doNotRestrictTicketsWithoutAnAgentGroup: false,
  restrictTicketsByAgentGroup: false,
  updateStatusTo: "",
  autoUpdateStatus: false,
  isFeedbackMandatory: false,
  enableCommentReactions: false,
  allowAnyoneToCreateTickets: false,
  defaultTicketType: "",
  preferKnowledgeBase: false,
  skipEmailWorkflow: false,
  disableSavedRepliesGlobalScope: false,
  enableOutsideHoursBanner: false,
  outsideWorkingHoursBannerMessage: "",
  enableOurServices: true,
  enableBuyServices: true,
  enableWiki: true,
  ourServicesContent: "",
});
const disableSignup = ref(false);

provide(HDSettingsSymbol, settingsData);

const settingsDataResource = createResource({
  url: "frappe.client.get",
  params: {
    doctype: "HD Settings",
    name: "HD Settings",
  },
  auto: true,
  onSuccess(data: HDSettings) {
    settingsData.value = transformData(data);
    initialData.value = JSON.stringify(settingsData.value);
  },
});

const isWebsiteSettingsChanged = computed(() => {
  return (
    disableSignup.value !==
    Boolean(websiteSettingsResource.data?.disable_signup)
  );
});

const saveSettingsResource = createResource({
  url: "frappe.client.set_value",
  makeParams() {
    return {
      doctype: "HD Settings",
      name: "HD Settings",
      fieldname: {
        brand_name: settingsData.value.brandName,
        auto_close_after_days: Number(settingsData.value.autoCloseAfterDays),
        auto_close_status: settingsData.value.autoCloseStatus,
        auto_close_tickets: settingsData.value.autoCloseTickets,
        assign_within_team: settingsData.value.assignWithinTeam,
        do_not_restrict_tickets_without_an_agent_group:
          settingsData.value.doNotRestrictTicketsWithoutAnAgentGroup,
        restrict_tickets_by_agent_group:
          settingsData.value.restrictTicketsByAgentGroup,
        update_status_to: settingsData.value.updateStatusTo,
        auto_update_status: settingsData.value.autoUpdateStatus,
        is_feedback_mandatory: settingsData.value.isFeedbackMandatory,
        enable_comment_reactions: settingsData.value.enableCommentReactions,
        allow_anyone_to_create_tickets:
          settingsData.value.allowAnyoneToCreateTickets,
        default_ticket_type: settingsData.value.defaultTicketType,
        prefer_knowledge_base: settingsData.value.preferKnowledgeBase,
        skip_email_workflow: settingsData.value.skipEmailWorkflow,
        disable_saved_replies_global_scope:
          settingsData.value.disableSavedRepliesGlobalScope,
        enable_outside_hours_banner:
          settingsData.value.enableOutsideHoursBanner,
        outside_working_hours_message:
          settingsData.value.outsideWorkingHoursBannerMessage,
        enable_our_services: settingsData.value.enableOurServices,
        enable_buy_services: settingsData.value.enableBuyServices,
        enable_wiki: settingsData.value.enableWiki,
        our_services_content: settingsData.value.ourServicesContent,
      },
    };
  },
  onSuccess(data: HDSettings) {
    settingsData.value = transformData(data);
    initialData.value = JSON.stringify(settingsData.value);
  },
});

const transformData = (data: any) => {
  return {
    brandName: data.brand_name,
    brandLogo: data.brand_logo,
    favicon: data.favicon,
    autoCloseAfterDays: data.auto_close_after_days,
    autoCloseStatus: data.auto_close_status,
    autoCloseTickets: data.auto_close_tickets,
    assignWithinTeam: Boolean(data.assign_within_team),
    doNotRestrictTicketsWithoutAnAgentGroup: Boolean(
      data.do_not_restrict_tickets_without_an_agent_group
    ),
    restrictTicketsByAgentGroup: Boolean(data.restrict_tickets_by_agent_group),
    updateStatusTo: data.update_status_to,
    autoUpdateStatus: data.auto_update_status,
    isFeedbackMandatory: Boolean(data.is_feedback_mandatory),
    enableCommentReactions: Boolean(data.enable_comment_reactions),
    allowAnyoneToCreateTickets: Boolean(data.allow_anyone_to_create_tickets),
    defaultTicketType: data.default_ticket_type,
    preferKnowledgeBase: Boolean(data.prefer_knowledge_base),
    skipEmailWorkflow: Boolean(data.skip_email_workflow),
    disableSavedRepliesGlobalScope: Boolean(
      data.disable_saved_replies_global_scope
    ),
    enableOutsideHoursBanner: Boolean(data.enable_outside_hours_banner),
    outsideWorkingHoursBannerMessage: data.outside_working_hours_message || "",
    enableOurServices: data.enable_our_services !== undefined ? Boolean(data.enable_our_services) : true,
    enableBuyServices: data.enable_buy_services !== undefined ? Boolean(data.enable_buy_services) : true,
    enableWiki: data.enable_wiki !== undefined ? Boolean(data.enable_wiki) : true,
    ourServicesContent: data.our_services_content || "",
  };
};

const websiteSettingsResource = createResource({
  url: "frappe.client.get",
  params: {
    doctype: "Website Settings",
    name: "Website Settings",
    fields: ["disable_signup"],
  },
  auto: true,
  onSuccess(data: any) {
    disableSignup.value = Boolean(data.disable_signup);
  },
});

const saveWebsiteSettingsResource = createResource({
  url: "frappe.client.set_value",
  makeParams() {
    return {
      doctype: "Website Settings",
      name: "Website Settings",
      fieldname: {
        disable_signup: disableSignup.value,
      },
    };
  },
  onSuccess() {
    websiteSettingsResource.reload();
  },
});

const saveSettings = async () => {
  const promises = [];
  if (isDirty.value) {
    promises.push(saveSettingsResource.submit());
  }
  if (isWebsiteSettingsChanged.value) {
    promises.push(saveWebsiteSettingsResource.submit());
  }
  await Promise.allSettled(promises).then(() => {
    toast.success(__("Settings updated"));
  });
};

watch(
  settingsData,
  (data) => {
    if (!initialData.value) return;
    isDirty.value = JSON.stringify(data) !== initialData.value;
    if (isDirty.value) {
      disableSettingModalOutsideClick.value = true;
    } else {
      disableSettingModalOutsideClick.value = false;
    }
  },
  { deep: true }
);
</script>
