<template>
  <div
    class="grid grid-cols-6 items-center gap-4 cursor-pointer hover:bg-gray-50 rounded"
  >
    <div
      @click="activeScreen = { screen: 'view', data: data }"
      class="w-full pl-2 col-span-3 flex flex-col justify-center h-14"
    >
      <div class="text-base text-ink-gray-7 font-medium">
        {{ data.title }}
      </div>
    </div>
    <div class="col-span-1 text-sm text-ink-gray-5 truncate">
      {{ data.route || "-" }}
    </div>
    <div class="col-span-1">
      <Switch
        size="sm"
        :modelValue="data.published"
        @update:modelValue="onToggle"
      />
    </div>
    <div class="col-span-1 flex justify-end pr-2">
      <Dropdown placement="right" :options="dropdownOptions">
        <Button
          icon="more-horizontal"
          variant="ghost"
          @click="isConfirmingDelete = false"
        />
      </Dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Switch, Button, Dropdown, toast } from "frappe-ui";
import { ref, inject } from "vue";
import { ConfirmDelete } from "@/utils";
import { __ } from "@/translation";

const activeScreen = inject<any>("wikiActiveScreen");
const wikiList = inject<any>("wikiListResource");

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
});

const isConfirmingDelete = ref(false);

const dropdownOptions = [
  ...ConfirmDelete({
    onConfirmDelete: () => deletePage(),
    isConfirmingDelete,
  }),
];

const deletePage = () => {
  if (!isConfirmingDelete.value) {
    isConfirmingDelete.value = true;
    return;
  }
  wikiList?.delete.submit(props.data.name, {
    onSuccess: () => {
      toast.success(__("Wiki page deleted"));
    },
  });
};

const onToggle = () => {
  wikiList?.setValue.submit(
    {
      name: props.data.name,
      published: !props.data.published,
    },
    {
      onSuccess: () => {
        toast.success(__("Wiki page status updated"));
      },
    }
  );
};
</script>
