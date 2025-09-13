<template>
  <div class="space-y-4">
    <div>
      <label class="block text-sm font-medium text-ink-gray-7 mb-1">
        {{ __("Category") }}
      </label>
      <FormControl
        type="select"
        v-model="selectedCategory"
        :options="categoryOptions"
        :placeholder="__('Select a category')"
        @change="onCategoryChange"
      />
    </div>

    <div v-if="selectedCategory">
      <label class="block text-sm font-medium text-ink-gray-7 mb-1">
        {{ __("Subcategory") }}
      </label>
      <FormControl
        type="select"
        v-model="selectedSubcategory"
        :options="subcategoryOptions"
        :placeholder="__('Select a subcategory')"
        :disabled="!selectedCategory"
        @change="onSubcategoryChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { FormControl } from 'frappe-ui';
import { createResource } from 'frappe-ui';

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ category: '', subcategory: '' })
  },
  categoryField: {
    type: String,
    default: 'category'
  },
  subcategoryField: {
    type: String,
    default: 'subcategory'
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

const selectedCategory = ref(props.modelValue.category || '');
const selectedSubcategory = ref(props.modelValue.subcategory || '');

// Resource for fetching categories
const categoriesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'HD Ticket Type',
    fields: ['name', 'parent_hd_ticket_type'],
    filters: [['parent_hd_ticket_type', '=', '']],
    order_by: 'name asc',
    limit: 0
  },
  auto: true,
  transform: (data) => {
    return data.map(item => ({
      label: item.name,
      value: item.name
    }));
  }
});

// Resource for fetching subcategories
const subcategoriesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'HD Ticket Type',
    fields: ['name'],
    filters: [['parent_hd_ticket_type', '=', selectedCategory.value]],
    order_by: 'name asc',
    limit: 0
  },
  auto: false,
  transform: (data) => {
    return data.map(item => ({
      label: item.name,
      value: item.name
    }));
  }
});

const categoryOptions = computed(() => {
  return categoriesResource.data || [];
});

const subcategoryOptions = computed(() => {
  if (!selectedCategory.value) return [];
  return subcategoriesResource.data || [];
});

const onCategoryChange = () => {
  // Reset subcategory when category changes
  selectedSubcategory.value = '';
  
  // Fetch subcategories for the selected category
  if (selectedCategory.value) {
    subcategoriesResource.update({
      params: {
        doctype: 'HD Ticket Type',
        fields: ['name'],
        filters: [['parent_hd_ticket_type', '=', selectedCategory.value]],
        order_by: 'name asc',
        limit: 0
      }
    });
    subcategoriesResource.fetch();
  }
  
  emitUpdate();
};

const onSubcategoryChange = () => {
  emitUpdate();
};

const emitUpdate = () => {
  const value = {
    [props.categoryField]: selectedCategory.value,
    [props.subcategoryField]: selectedSubcategory.value
  };
  emit('update:modelValue', value);
  emit('change', value);
};

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  if (newValue.category !== selectedCategory.value) {
    selectedCategory.value = newValue.category || '';
    if (selectedCategory.value) {
      onCategoryChange();
    }
  }
  if (newValue.subcategory !== selectedSubcategory.value) {
    selectedSubcategory.value = newValue.subcategory || '';
  }
}, { deep: true });

onMounted(() => {
  if (selectedCategory.value) {
    onCategoryChange();
  }
});
</script>