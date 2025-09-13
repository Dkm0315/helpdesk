<template>
  <div class="mt-7">
    <div class="flex items-center justify-between gap-2">
      <div>
        <div class="text-base font-medium text-ink-gray-8">
          {{ __("Holiday Lists") }}
        </div>
        <div class="text-p-sm text-ink-gray-6 mt-1">
          {{ __("Select holiday lists that affect SLA timing for assigned agents.") }}
        </div>
      </div>
      <Button
        variant="subtle"
        icon="plus"
        @click="showHolidayModal = true"
      >
        {{ __("Add Holiday List") }}
      </Button>
    </div>

    <div v-if="selectedHolidays.length > 0" class="mt-4 space-y-2">
      <div
        v-for="holiday in selectedHolidays"
        :key="holiday.name"
        class="flex items-center justify-between p-3 bg-surface-gray-2 rounded-lg"
      >
        <div class="flex items-center gap-3">
          <FeatherIcon name="calendar" class="size-5 text-ink-gray-6" />
          <div>
            <div class="text-sm font-medium text-ink-gray-8">
              {{ holiday.holiday_name || holiday.name }}
            </div>
            <div class="text-xs text-ink-gray-5 mt-0.5">
              {{ formatDate(holiday.date) }}
              <span v-if="holiday.type" class="ml-2">
                • {{ holiday.type }}
              </span>
              <span v-if="holiday.repeat_next_year" class="ml-2 text-blue-600">
                • Repeats Yearly
              </span>
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          icon="x"
          @click="removeHoliday(holiday)"
        />
      </div>
    </div>

    <ErrorMessage :message="assignmentRulesErrors.holidays" />

    <Dialog
      v-model="showHolidayModal"
      :options="{
        title: __('Select Holiday Lists'),
        size: 'lg',
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            type="text"
            v-model="searchQuery"
            :placeholder="__('Search holiday lists...')"
            class="mb-4"
          >
            <template #prefix>
              <FeatherIcon name="search" class="size-4" />
            </template>
          </FormControl>

          <div class="max-h-96 overflow-y-auto">
            <div v-if="loading" class="flex justify-center py-8">
              <Spinner />
            </div>
            <div
              v-else-if="filteredHolidays.length === 0"
              class="text-center py-8 text-ink-gray-5"
            >
              {{ __("No holiday lists found") }}
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="holiday in filteredHolidays"
                :key="holiday.name"
                class="p-3 border rounded-lg hover:bg-surface-gray-1 cursor-pointer transition-colors"
                :class="{
                  'border-blue-500 bg-blue-50': isSelected(holiday),
                  'border-surface-gray-3': !isSelected(holiday),
                }"
                @click="toggleHoliday(holiday)"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="font-medium text-ink-gray-8">
                      {{ holiday.holiday_name || holiday.name }}
                    </div>
                    <div class="text-sm text-ink-gray-6 mt-1">
                      {{ formatDate(holiday.date) }}
                      <span v-if="holiday.type" class="ml-2">
                        • {{ holiday.type }}
                      </span>
                    </div>
                    <div v-if="holiday.repeat_next_year" class="text-xs text-blue-600 mt-1">
                      Repeats Yearly
                    </div>
                  </div>
                  <Checkbox
                    :model-value="isSelected(holiday)"
                    @update:model-value="toggleHoliday(holiday)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="subtle" @click="showHolidayModal = false">
          {{ __("Cancel") }}
        </Button>
        <Button variant="solid" @click="applySelections">
          {{ __("Apply") }}
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { Button, Dialog, FormControl, ErrorMessage, Checkbox, Spinner } from 'frappe-ui';
import {
  assignmentRuleData,
  assignmentRulesErrors,
  fetchHolidays,
  holidaysList,
} from '../../../stores/assignmentRules';

const showHolidayModal = ref(false);
const searchQuery = ref('');
const loading = ref(false);
const tempSelections = ref([]);

const selectedHolidays = computed(() => {
  return assignmentRuleData.value.holidays || [];
});

const filteredHolidays = computed(() => {
  if (!searchQuery.value) {
    return holidaysList.value;
  }
  const query = searchQuery.value.toLowerCase();
  return holidaysList.value.filter(
    (holiday) =>
      holiday.holiday_name?.toLowerCase().includes(query) ||
      holiday.type?.toLowerCase().includes(query) ||
      holiday.date?.toLowerCase().includes(query)
  );
});

const isSelected = (holiday) => {
  return tempSelections.value.some((h) => h.name === holiday.name);
};

const toggleHoliday = (holiday) => {
  const index = tempSelections.value.findIndex((h) => h.name === holiday.name);
  if (index > -1) {
    tempSelections.value.splice(index, 1);
  } else {
    tempSelections.value.push(holiday);
  }
};

const removeHoliday = (holiday) => {
  assignmentRuleData.value.holidays = 
    assignmentRuleData.value.holidays.filter(
      (h) => h.name !== holiday.name
    );
};

const applySelections = () => {
  assignmentRuleData.value.holidays = [...tempSelections.value];
  showHolidayModal.value = false;
  tempSelections.value = [];
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric' 
  });
};

const loadHolidays = async () => {
  loading.value = true;
  try {
    await fetchHolidays();
  } finally {
    loading.value = false;
  }
};

watch(showHolidayModal, (newVal) => {
  if (newVal) {
    tempSelections.value = [...selectedHolidays.value];
    loadHolidays();
  }
});

onMounted(() => {
  loadHolidays();
});
</script>