<template>
  <SettingsLayoutBase
    :description="__(
      'Manage the editable Support Plan page shown in the sidebar.'
    )"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <h1 class="text-lg font-semibold text-ink-gray-8">
          {{ __("Support Plan") }}
        </h1>
        <Badge
          v-if="isDirty"
          variant="subtle"
          theme="orange"
          size="sm"
          :label="__('Unsaved')"
        />
      </div>
    </template>
    <template #header-actions>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <Switch v-model="formData.enabled" :disabled="!isEditing" size="sm" />
          <span class="text-sm font-medium text-ink-gray-7">
            {{ __("Enabled") }}
          </span>
        </div>
        <Button
          v-if="!isEditing"
          variant="ghost"
          icon-left="edit-2"
          :label="__('Edit')"
          @click="isEditing = true"
        />
        <template v-else>
          <Button variant="ghost" :label="__('Cancel')" @click="cancelEditing" />
          <Button
            variant="solid"
            :label="__('Save')"
            :loading="saveResource.loading"
            :disabled="!isDirty"
            @click="saveSupportPlan"
          />
        </template>
      </div>
    </template>
    <template #content>
      <div v-if="supportPlanResource.loading && !initialData" class="flex items-center justify-center mt-12">
        <LoadingIndicator class="w-4" />
      </div>
      <div v-else class="flex flex-col gap-6">
        <FormControl
          type="text"
          size="sm"
          variant="subtle"
          :label="__('Title')"
          :placeholder="__('Support Plan')"
          v-model="formData.title"
          :disabled="!isEditing"
          required
        />

        <div v-if="isEditing" class="space-y-1.5">
          <FormLabel :label="__('Content')" required />
          <TextEditor
            editor-class="!prose-sm max-w-full overflow-auto min-h-[360px] max-h-[640px] py-1.5 px-2 rounded-b border border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:shadow-sm focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors -mt-0.5"
            :bubble-menu="false"
            :content="formData.content"
            @change="formData.content = $event"
            :fixed-menu="editorMenu"
            :placeholder="__('Write the support plan content here...')"
          />
        </div>

        <div v-else class="rounded-lg border border-outline-gray-2 bg-surface-gray-1 p-4">
          <div
            v-if="formData.content"
            class="support-plan-content prose prose-sm max-w-none"
            v-html="formData.content"
          />
          <p v-else class="text-p-sm text-ink-gray-6">
            {{ __("No content has been added yet.") }}
          </p>
        </div>
      </div>
    </template>
  </SettingsLayoutBase>
</template>

<script setup lang="ts">
import { __ } from "@/translation";
import SettingsLayoutBase from "@/components/layouts/SettingsLayoutBase.vue";
import {
  Badge,
  Button,
  createResource,
  FormControl,
  FormLabel,
  LoadingIndicator,
  Switch,
  TextEditor,
  toast,
} from "frappe-ui";
import { computed, onUnmounted, ref, watch } from "vue";
import { disableSettingModalOutsideClick } from "../settingsModal";

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
  ["InsertTable", "AddRowAfter", "AddColumnAfter", "DeleteTable"],
];

const isEditing = ref(false);
const initialData = ref<string | null>(null);
const formData = ref({
  title: "",
  content: "",
  enabled: true,
});

const isDirty = computed(() => {
  if (!initialData.value) return false;
  return JSON.stringify(formData.value) !== initialData.value;
});

const supportPlanResource = createResource({
  url: "frappe.client.get",
  params: {
    doctype: "HD Support Plan",
    name: "HD Support Plan",
  },
  auto: true,
  onSuccess(data: any) {
    formData.value = {
      title: data.title || __("Support Plan"),
      content: data.content || "",
      enabled: Boolean(data.enabled),
    };
    initialData.value = JSON.stringify(formData.value);
  },
});

const saveResource = createResource({
  url: "frappe.client.set_value",
  makeParams() {
    return {
      doctype: "HD Support Plan",
      name: "HD Support Plan",
      fieldname: {
        title: formData.value.title,
        content: formData.value.content,
        enabled: formData.value.enabled,
      },
    };
  },
  onSuccess(data: any) {
    formData.value = {
      title: data.title || __("Support Plan"),
      content: data.content || "",
      enabled: Boolean(data.enabled),
    };
    initialData.value = JSON.stringify(formData.value);
    isEditing.value = false;
    toast.success(__("Support Plan updated"));
  },
});

const cancelEditing = () => {
  if (!initialData.value) return;
  formData.value = JSON.parse(initialData.value);
  isEditing.value = false;
};

const saveSupportPlan = () => {
  if (!formData.value.title?.trim()) {
    toast.error(__("Title is required"));
    return;
  }

  if (!formData.value.content?.trim()) {
    toast.error(__("Content is required"));
    return;
  }

  saveResource.submit();
};

watch(
  [isEditing, isDirty],
  ([editing, dirty]) => {
    disableSettingModalOutsideClick.value = editing || dirty;
  },
  { immediate: true }
);

onUnmounted(() => {
  disableSettingModalOutsideClick.value = false;
});
</script>

<style>
.support-plan-content table {
  @apply w-full border-collapse overflow-hidden rounded-lg;
}

.support-plan-content th,
.support-plan-content td {
  @apply border border-outline-gray-2 px-3 py-2 align-top text-p-sm text-ink-gray-7;
}

.support-plan-content th {
  @apply bg-surface-gray-2 font-semibold text-ink-gray-9;
}

.support-plan-content tbody tr:nth-child(even) {
  @apply bg-surface-gray-1;
}

.support-plan-content p {
  @apply my-2;
}
</style>
