<template>
  <div
    class="grid grid-cols-6 items-center gap-4 cursor-pointer hover:bg-gray-50 rounded"
  >
    <div
      @click="
        activeScreen = { screen: 'view', data: data }
      "
      class="w-full pl-2 col-span-3 flex items-center gap-3 h-14"
    >
      <div
        class="flex items-center justify-center w-8 h-8 rounded text-sm font-bold"
        :class="colorClasses"
      >
        {{ data.icon_letter || data.technology_name?.charAt(0) }}
      </div>
      <div class="flex flex-col">
        <div class="text-base text-ink-gray-7 font-medium">
          {{ data.technology_name }}
        </div>
        <div
          v-if="data.description"
          class="text-sm text-ink-gray-5 truncate max-w-xs"
        >
          {{ data.description }}
        </div>
      </div>
    </div>
    <div class="col-span-1 text-sm text-ink-gray-6">
      {{ data.sort_order || 0 }}
    </div>
    <div class="col-span-1">
      <Switch
        size="sm"
        :modelValue="data.enabled"
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
import { ref, inject, computed } from "vue";
import { ConfirmDelete } from "@/utils";
import { __ } from "@/translation";

const activeScreen = inject<any>("techActiveScreen");
const techList = inject<any>("techListResource");

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
});

const COLOR_MAP: Record<string, { bg: string; text: string }> = {
  Red: { bg: "bg-red-100", text: "text-red-600" },
  Orange: { bg: "bg-orange-100", text: "text-orange-600" },
  Green: { bg: "bg-green-100", text: "text-green-600" },
  Blue: { bg: "bg-blue-100", text: "text-blue-600" },
  Purple: { bg: "bg-purple-100", text: "text-purple-600" },
  Indigo: { bg: "bg-indigo-100", text: "text-indigo-600" },
};

const colorClasses = computed(() => {
  const c = COLOR_MAP[props.data.icon_color] || COLOR_MAP.Blue;
  return `${c.bg} ${c.text}`;
});

const isConfirmingDelete = ref(false);

const dropdownOptions = [
  ...ConfirmDelete({
    onConfirmDelete: () => deleteTech(),
    isConfirmingDelete,
  }),
];

const deleteTech = () => {
  if (!isConfirmingDelete.value) {
    isConfirmingDelete.value = true;
    return;
  }
  techList?.delete.submit(props.data.name, {
    onSuccess: () => {
      toast.success(__("Technology deleted"));
    },
  });
};

const onToggle = () => {
  techList?.setValue.submit(
    {
      name: props.data.name,
      enabled: !props.data.enabled,
    },
    {
      onSuccess: () => {
        toast.success(__("Technology status updated"));
      },
    }
  );
};
</script>
