<template>
  <WikiPageList v-if="activeScreen.screen === 'list'" />
  <WikiPageView v-else-if="activeScreen.screen === 'view'" />
</template>

<script setup lang="ts">
import { createListResource } from "frappe-ui";
import { onUnmounted, provide, ref } from "vue";
import WikiPageList from "./WikiPageList.vue";
import WikiPageView from "./WikiPageView.vue";

const activeScreen = ref<{
  screen: "list" | "view";
  data: Record<string, any> | null;
}>({
  screen: "list",
  data: null,
});

const wikiListResource = createListResource({
  doctype: "Wiki Page",
  fields: ["name", "title", "route", "published"],
  cache: ["WikiPageSettingsList"],
  orderBy: "modified desc",
  start: 0,
  pageLength: 999,
  auto: true,
});

const searchQuery = ref("");

provide("wikiActiveScreen", activeScreen);
provide("wikiListResource", wikiListResource);
provide("wikiSearchQuery", searchQuery);

onUnmounted(() => {
  searchQuery.value = "";
  wikiListResource.filters = {};
});
</script>
