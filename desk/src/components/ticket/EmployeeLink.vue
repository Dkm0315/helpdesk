<template>
  <div class="space-y-1.5">
    <Autocomplete
      ref="autocomplete"
      :options="transformedOptions"
      v-model="value"
      size="sm"
      :filterable="true"
      :placeholder="placeholder"
      :disabled="options.loading"
    >
      <template #item-label="{ active, selected, option }">
        <div class="flex-1 truncate text-ink-gray-7">
          {{ option.label }}
        </div>
      </template>
    </Autocomplete>
  </div>
</template>

<script setup lang="ts">
import { Autocomplete, createResource, call } from "frappe-ui";
import { computed, ref, watch, onMounted, reactive } from "vue";
import { watchDebounced } from "@vueuse/core";

interface Props {
  modelValue?: string;
  placeholder?: string;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: "Select Employee",
});

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const autocomplete = ref<any>(null);
const text = ref("");

// Cache for employee names (reactive so Vue can track changes)
const employeeNameCache = reactive<Record<string, string>>({});

// Value computed property - must return object format to match options for Combobox comparison
// The Combobox comparison accesses .value, so we return an object even when empty to avoid errors
const value = computed({
  get: () => {
    const val = props.modelValue;
    if (!val) {
      // Return an object with empty value instead of null to avoid Combobox comparison errors
      // The Combobox's comparison function accesses .value, so null would cause errors
      return { value: "", label: "", description: "" };
    }
    // Find matching option in transformedOptions to ensure proper comparison
    const option = transformedOptions.value.find((opt: any) => opt.value === val);
    if (option) {
      return option;
    }
    // If option not found in current list, create a matching object structure
    // This ensures Combobox can compare it correctly
    return {
      value: val,
      label: employeeNameCache[val] || val,
      description: val,
    };
  },
  set: (val: any) => {
    // Handle null/undefined/empty values or objects with empty value
    if (!val || val === null || (typeof val === "object" && (!val.value || val.value === ""))) {
      emit("update:modelValue", "");
      return;
    }
    // Extract value from option object (Autocomplete passes object with value property)
    const newVal = val && typeof val === "object" && val.value !== undefined ? val.value : val;
    emit("update:modelValue", newVal || "");
  },
});

// Watch for query changes to reload options
watchDebounced(
  () => autocomplete.value?.query,
  (val) => {
    val = val || "";
    if (text.value === val) return;
    text.value = val;
    reload(val);
  },
  { debounce: 300, immediate: true }
);

const options = createResource({
  url: "frappe.desk.search.search_link",
  cache: ["Employee", text.value],
  method: "POST",
  params: {
    txt: text.value,
    doctype: "Employee",
    filters: {},
    page_length: 20,
  },
  auto: false,
});

const transformedOptions = computed(() => {
  if (!options.data || !Array.isArray(options.data)) {
    return [];
  }
  
  return options.data.map((option: any) => {
    const value = option?.value;
    let label = option?.label;
    
    // If label is missing or same as value (ID), use cached name
    if (!label || label === value) {
      if (employeeNameCache[value]) {
        label = employeeNameCache[value];
      } else {
        label = value; // Temporary fallback - will be updated when cache is populated
      }
    }
    
    return {
      value: value,
      label: label,
      description: option?.description || value,
    };
  });
});

// Watch for options data changes and batch fetch missing employee names
watch(
  () => options.data,
  (newData) => {
    if (!newData || !Array.isArray(newData)) return;
    
    const optionsToFetch: string[] = [];
    newData.forEach((option: any) => {
      const value = option?.value;
      const label = option?.label;
      
      // If label is missing or same as value, and not cached, mark for fetching
      if ((!label || label === value) && !employeeNameCache[value]) {
        if (!optionsToFetch.includes(value)) {
          optionsToFetch.push(value);
        }
      }
    });
    
    // Batch fetch employee names for options that need them
    if (optionsToFetch.length > 0) {
      batchFetchEmployeeNames(optionsToFetch);
    }
  },
  { immediate: true, deep: true }
);

async function fetchEmployeeName(employeeId: string) {
  if (!employeeId || employeeNameCache[employeeId]) return;
  
  try {
    const employeeRes = await call("frappe.client.get", {
      doctype: "Employee",
      name: employeeId,
    });
    
    if (employeeRes?.message) {
      const employee = employeeRes.message;
      // Use employee_name (full name) or first_name as fallback
      const employeeName = employee.employee_name || employee.first_name || employee.name;
      employeeNameCache[employeeId] = employeeName;
      // Update link title cache
      updateLinkTitle(employeeId, employeeName);
    }
  } catch (error) {
    console.warn("Error fetching employee name:", error);
  }
}

async function batchFetchEmployeeNames(employeeIds: string[]) {
  // Filter out already cached IDs
  const idsToFetch = employeeIds.filter(id => !employeeNameCache[id]);
  if (idsToFetch.length === 0) return;
  
  try {
    // Fetch all employees at once using get_list
    const employeesRes = await call("frappe.client.get_list", {
      doctype: "Employee",
      filters: {
        name: ["in", idsToFetch],
      },
      fields: ["name", "employee_name", "first_name"],
      limit_page_length: idsToFetch.length,
    });
    
    if (employeesRes?.message && Array.isArray(employeesRes.message)) {
      employeesRes.message.forEach((employee: any) => {
        const employeeName = employee.employee_name || employee.first_name || employee.name;
        employeeNameCache[employee.name] = employeeName;
        updateLinkTitle(employee.name, employeeName);
      });
      
      // Force reactivity update by updating the cache and triggering recomputation
      // The computed property will automatically update when employeeNameCache changes
    }
  } catch (error) {
    console.warn("Error batch fetching employee names:", error);
    // Fallback to individual fetches
    idsToFetch.forEach(id => fetchEmployeeName(id));
  }
}

function updateLinkTitle(employeeId: string, employeeName: string) {
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

function reload(val: string) {
  options.update({
    params: {
      txt: val,
      doctype: "Employee",
      filters: {},
      page_length: 20,
    },
  });
  options.reload();
}

// Ensure employee name is displayed for current value
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      fetchEmployeeName(newValue);
    }
  },
  { immediate: true }
);

// Load initial options when component mounts
onMounted(() => {
  reload("");
  if (props.modelValue) {
    fetchEmployeeName(props.modelValue);
  }
});
</script>

