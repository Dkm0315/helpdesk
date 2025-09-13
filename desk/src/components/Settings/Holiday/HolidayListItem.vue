<template>
  <div class="flex items-center cursor-pointer hover:bg-gray-50 rounded">
    <div
      class="w-full py-3 pl-2"
      @click="holidayListActiveScreen = { screen: 'view', data: data }"
    >
      <div class="text-base text-ink-gray-7 font-medium">{{ data.holiday_name || data.name }}</div>
      <div class="flex items-center gap-4 mt-1">
        <div class="text-sm text-ink-gray-5">
          {{ formatDate(data.date) }}
        </div>
        <div v-if="data.type" class="text-xs px-2 py-0.5 rounded bg-gray-100 text-ink-gray-6">
          {{ data.type }}
        </div>
        <div v-if="data.repeat_next_year" class="text-xs text-blue-600">
          Repeats Yearly
        </div>
      </div>
    </div>
    <div class="flex justify-between items-center pr-2">
      <div>
        <Dropdown placement="right" :options="dropdownOptions">
          <Button
            icon="more-horizontal"
            variant="ghost"
            @click="isConfirmingDelete = false"
          />
        </Dropdown>
      </div>
    </div>
  </div>
  <Dialog
    :options="{ title: `Duplicate Holiday List` }"
    v-model="duplicateDialog.show"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <FormControl
          label="New Holiday List Name"
          type="text"
          v-model="duplicateDialog.name"
        />
      </div>
    </template>
    <template #actions>
      <div class="flex gap-2 justify-end">
        <Button
          variant="subtle"
          label="Close"
          @click="duplicateDialog.show = false"
        />
        <Button variant="solid" label="Duplicate" @click="duplicate()" />
      </div>
    </template>
  </Dialog>
</template>
<script setup lang="ts">
import { Button, createResource, toast } from "frappe-ui";
import { inject, ref } from "vue";
import { holidayListActiveScreen } from "@/stores/holidayList";
import { ConfirmDelete } from "@/utils";

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  });
};

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
});

const holidayList = inject<any>("holidayList");

const duplicateDialog = ref({
  show: false,
  name: "",
});

const isConfirmingDelete = ref(false);

const dropdownOptions = [
  {
    label: "Duplicate",
    onClick: () => {
      duplicateDialog.value.show = true;
      duplicateDialog.value.name = props.data.name + " (Copy)";
    },
    icon: "copy",
  },
  ...ConfirmDelete({
    onConfirmDelete: () => deleteHolidayList(),
    isConfirmingDelete,
  }),
];

const duplicate = () => {
  // For Holidays doctype, we create a new holiday with the same data
  createResource({
    url: "helpdesk.api.holidays.create_holiday",
    params: {
      holiday_data: {
        holiday_name: duplicateDialog.value.name,
        date: props.data.date,
        type: props.data.type || "National Holiday",
        repeat_next_year: props.data.repeat_next_year || 0
      }
    },
    onSuccess: (data) => {
      holidayList.reload();
      toast.success("Holiday duplicated");
      duplicateDialog.value = {
        show: false,
        name: "",
      };
      setTimeout(() => {
        holidayListActiveScreen.value = {
          screen: "view",
          data: data,
        };
      }, 250);
    },
    auto: true,
  });
};

const deleteHolidayList = () => {
  if (!isConfirmingDelete.value) {
    isConfirmingDelete.value = true;
    return;
  }

  createResource({
    url: "helpdesk.api.holidays.delete_holiday",
    params: {
      holiday_name: props.data.name
    },
    onSuccess: () => {
      toast.success("Holiday deleted");
      holidayList.reload();
    },
    auto: true
  });
};
</script>
