<template>
  <SettingsLayoutBase>
    <template #title>
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          icon-left="chevron-left"
          :label="pageData.title || __('New Wiki Page')"
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
          @click="pageData.published = !pageData.published"
        >
          <Switch size="sm" v-model="pageData.published" />
          <span class="text-sm text-ink-gray-7 font-medium">
            {{ __("Published") }}
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
      <div v-else class="flex flex-col gap-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <FormControl
            type="text"
            size="sm"
            variant="subtle"
            :placeholder="__('Page Title')"
            :label="__('Title')"
            v-model="pageData.title"
            required
            maxlength="140"
          />
          <FormControl
            type="text"
            size="sm"
            variant="subtle"
            :placeholder="__('e.g. my-wiki/page-slug')"
            :label="__('Route')"
            v-model="pageData.route"
          />
        </div>
        <div class="space-y-1.5">
          <FormLabel :label="__('Content (Markdown)')" required />
          <textarea
            v-model="pageData.content"
            class="w-full rounded border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-700 font-mono focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
            rows="20"
            :placeholder="__('Write your wiki page content in Markdown...')"
          />
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
  Switch,
  toast,
} from "frappe-ui";
import { inject, onUnmounted, ref, watch } from "vue";
import { disableSettingModalOutsideClick } from "../settingsModal";
import { __ } from "@/translation";
import SettingsLayoutBase from "@/components/layouts/SettingsLayoutBase.vue";

const activeScreen = inject<any>("wikiActiveScreen");
const wikiList = inject<any>("wikiListResource");

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

const pageData = ref({
  title: "",
  route: "",
  content: "",
  published: true,
});

const getPageData = createResource({
  url: "frappe.client.get",
  params: {
    doctype: "Wiki Page",
    name: activeScreen.value.data?.name,
  },
  auto: false,
  onSuccess(data: any) {
    pageData.value = {
      title: data.title || "",
      route: data.route || "",
      content: data.content || "",
      published: Boolean(data.published),
    };
    initialData.value = JSON.stringify(pageData.value);
    loading.value = false;
  },
});

if (activeScreen.value.data?.name) {
  loading.value = true;
  getPageData.submit();
} else {
  initialData.value = JSON.stringify(pageData.value);
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
  if (!pageData.value.title?.trim()) {
    toast.error(__("Title is required"));
    return;
  }

  if (activeScreen.value.data) {
    updatePage();
  } else {
    createPage();
  }
};

const createPage = () => {
  saving.value = true;
  wikiList?.insert.submit(
    {
      title: pageData.value.title,
      route: pageData.value.route,
      content: pageData.value.content,
      published: pageData.value.published,
    },
    {
      onSuccess(data: any) {
        saving.value = false;
        toast.success(__("Wiki page created"));
        activeScreen.value = {
          screen: "view",
          data: { name: data.name },
        };
        loading.value = true;
        getPageData.submit({
          doctype: "Wiki Page",
          name: data.name,
        });
      },
      onError() {
        saving.value = false;
      },
    }
  );
};

const updatePage = () => {
  saving.value = true;
  wikiList?.setValue.submit(
    {
      name: activeScreen.value.data.name,
      title: pageData.value.title,
      route: pageData.value.route,
      content: pageData.value.content,
      published: pageData.value.published,
    },
    {
      onSuccess() {
        saving.value = false;
        toast.success(__("Wiki page updated"));
        getPageData.submit();
        wikiList.reload();
      },
      onError() {
        saving.value = false;
      },
    }
  );
};

watch(
  pageData,
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
