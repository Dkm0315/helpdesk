<template>
  <TechnologyList v-if="activeScreen.screen === 'list'" />
  <TechnologyView v-else-if="activeScreen.screen === 'view'" />
</template>

<script setup lang="ts">
import { createListResource } from "frappe-ui";
import { onUnmounted, provide, ref } from "vue";
import TechnologyList from "./TechnologyList.vue";
import TechnologyView from "./TechnologyView.vue";

const activeScreen = ref<{
  screen: "list" | "view";
  data: Record<string, any> | null;
}>({
  screen: "list",
  data: null,
});

const technologyListResource = createListResource({
  doctype: "HD Supported Technology",
  fields: [
    "name",
    "technology_name",
    "description",
    "icon_letter",
    "icon_color",
    "sort_order",
    "enabled",
  ],
  cache: ["TechnologyList"],
  orderBy: "sort_order asc, technology_name asc",
  start: 0,
  pageLength: 999,
  auto: true,
});

const searchQuery = ref("");

provide("techActiveScreen", activeScreen);
provide("techListResource", technologyListResource);
provide("techSearchQuery", searchQuery);

onUnmounted(() => {
  searchQuery.value = "";
  technologyListResource.filters = {};
});
</script>
