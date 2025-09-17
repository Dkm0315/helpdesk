<template>
  <div
    v-if="getAssignmentRuleData.loading"
    class="flex items-center h-full justify-center"
  >
    <LoadingIndicator class="w-4" />
  </div>
  <div
    v-if="!getAssignmentRuleData.loading"
    class="sticky top-0 z-10 bg-white pb-6 px-10 py-8"
  >
    <div class="flex items-center justify-between w-full">
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          icon-left="chevron-left"
          :label="
            assignmentRuleData.assignmentRuleName || 'New Assignment Rule'
          "
          size="md"
          @click="goBack()"
          class="cursor-pointer -ml-4 hover:bg-transparent focus:bg-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 focus-visible:none active:bg-transparent active:outline-none active:ring-0 active:ring-offset-0 active:text-ink-gray-5 font-semibold text-xl hover:opacity-70 !pr-0 !max-w-96 !justify-start"
        />
        <Badge
          :variant="'subtle'"
          :theme="'orange'"
          size="sm"
          :label="__('Unsaved')"
          v-if="isDirty"
        />
      </div>
      <div class="flex items-center gap-4">
        <div
          class="flex items-center justify-between gap-2"
          @click="assignmentRuleData.disabled = !assignmentRuleData.disabled"
        >
          <Switch size="sm" :model-value="!assignmentRuleData.disabled" />
          <span class="text-sm text-ink-gray-7">{{ __("Enabled") }}</span>
        </div>
        <Button
          :disabled="Boolean(!isDirty && assignmentRulesActiveScreen.data)"
          :label="__('Save')"
          theme="gray"
          variant="solid"
          @click="saveAssignmentRule()"
          :loading="isLoading || getAssignmentRuleData.loading"
        />
      </div>
    </div>
  </div>
  <div v-if="!getAssignmentRuleData.loading" class="overflow-y-auto px-10 pb-8">
    <div class="grid grid-cols-2 gap-5">
      <div>
        <FormControl
          :type="'text'"
          size="sm"
          variant="subtle"
          placeholder="Name"
          label="Name"
          v-model="assignmentRuleData.assignmentRuleName"
          required
          maxlength="50"
          @change="validateAssignmentRule('assignmentRuleName')"
        />
        <ErrorMessage
          :message="assignmentRulesErrors.assignmentRuleName"
          class="mt-2"
        />
      </div>
      <div class="flex flex-col gap-1.5">
        <FormLabel label="Priority" />
        <Popover>
          <template #target="{ togglePopover }">
            <div
              class="flex items-center justify-between text-base rounded h-7 py-1.5 pl-2 pr-2 border border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:bg-surface-gray-3 focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors w-full dark:[color-scheme:dark] cursor-default"
              @click="togglePopover()"
            >
              <div>
                {{
                  priorityOptions.find(
                    (option) => option.value == assignmentRuleData.priority
                  )?.label
                }}
              </div>
              <FeatherIcon name="chevron-down" class="size-4" />
            </div>
          </template>
          <template #body="{ togglePopover }">
            <div
              class="p-1 text-ink-gray-6 top-1 absolute w-full bg-white shadow-2xl rounded"
            >
              <div
                v-for="option in priorityOptions"
                :key="option.value"
                class="p-2 cursor-pointer hover:bg-gray-50 text-base flex items-center justify-between rounded"
                @click="
                  assignmentRuleData.priority = option.value;
                  togglePopover();
                "
              >
                {{ option.label }}
                <FeatherIcon
                  v-if="assignmentRuleData.priority == option.value"
                  name="check"
                  class="size-4"
                />
              </div>
            </div>
          </template>
        </Popover>
      </div>
      <div>
        <FormControl
          :type="'textarea'"
          size="sm"
          variant="subtle"
          placeholder="Description"
          label="Description"
          required
          maxlength="250"
          @change="validateAssignmentRule('description')"
          v-model="assignmentRuleData.description"
        />
        <ErrorMessage
          :message="assignmentRulesErrors.description"
          class="mt-2"
        />
      </div>
    </div>
    <hr class="my-8" />
    <div>
      <div class="flex flex-col gap-1">
        <span class="text-lg font-semibold text-ink-gray-8">{{
          __("Assignment condition")
        }}</span>
        <div class="flex items-center justify-between gap-6">
          <span class="text-p-sm text-ink-gray-6">
            {{
              __("Choose which tickets are affected by this assignment rule.")
            }}
            <a
              class="font-medium underline"
              href="https://docs.frappe.io/helpdesk/assignment-rule"
              target="_blank"
              >{{ __("Learn about conditions") }}</a
            >
          </span>
          <div v-if="isOldSla && assignmentRulesActiveScreen.data">
            <Popover trigger="hover" :hoverDelay="0.25" placement="top-end">
              <template #target>
                <div
                  class="text-sm text-ink-gray-6 flex gap-1 cursor-default text-nowrap flex items-center"
                >
                  <span>{{ __("Old Condition") }}</span>
                  <FeatherIcon name="info" class="size-4" />
                </div>
              </template>
              <template #body-main>
                <div
                  class="text-sm text-ink-gray-6 p-2 bg-white rounded-md max-w-96 text-wrap whitespace-pre-wrap leading-5"
                >
                  <code>{{ assignmentRuleData.assignCondition }}</code>
                </div>
              </template>
            </Popover>
          </div>
        </div>
      </div>
      <div class="mt-5">
        <div
          class="flex flex-col gap-3 items-center text-center text-ink-gray-7 text-sm mb-2 border border-gray-300 rounded-md p-3 py-4"
          v-if="!useNewUI && assignmentRuleData.assignCondition"
        >
          <span class="text-p-sm">
            Conditions for this rule were created from
            <a :href="deskUrl" target="_blank" class="underline">desk</a> which
            are not compatible with this UI, you will need to recreate the
            conditions here if you want to manage and add new conditions from
            this UI.
          </span>
          <Button
            label="I understand, add conditions"
            variant="subtle"
            theme="gray"
            @click="useNewUI = true"
          />
        </div>
        <AssignmentRulesSection
          :conditions="assignmentRuleData.assignConditionJson"
          name="assignCondition"
          :errors="assignmentRulesErrors.assignConditionError"
          v-else
        />
        <ErrorMessage
          :message="assignmentRulesErrors.assignCondition"
          class="mt-2"
        />
      </div>
    </div>
    <hr class="my-8" />
    <div>
      <div class="flex flex-col gap-1">
        <span class="text-lg font-semibold text-ink-gray-8">{{
          __("Unassignment condition")
        }}</span>
        <div class="flex items-center justify-between gap-6">
          <span class="text-p-sm text-ink-gray-6">
            {{
              __(
                "Choose which tickets are affected by this un-assignment rule."
              )
            }}
            <a
              class="font-medium underline"
              href="https://docs.frappe.io/helpdesk/assignment-rule"
              target="_blank"
              >{{ __("Learn about conditions") }}</a
            >
          </span>
          <div
            v-if="
              isOldSla &&
              assignmentRulesActiveScreen.data &&
              assignmentRuleData.unassignCondition
            "
          >
            <Popover trigger="hover" :hoverDelay="0.25" placement="top-end">
              <template #target>
                <div
                  class="text-sm text-ink-gray-6 flex gap-1 cursor-default text-nowrap flex items-center"
                >
                  <span> {{ __("Old Condition") }} </span>
                  <FeatherIcon name="info" class="size-4" />
                </div>
              </template>
              <template #body-main>
                <div
                  class="text-sm text-ink-gray-6 p-2 bg-white rounded-md max-w-96 text-wrap whitespace-pre-wrap leading-5"
                >
                  <code>{{ assignmentRuleData.unassignCondition }}</code>
                </div>
              </template>
            </Popover>
          </div>
        </div>
      </div>
      <div class="mt-5">
        <div
          class="flex flex-col gap-3 items-center text-center text-ink-gray-7 text-sm mb-2 border border-gray-300 rounded-md p-3 py-4"
          v-if="!useNewUI && assignmentRuleData.unassignCondition"
        >
          <span class="text-p-sm">
            Conditions for this rule were created from
            <a :href="deskUrl" target="_blank" class="underline">desk</a> which
            are not compatible with this UI, you will need to recreate the
            conditions here if you want to manage and add new conditions from
            this UI.
          </span>
          <Button
            label="I understand, add conditions"
            variant="subtle"
            theme="gray"
            @click="useNewUI = true"
          />
        </div>
        <AssignmentRulesSection
          :conditions="assignmentRuleData.unassignConditionJson"
          name="unassignCondition"
          :errors="assignmentRulesErrors.unassignConditionError"
          v-else
        />
      </div>
    </div>
    <hr class="my-8" />
    <div>
      <div class="flex flex-col gap-1">
        <span class="text-lg font-semibold text-ink-gray-8">{{
          __("Assignment Schedule")
        }}</span>
        <span class="text-p-sm text-ink-gray-6">
          {{
            __("Choose the days of the week when this rule should be active.")
          }}
        </span>
      </div>
      <div class="mt-6">
        <AssignmentSchedule />
      </div>
    </div>
    <hr class="my-8" />
    <AssigneeRules />
  </div>
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
  call,
  createResource,
  ErrorMessage,
  FormControl,
  FormLabel,
  LoadingIndicator,
  Popover,
  Switch,
  toast,
} from "frappe-ui";
import { onMounted, onUnmounted, ref, watch } from "vue";
import {
  assignmentRuleData,
  assignmentRulesActiveScreen,
  assignmentRulesErrors,
  defaultAssignmentDays,
  resetAssignmentRuleData,
  resetAssignmentRuleErrors,
  validateAssignmentRule,
} from "../../../stores/assignmentRules";
import AssigneeRules from "./AssigneeRules.vue";
import AssignmentRulesSection from "./AssignmentRulesSection.vue";
import AssignmentSchedule from "./AssignmentSchedule.vue";
import { convertToConditions } from "@/utils";
import { disableSettingModalOutsideClick } from "../settingsModal";

const isDirty = ref(false);
const initialData = ref(null);
const isLoading = ref(false);

const showConfirmDialog = ref({
  show: false,
  title: "",
  message: "",
  onConfirm: () => {},
});
const useNewUI = ref(true);
const isOldSla = ref(false);
const deskUrl = `${window.location.origin}/app/assignment-rule/${assignmentRulesActiveScreen.value.data?.name}`;

const getAssignmentRuleData = createResource({
  url: "helpdesk.api.assignment_rule.get_assignment_rule_details",
  params: {
    name: assignmentRulesActiveScreen.value.data?.name,
  },
  auto: Boolean(assignmentRulesActiveScreen.value.data),
  onSuccess(data) {
    const assignmentDays =
      data.assignmentDays && data.assignmentDays.length
        ? data.assignmentDays
        : [...defaultAssignmentDays];

    assignmentRuleData.value = {
      loading: false,
      assignCondition: data.assign_condition,
      unassignCondition: data.unassign_condition,
      assignConditionJson: data.assignConditionJson || [],
      unassignConditionJson: data.unassignConditionJson || [],
      rule: data.rule,
      priority: data.priority,
      users: data.users || [],
      dynamicUserAssignments: data.dynamicUserAssignments || [],
      holidays: data.holidays || [],
      disabled: data.disabled,
      description: data.description,
      name: data.name,
      assignmentRuleName: data.assignment_rule_name || data.name,
      assignmentDays,
      custom_user_assignment: data.custom_user_assignment || null,
    };

    initialData.value = JSON.stringify(assignmentRuleData.value);

    const conditionsAvailable =
      assignmentRuleData.value.assignCondition?.length > 0;
    const conditionsJsonAvailable =
      assignmentRuleData.value.assignConditionJson?.length > 0;

    if (conditionsAvailable && !conditionsJsonAvailable) {
      useNewUI.value = false;
      isOldSla.value = true;
    } else {
      useNewUI.value = true;
      isOldSla.value = false;
    }
  },
});

if (!assignmentRulesActiveScreen.value.data) {
  disableSettingModalOutsideClick.value = true;
}

const goBack = () => {
  const confirmDialogInfo = {
    show: true,
    title: "Unsaved changes",
    message: "Are you sure you want to go back? Unsaved changes will be lost.",
    onConfirm: goBack,
  };
  if (isDirty.value && !showConfirmDialog.value.show) {
    showConfirmDialog.value = confirmDialogInfo;
    return;
  }
  if (
    !assignmentRulesActiveScreen.value.data &&
    !showConfirmDialog.value.show
  ) {
    showConfirmDialog.value = confirmDialogInfo;
    return;
  }
  // Workaround fix for settings modal not closing after going back
  setTimeout(() => {
    assignmentRulesActiveScreen.value = {
      screen: "list",
      data: null,
    };
  }, 250);
  showConfirmDialog.value.show = false;
};

const saveAssignmentRule = () => {
  const validationErrors = validateAssignmentRule(undefined, !useNewUI.value);

  if (Object.values(validationErrors).some((error) => error)) {
    toast.error(
      "Invalid fields, check if all are filled in and values are correct."
    );
    return;
  }

  if (assignmentRulesActiveScreen.value.data) {
    if (isOldSla.value && useNewUI.value) {
      showConfirmDialog.value = {
        show: true,
        title: "Confirm overwrite",
        message:
          "Your old condition will be overwritten. Are you sure you want to save?",
        onConfirm: () => {
          updateAssignmentRule();
          showConfirmDialog.value.show = false;
        },
      };
      return;
    }
    updateAssignmentRule();
  } else {
    createAssignmentRule();
  }
};

const buildAssignmentRulePayload = () => {
  const payload: Record<string, any> = {
    name: assignmentRuleData.value.name,
    assignmentRuleName: assignmentRuleData.value.assignmentRuleName,
    description: assignmentRuleData.value.description,
    disabled: assignmentRuleData.value.disabled,
    priority: assignmentRuleData.value.priority,
    rule: assignmentRuleData.value.rule,
    assignCondition: useNewUI.value
      ? convertToConditions({
          conditions: assignmentRuleData.value.assignConditionJson,
        })
      : assignmentRuleData.value.assignCondition,
    unassignCondition: useNewUI.value
      ? convertToConditions({
          conditions: assignmentRuleData.value.unassignConditionJson,
        })
      : assignmentRuleData.value.unassignCondition,
    assignmentDays: assignmentRuleData.value.assignmentDays,
    users:
      assignmentRuleData.value.users?.map((user) => ({
        user: user.user || user.email || user,
      })) || [],
    dynamicUserAssignments:
      assignmentRuleData.value.dynamicUserAssignments?.map((assignment) => ({
        name: assignment.name,
      })) || [],
    holidays:
      assignmentRuleData.value.holidays?.map((holiday) => ({
        name: holiday.name,
      })) || [],
    custom_user_assignment: assignmentRuleData.value.custom_user_assignment,
  };

  if (useNewUI.value) {
    payload.assignConditionJson = assignmentRuleData.value.assignConditionJson;
    payload.unassignConditionJson =
      assignmentRuleData.value.unassignConditionJson;
  }

  if (!payload.name) {
    delete payload.name;
  }

  return payload;
};

const createAssignmentRule = async () => {
  isLoading.value = true;
  try {
    const payload = buildAssignmentRulePayload();
    const response = await call(
      "helpdesk.api.assignment_rule.save_assignment_rule",
      { data: payload }
    );
    const newName = response?.name || payload.assignmentRuleName;
    assignmentRuleData.value.name = newName;
    assignmentRuleData.value.assignmentRuleName =
      assignmentRuleData.value.assignmentRuleName || newName;
    assignmentRulesActiveScreen.value = {
      screen: "view",
      data: { name: newName },
    };
    await getAssignmentRuleData.submit({ name: newName });
    toast.success("Assignment rule created");
  } catch (er) {
    const error =
      er?.messages?.[0] ||
      "Some error occurred while creating assignment rule";
    toast.error(error);
  } finally {
    isLoading.value = false;
  }
};

const priorityOptions = [
  { label: "Low", value: "0" },
  { label: "Low-Medium", value: "1" },
  { label: "Medium", value: "2" },
  { label: "Medium-High", value: "3" },
  { label: "High", value: "4" },
];

const updateAssignmentRule = async () => {
  isLoading.value = true;
  try {
    const payload = buildAssignmentRulePayload();
    const response = await call(
      "helpdesk.api.assignment_rule.save_assignment_rule",
      { data: payload }
    );
    const updatedName = response?.name || payload.name;
    assignmentRuleData.value.name = updatedName;
    assignmentRuleData.value.assignmentRuleName =
      assignmentRuleData.value.assignmentRuleName || updatedName;
    assignmentRulesActiveScreen.value = {
      screen: "view",
      data: { name: updatedName },
    };
    await getAssignmentRuleData.submit({ name: updatedName });
    toast.success("Assignment rule updated");
  } catch (er) {
    const error =
      er?.messages?.[0] ||
      "Some error occurred while updating assignment rule";
    toast.error(error);
  } finally {
    isLoading.value = false;
  }
};

watch(
  assignmentRuleData,
  (newVal) => {
    if (!initialData.value) return;
    isDirty.value = JSON.stringify(newVal) != initialData.value;
    if (isDirty.value) {
      disableSettingModalOutsideClick.value = true;
    } else {
      disableSettingModalOutsideClick.value = false;
    }
  },
  { deep: true }
);

const beforeUnloadHandler = (event) => {
  if (!isDirty.value) return;
  event.preventDefault();
  event.returnValue = true;
};

onMounted(() => {
  addEventListener("beforeunload", beforeUnloadHandler);
});

onUnmounted(() => {
  resetAssignmentRuleErrors();
  resetAssignmentRuleData();
  removeEventListener("beforeunload", beforeUnloadHandler);
  disableSettingModalOutsideClick.value = false;
});
</script>
