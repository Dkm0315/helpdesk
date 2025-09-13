<template>
  <div class="mt-7">
    <div class="flex items-center justify-between gap-2">
      <div>
        <div class="text-base font-medium text-ink-gray-8">
          {{ __("Dynamic User Assignments") }}
        </div>
        <div class="text-p-sm text-ink-gray-6 mt-1">
          {{ __("Select dynamic assignment rules to automatically add users based on conditions.") }}
        </div>
      </div>
      <Button
        variant="subtle"
        icon="plus"
        @click="showAssignmentModal = true"
      >
        {{ __("Add Assignment") }}
      </Button>
    </div>

    <div v-if="selectedAssignments.length > 0" class="mt-4 flex flex-wrap gap-2">
      <div
        v-for="assignment in selectedAssignments"
        :key="assignment.name"
        class="flex items-center gap-2 text-sm bg-surface-gray-2 rounded-md p-1 px-2 select-none"
      >
        <div class="flex items-center gap-2">
          <FeatherIcon name="users" class="size-4 text-ink-gray-6" />
          <span class="text-ink-gray-7">{{ assignment.assignment_name }}</span>
          <span class="text-xs text-ink-gray-5">
            ({{ assignment.user_count || 0 }} {{ __("users") }})
          </span>
        </div>
        <Button
          variant="ghost"
          icon="x"
          @click="removeAssignment(assignment)"
        />
      </div>
    </div>

    <ErrorMessage :message="assignmentRulesErrors.dynamicUserAssignments" />

    <Dialog
      v-model="showAssignmentModal"
      :options="{
        title: __('Select Dynamic User Assignment'),
        size: 'lg',
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            type="text"
            v-model="searchQuery"
            :placeholder="__('Search assignments...')"
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
              v-else-if="filteredAssignments.length === 0"
              class="text-center py-8 text-ink-gray-5"
            >
              {{ __("No assignments found") }}
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="assignment in filteredAssignments"
                :key="assignment.name"
                class="p-3 border rounded-lg hover:bg-surface-gray-1 cursor-pointer transition-colors"
                :class="{
                  'border-blue-500 bg-blue-50': isSelected(assignment),
                  'border-surface-gray-3': !isSelected(assignment),
                }"
                @click="toggleAssignment(assignment)"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="font-medium text-ink-gray-8">
                      {{ assignment.assignment_name }}
                    </div>
                    <div class="text-sm text-ink-gray-6 mt-1">
                      {{ assignment.description }}
                    </div>
                    <div class="flex items-center gap-4 mt-2 text-xs text-ink-gray-5">
                      <span class="flex items-center gap-1">
                        <FeatherIcon name="users" class="size-3" />
                        {{ assignment.user_count || 0 }} {{ __("users") }}
                      </span>
                      <span v-if="assignment.conditions_count" class="flex items-center gap-1">
                        <FeatherIcon name="filter" class="size-3" />
                        {{ assignment.conditions_count }} {{ __("conditions") }}
                      </span>
                    </div>
                  </div>
                  <Checkbox
                    :model-value="isSelected(assignment)"
                    @update:model-value="toggleAssignment(assignment)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="subtle" @click="showAssignmentModal = false">
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
  fetchDynamicUserAssignments,
  dynamicUserAssignmentsList,
  applyDynamicUserAssignment,
} from '../../../stores/assignmentRules';

const showAssignmentModal = ref(false);
const searchQuery = ref('');
const loading = ref(false);
const tempSelections = ref([]);

const selectedAssignments = computed(() => {
  return assignmentRuleData.value.dynamicUserAssignments || [];
});

const filteredAssignments = computed(() => {
  if (!searchQuery.value) {
    return dynamicUserAssignmentsList.value;
  }
  const query = searchQuery.value.toLowerCase();
  return dynamicUserAssignmentsList.value.filter(
    (assignment) =>
      assignment.assignment_name?.toLowerCase().includes(query) ||
      assignment.description?.toLowerCase().includes(query)
  );
});

const isSelected = (assignment) => {
  return tempSelections.value.some((a) => a.name === assignment.name);
};

const toggleAssignment = (assignment) => {
  const index = tempSelections.value.findIndex((a) => a.name === assignment.name);
  if (index > -1) {
    tempSelections.value.splice(index, 1);
  } else {
    tempSelections.value.push(assignment);
  }
};

const removeAssignment = (assignment) => {
  assignmentRuleData.value.dynamicUserAssignments = 
    assignmentRuleData.value.dynamicUserAssignments.filter(
      (a) => a.name !== assignment.name
    );
};

const applySelections = async () => {
  // Apply each selected dynamic assignment and get users
  const allUsers = [];
  const userEmails = new Set();
  
  for (const assignment of tempSelections.value) {
    const users = await applyDynamicUserAssignment(assignment.name);
    if (users && users.length > 0) {
      // Add fetched users to the assignment
      assignment.fetched_users = users;
      
      // Aggregate unique users
      users.forEach(user => {
        if (!userEmails.has(user.email || user.user)) {
          userEmails.add(user.email || user.user);
          allUsers.push({
            user: user.email || user.user,
            full_name: user.full_name,
            email: user.email || user.user,
            user_image: user.user_image
          });
        }
      });
    }
  }
  
  // Update both dynamic assignments and users
  assignmentRuleData.value.dynamicUserAssignments = [...tempSelections.value];
  
  // Add users from dynamic assignments to the users list
  if (allUsers.length > 0) {
    // Merge with existing users, avoiding duplicates
    const existingUserEmails = new Set(assignmentRuleData.value.users.map(u => u.user));
    allUsers.forEach(user => {
      if (!existingUserEmails.has(user.user)) {
        assignmentRuleData.value.users.push(user);
      }
    });
  }
  
  showAssignmentModal.value = false;
  tempSelections.value = [];
};

const loadAssignments = async () => {
  loading.value = true;
  try {
    await fetchDynamicUserAssignments();
  } finally {
    loading.value = false;
  }
};

watch(showAssignmentModal, (newVal) => {
  if (newVal) {
    tempSelections.value = [...selectedAssignments.value];
    loadAssignments();
  }
});

onMounted(() => {
  loadAssignments();
});
</script>