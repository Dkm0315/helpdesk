<template>
  <div class="flex flex-col h-full">
    <div
      v-if="loading"
      class="flex items-center h-full justify-center"
    >
      <LoadingIndicator class="w-4" />
    </div>
    <div
      v-if="!loading"
      class="flex items-center justify-between sticky top-0 z-10 bg-white px-10 pt-8 pb-4"
    >
      <div>
        <div class="flex items-center gap-2">
          <Button
            variant="ghost"
            icon-left="chevron-left"
            :label="holidayData?.holiday_name || 'New Holiday'"
            size="md"
            @click="goBack()"
            class="cursor-pointer -ml-4 hover:bg-transparent focus:bg-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 focus-visible:none active:bg-transparent active:outline-none active:ring-0 active:ring-offset-0 active:text-ink-gray-5 font-semibold text-ink-gray-7 text-xl hover:opacity-70 !pr-0"
          />
          <Badge
            :variant="'subtle'"
            :theme="'orange'"
            size="sm"
            label="Unsaved changes"
            v-if="isDirty"
          />
        </div>
      </div>
      <div class="flex gap-2 items-center">
        <Button
          label="Save"
          theme="gray"
          variant="solid"
          @click="saveHoliday()"
          :disabled="Boolean(!isDirty && holidayListActiveScreen.data)"
          :loading="saveLoading"
        />
      </div>
    </div>

    <div v-if="!loading" class="px-10 pb-8 overflow-y-scroll h-full">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-6">
        <div>
          <FormControl
            :type="'text'"
            size="sm"
            variant="subtle"
            placeholder="Holiday Name"
            label="Holiday Name"
            v-model="holidayData.holiday_name"
            required
            @change="checkDirty"
          />
          <ErrorMessage
            :message="errors.holiday_name"
            class="mt-2"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-700 mb-1">Date <span class="text-red-500">*</span></label>
          <DatePicker
            v-model="holidayData.date"
            variant="subtle"
            placeholder="Select date"
            class="w-full"
            :formatter="(date) => getFormattedDate(date)"
            @update:model-value="checkDirty"
          />
          <ErrorMessage
            :message="errors.date"
            class="mt-2"
          />
        </div>
        <div>
          <FormControl
            :type="'select'"
            size="sm"
            variant="subtle"
            label="Type"
            v-model="holidayData.type"
            :options="[
              { label: 'National Holiday', value: 'National Holiday' },
              { label: 'Mandatory', value: 'Mandatory' },
              { label: 'Optional', value: 'Optional' }
            ]"
            @change="checkDirty"
          />
        </div>
        <div class="flex items-center gap-2 mt-6">
          <input
            type="checkbox"
            id="repeat_next_year"
            v-model="holidayData.repeat_next_year"
            @change="checkDirty"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="repeat_next_year" class="text-sm text-gray-700">
            Repeat Next Year
          </label>
        </div>
      </div>
    </div>
  </div>
  <ConfirmDialog
    v-model="showConfirmDialog"
    title="Unsaved changes"
    message="Are you sure you want to go back? Unsaved changes will be lost."
    :onConfirm="confirmGoBack"
    :onCancel="() => (showConfirmDialog = false)"
  />
</template>

<script setup lang="ts">
import {
  holidayListActiveScreen,
} from "@/stores/holidayList";
import {
  Button,
  createResource,
  DatePicker,
  FormControl,
  LoadingIndicator,
  toast,
  Badge,
  ErrorMessage
} from "frappe-ui";
import { inject, onMounted, onUnmounted, ref, reactive } from "vue";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import { getFormattedDate } from "@/utils";
import dayjs from "dayjs";

const isDirty = ref(false);
const initialData = ref(null);
const loading = ref(false);
const saveLoading = ref(false);
const showConfirmDialog = ref(false);

const holidayList = inject<any>("holidayList");

const holidayData = reactive({
  holiday_name: "",
  date: null,
  type: "National Holiday",
  repeat_next_year: false
});

const errors = reactive({
  holiday_name: "",
  date: ""
});

// Load holiday data if editing
if (holidayListActiveScreen.value.data?.name) {
  loading.value = true;
  createResource({
    url: "helpdesk.api.holidays.get_holiday_details",
    params: {
      holiday_name: holidayListActiveScreen.value.data.name,
    },
    onSuccess(data) {
      holidayData.holiday_name = data.holiday_name;
      holidayData.date = data.date;
      holidayData.type = data.type || "National Holiday";
      holidayData.repeat_next_year = data.repeat_next_year === 1;
      initialData.value = JSON.stringify(holidayData);
      loading.value = false;
    },
    auto: true
  });
} else {
  initialData.value = JSON.stringify(holidayData);
}

const checkDirty = () => {
  isDirty.value = JSON.stringify(holidayData) !== initialData.value;
};

const validate = () => {
  let isValid = true;
  errors.holiday_name = "";
  errors.date = "";

  if (!holidayData.holiday_name?.trim()) {
    errors.holiday_name = "Holiday name is required";
    isValid = false;
  }

  if (!holidayData.date) {
    errors.date = "Date is required";
    isValid = false;
  }

  return isValid;
};

const goBack = () => {
  if (isDirty.value) {
    showConfirmDialog.value = true;
    return;
  }
  confirmGoBack();
};

const confirmGoBack = () => {
  showConfirmDialog.value = false;
  holidayListActiveScreen.value = {
    screen: "list",
    data: null,
  };
};

const saveHoliday = () => {
  if (!validate()) {
    toast.error("Please fill in all required fields");
    return;
  }

  saveLoading.value = true;

  const holidayPayload = {
    holiday_name: holidayData.holiday_name,
    date: dayjs(holidayData.date).format("YYYY-MM-DD"),
    type: holidayData.type,
    repeat_next_year: holidayData.repeat_next_year ? 1 : 0
  };

  if (holidayListActiveScreen.value.data) {
    // Update existing holiday
    createResource({
      url: "helpdesk.api.holidays.update_holiday",
      params: {
        holiday_name: holidayListActiveScreen.value.data.name,
        holiday_data: holidayPayload
      },
      onSuccess() {
        toast.success("Holiday updated");
        holidayList.reload();
        holidayListActiveScreen.value = {
          screen: "list",
          data: null,
        };
        saveLoading.value = false;
      },
      onError(error) {
        toast.error(error.message || "Failed to update holiday");
        saveLoading.value = false;
      },
      auto: true
    });
  } else {
    // Create new holiday
    createResource({
      url: "helpdesk.api.holidays.create_holiday",
      params: {
        holiday_data: holidayPayload
      },
      onSuccess() {
        toast.success("Holiday created");
        holidayList.reload();
        holidayListActiveScreen.value = {
          screen: "list",
          data: null,
        };
        saveLoading.value = false;
      },
      onError(error) {
        toast.error(error.message || "Failed to create holiday");
        saveLoading.value = false;
      },
      auto: true
    });
  }
};

const beforeUnloadHandler = (event) => {
  if (!isDirty.value) return;
  event.preventDefault();
  event.returnValue = true;
};

onMounted(() => {
  addEventListener("beforeunload", beforeUnloadHandler);
});

onUnmounted(() => {
  removeEventListener("beforeunload", beforeUnloadHandler);
});
</script>