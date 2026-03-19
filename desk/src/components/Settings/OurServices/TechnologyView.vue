<template>
  <SettingsLayoutBase>
    <template #title>
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          icon-left="chevron-left"
          :label="techData.technology_name || __('New Technology')"
          size="md"
          @click="goBack()"
          class="cursor-pointer -ml-4 hover:bg-transparent focus:bg-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 focus-visible:none active:bg-transparent active:outline-none active:ring-0 active:ring-offset-0 active:text-ink-gray-5 font-semibold text-ink-gray-7 text-lg hover:opacity-70 !pr-0"
        />
        <Badge
          variant="subtle"
          theme="orange"
          size="sm"
          :label="__('Unsaved')"
          v-if="isDirty"
        />
      </div>
    </template>
    <template #header-actions>
      <div class="flex gap-4 items-center">
        <div
          class="flex items-center justify-between gap-2 cursor-pointer"
          @click="techData.enabled = !techData.enabled"
        >
          <Switch size="sm" v-model="techData.enabled" />
          <span class="text-sm text-ink-gray-7 font-medium">
            {{ __("Enabled") }}
          </span>
        </div>
        <Button
          :label="__('Save')"
          theme="gray"
          variant="solid"
          @click="onSave()"
          :disabled="Boolean(!isDirty && activeScreen.data)"
          :loading="saving"
        />
      </div>
    </template>
    <template #content>
      <div
        v-if="loading"
        class="flex items-center h-full justify-center"
      >
        <LoadingIndicator class="w-4" />
      </div>
      <div v-else>
        <!-- Basic Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <FormControl
            type="text"
            size="sm"
            variant="subtle"
            :placeholder="__('e.g. Redis')"
            :label="__('Technology Name')"
            v-model="techData.technology_name"
            required
            :disabled="Boolean(activeScreen.data)"
            maxlength="140"
          />
          <div class="grid grid-cols-2 gap-3">
            <FormControl
              type="text"
              size="sm"
              variant="subtle"
              :placeholder="__('e.g. R')"
              :label="__('Icon Letter')"
              v-model="techData.icon_letter"
              maxlength="2"
            />
            <div class="space-y-1.5">
              <FormLabel :label="__('Icon Color')" />
              <Select
                v-model="techData.icon_color"
                :options="colorOptions"
              />
            </div>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
          <FormControl
            type="textarea"
            size="sm"
            variant="subtle"
            :placeholder="__('Short description for the card')"
            :label="__('Short Description')"
            v-model="techData.description"
          />
          <FormControl
            type="textarea"
            size="sm"
            variant="subtle"
            :placeholder="__('Introduction text for the detail page')"
            :label="__('Detail Page Introduction')"
            v-model="techData.detail_intro"
          />
        </div>
        <div class="mt-5">
          <FormControl
            type="number"
            size="sm"
            variant="subtle"
            :label="__('Sort Order')"
            v-model="techData.sort_order"
          />
        </div>

        <hr class="my-8" />

        <!-- Service Tiers -->
        <div>
          <div class="flex items-center justify-between">
            <div class="flex flex-col gap-1">
              <span class="text-lg font-semibold text-ink-gray-8">
                {{ __("Service Tiers") }}
              </span>
              <span class="text-p-sm text-ink-gray-6">
                {{ __("Define the support tiers offered for this technology.") }}
              </span>
            </div>
            <Button
              :label="__('Add Tier')"
              theme="gray"
              variant="subtle"
              icon-left="plus"
              @click="addTier()"
            />
          </div>

          <div
            v-if="!techData.service_tiers?.length"
            class="mt-4 text-center text-sm text-ink-gray-5 py-8 border border-dashed border-gray-300 rounded-lg"
          >
            {{ __("No service tiers yet. Click 'Add Tier' to create one.") }}
          </div>

          <div
            v-for="(tier, idx) in techData.service_tiers"
            :key="tier._id"
            class="mt-4 border rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-3">
              <span class="text-base font-medium text-ink-gray-8">
                {{ tier.tier_name || __("Tier") + " " + (idx + 1) }}
              </span>
              <Button
                icon="trash-2"
                variant="ghost"
                theme="red"
                @click="removeTier(idx)"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                :label="__('Tier Name')"
                :placeholder="__('e.g. L1 - Operational Support')"
                v-model="tier.tier_name"
                required
              />
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                :label="__('Primary Role / Description')"
                :placeholder="__('Brief description of this tier')"
                v-model="tier.tier_description"
              />
            </div>

            <div class="mt-4 space-y-1.5">
              <FormLabel :label="__('Responsibilities')" />
              <TextEditor
                editor-class="!prose-sm max-w-full overflow-auto min-h-[120px] max-h-60 py-1.5 px-2 rounded-b border border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:shadow-sm focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors -mt-0.5"
                :bubble-menu="false"
                :content="tier.responsibilities || ''"
                @change="tier.responsibilities = $event"
                :fixed-menu="editorMenu"
                :placeholder="__('List responsibilities, one per line')"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <FormControl
                type="textarea"
                size="sm"
                variant="subtle"
                :label="__('Tools & Methods')"
                :placeholder="__('Tools and methods used')"
                v-model="tier.tools_methods"
              />
              <FormControl
                type="textarea"
                size="sm"
                variant="subtle"
                :label="__('Out of Scope')"
                :placeholder="__('What is not covered')"
                v-model="tier.out_of_scope"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </SettingsLayoutBase>
  <ConfirmDialog
    v-model="showConfirmDialog.show"
    :title="showConfirmDialog.title"
    :message="showConfirmDialog.message"
    :onConfirm="showConfirmDialog.onConfirm"
    :onCancel="() => (showConfirmDialog.show = false)"
  />
</template>

<script setup lang="ts">
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import {
  Badge,
  Button,
  createResource,
  FormControl,
  FormLabel,
  LoadingIndicator,
  Select,
  Switch,
  TextEditor,
  toast,
} from "frappe-ui";
import { inject, onUnmounted, ref, watch } from "vue";
import { disableSettingModalOutsideClick } from "../settingsModal";
import { __ } from "@/translation";
import SettingsLayoutBase from "@/components/layouts/SettingsLayoutBase.vue";

const activeScreen = inject<any>("techActiveScreen");
const techList = inject<any>("techListResource");

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

const colorOptions = [
  { label: "Red", value: "Red" },
  { label: "Orange", value: "Orange" },
  { label: "Green", value: "Green" },
  { label: "Blue", value: "Blue" },
  { label: "Purple", value: "Purple" },
  { label: "Indigo", value: "Indigo" },
];

const showConfirmDialog = ref({
  show: false,
  title: "",
  message: "",
  onConfirm: () => {},
});

const isDirty = ref(false);
const initialData = ref<string | null>(null);
const loading = ref(false);
const saving = ref(false);

const techData = ref({
  technology_name: "",
  description: "",
  detail_intro: "",
  icon_letter: "",
  icon_color: "Blue",
  sort_order: 0,
  enabled: true,
  service_tiers: [] as any[],
});

let tierIdCounter = 0;

const addTier = () => {
  techData.value.service_tiers.push({
    _id: `new_${tierIdCounter++}`,
    tier_name: "",
    tier_description: "",
    responsibilities: "",
    tools_methods: "",
    out_of_scope: "",
  });
};

const removeTier = (idx: number) => {
  techData.value.service_tiers.splice(idx, 1);
};

// Load existing data
const getTechData = createResource({
  url: "frappe.client.get",
  params: {
    doctype: "HD Supported Technology",
    name: activeScreen.value.data?.name,
  },
  auto: false,
  onSuccess(data: any) {
    techData.value = {
      technology_name: data.technology_name || "",
      description: data.description || "",
      detail_intro: data.detail_intro || "",
      icon_letter: data.icon_letter || "",
      icon_color: data.icon_color || "Blue",
      sort_order: data.sort_order || 0,
      enabled: Boolean(data.enabled),
      service_tiers: (data.service_tiers || []).map((t: any) => ({
        ...t,
        _id: t.name || `existing_${tierIdCounter++}`,
      })),
    };
    initialData.value = JSON.stringify(techData.value);
    loading.value = false;
  },
});

if (activeScreen.value.data?.name) {
  loading.value = true;
  getTechData.submit();
} else {
  initialData.value = JSON.stringify(techData.value);
  disableSettingModalOutsideClick.value = true;
}

const goBack = () => {
  const confirmDialogInfo = {
    show: true,
    title: __("Unsaved changes"),
    message: __(
      "Are you sure you want to go back? Unsaved changes will be lost."
    ),
    onConfirm: goBack,
  };
  if (isDirty.value && !showConfirmDialog.value.show) {
    showConfirmDialog.value = confirmDialogInfo;
    return;
  }
  if (!activeScreen.value.data && !showConfirmDialog.value.show) {
    showConfirmDialog.value = confirmDialogInfo;
    return;
  }
  setTimeout(() => {
    activeScreen.value = {
      screen: "list",
      data: null,
    };
  }, 250);
  showConfirmDialog.value.show = false;
};

const onSave = () => {
  if (!techData.value.technology_name?.trim()) {
    toast.error(__("Technology name is required"));
    return;
  }

  if (activeScreen.value.data) {
    updateTech();
  } else {
    createTech();
  }
};

const createTech = () => {
  saving.value = true;
  techList?.insert.submit(
    {
      technology_name: techData.value.technology_name,
      description: techData.value.description,
      detail_intro: techData.value.detail_intro,
      icon_letter: techData.value.icon_letter,
      icon_color: techData.value.icon_color,
      sort_order: techData.value.sort_order,
      enabled: techData.value.enabled,
      service_tiers: techData.value.service_tiers.map((t) => ({
        tier_name: t.tier_name,
        tier_description: t.tier_description,
        responsibilities: t.responsibilities,
        tools_methods: t.tools_methods,
        out_of_scope: t.out_of_scope,
      })),
    },
    {
      onSuccess(data: any) {
        saving.value = false;
        toast.success(__("Technology created"));
        activeScreen.value = {
          screen: "view",
          data: { name: data.name },
        };
        loading.value = true;
        getTechData.submit({
          doctype: "HD Supported Technology",
          name: data.name,
        });
      },
      onError() {
        saving.value = false;
      },
    }
  );
};

const updateTech = () => {
  saving.value = true;
  techList?.setValue.submit(
    {
      name: activeScreen.value.data.name,
      description: techData.value.description,
      detail_intro: techData.value.detail_intro,
      icon_letter: techData.value.icon_letter,
      icon_color: techData.value.icon_color,
      sort_order: techData.value.sort_order,
      enabled: techData.value.enabled,
      service_tiers: techData.value.service_tiers.map((t) => ({
        tier_name: t.tier_name,
        tier_description: t.tier_description,
        responsibilities: t.responsibilities,
        tools_methods: t.tools_methods,
        out_of_scope: t.out_of_scope,
      })),
    },
    {
      onSuccess() {
        saving.value = false;
        toast.success(__("Technology updated"));
        getTechData.submit();
        techList.reload();
      },
      onError() {
        saving.value = false;
      },
    }
  );
};

watch(
  techData,
  (newVal) => {
    if (!initialData.value) return;
    isDirty.value = JSON.stringify(newVal) !== initialData.value;
    if (isDirty.value) {
      disableSettingModalOutsideClick.value = true;
    } else {
      disableSettingModalOutsideClick.value = false;
    }
  },
  { deep: true }
);

onUnmounted(() => {
  disableSettingModalOutsideClick.value = false;
});
</script>
