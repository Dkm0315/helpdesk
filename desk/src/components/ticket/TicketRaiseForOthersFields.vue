<template>
  <div class="flex flex-col gap-3 border-b px-6 py-3">
    <div class="flex flex-col gap-2">
      <span class="block text-sm font-medium text-gray-700">Raised For</span>
      <FormControl
        v-model="raisedFor"
        type="select"
        :options="raisedForOptions"
        size="sm"
        @change="handleRaisedForChange"
      />
    </div>
    <div v-if="raisedFor === 'Others'" class="flex flex-col gap-2">
      <span class="block text-sm font-medium text-gray-700">Employee</span>
          <EmployeeLink
            :model-value="ticket.custom_raise_for_employee"
            @update:model-value="handleEmployeeChange"
          />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Ticket } from "@/types";
import { FormControl } from "frappe-ui";
import { computed, ref, watch } from "vue";
import { call } from "frappe-ui";
import EmployeeLink from "./EmployeeLink.vue";

interface Props {
  ticket: Ticket;
}

const props = defineProps<Props>();
const emit = defineEmits(["update"]);

const raisedForOptions = [
  { label: "Myself", value: "Myself" },
  { label: "Others", value: "Others" },
];

const raisedFor = computed({
  get: () => {
    if (props.ticket.custom_for_others) return "Others";
    if (props.ticket.custom_for_myself) return "Myself";
    return props.ticket.custom_raised_for || "Myself";
  },
  set: (val) => {
    // This will be handled by handleRaisedForChange
  },
});

async function ensureEmployeeNameDisplay(employeeId: string) {
  if (!employeeId) return;
  
  try {
    const employeeRes = await call("frappe.client.get", {
      doctype: "Employee",
      name: employeeId,
    });
    
    if (employeeRes?.message) {
      const employee = employeeRes.message;
      const employeeName = employee.employee_name || employee.name;
      
      const frappeWindow = window as any;
      if (frappeWindow.frappe?.utils?.add_link_title) {
        frappeWindow.frappe.utils.add_link_title("Employee", employeeId, employeeName);
      } else if (frappeWindow.frappe?.link_title_cache) {
        if (!frappeWindow.frappe.link_title_cache["Employee"]) {
          frappeWindow.frappe.link_title_cache["Employee"] = {};
        }
        frappeWindow.frappe.link_title_cache["Employee"][employeeId] = employeeName;
      }
    }
  } catch (error) {
    console.warn("Error loading employee name:", error);
  }
}

function handleRaisedForChange(value: string) {
  const updates: any = {
    custom_raised_for: value,
    custom_for_myself: value === "Myself" ? 1 : 0,
    custom_for_others: value === "Others" ? 1 : 0,
  };
  
  if (value === "Myself") {
    updates.custom_raise_for_employee = "";
  }
  
  emit("update", { field: "custom_raised_for", value });
  emit("update", { field: "custom_for_myself", value: updates.custom_for_myself });
  emit("update", { field: "custom_for_others", value: updates.custom_for_others });
  
  if (value === "Myself") {
    emit("update", { field: "custom_raise_for_employee", value: "" });
  }
}

async function handleEmployeeChange(value: string) {
  emit("update", { field: "custom_raise_for_employee", value });
  if (value) {
    await ensureEmployeeNameDisplay(value);
  }
}

// Ensure employee name is displayed on load
watch(
  () => props.ticket.custom_raise_for_employee,
  (newValue) => {
    if (newValue) {
      ensureEmployeeNameDisplay(newValue);
    }
  },
  { immediate: true }
);
</script>

<style scoped>
:deep(.form-control input:not([type="checkbox"])),
:deep(.form-control select),
:deep(.form-control button) {
  border-color: transparent;
  background: white;
}
</style>

