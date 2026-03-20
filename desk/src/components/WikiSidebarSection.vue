<template>
  <div v-if="enableWiki && wikiData.data?.length">
    <div v-for="space in wikiData.data" :key="space.route">
      <div
        v-for="(pages, groupName) in space.groups"
        :key="groupName"
      >
        <!-- Group header (collapsible) -->
        <div
          class="-all flex h-7 cursor-pointer items-center rounded pl-2 pr-1 text-gray-800 duration-300 ease-in-out"
          :class="{
            'w-full': isExpanded,
            'w-8': !isExpanded,
            'hover:bg-gray-100': true,
          }"
          @click="toggleGroup(groupName)"
        >
          <Tooltip :text="groupName" v-if="!isExpanded">
            <span class="shrink-0 text-gray-700">
              <LucideBookOpen class="h-4 w-4" />
            </span>
          </Tooltip>
          <span v-else class="shrink-0 text-gray-700">
            <LucideBookOpen class="h-4 w-4" />
          </span>

          <div
            class="-all ml-2 flex shrink-0 grow items-center justify-between text-sm duration-300 ease-in-out"
            :class="{
              'opacity-100': isExpanded,
              'opacity-0': !isExpanded,
              '-z-50': !isExpanded,
            }"
          >
            {{ groupName }}
            <FeatherIcon
              name="chevron-right"
              class="h-3.5 text-gray-600 transition-all duration-300 ease-in-out"
              :class="{ 'rotate-90': openGroups.has(groupName) }"
            />
          </div>
        </div>

        <!-- Expandable page links -->
        <div
          v-show="openGroups.has(groupName) && isExpanded"
          class="ml-3 border-l border-gray-200 pl-1"
        >
          <SidebarLink
            v-for="page in pages"
            :key="page.name"
            :label="page.title"
            :to="getPageRoute(page.name)"
            :is-expanded="isExpanded"
            :is-active="isActivePage(page.name)"
            class="my-0.5"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SidebarLink from "@/components/SidebarLink.vue";
import { useConfigStore } from "@/stores/config";
import { isCustomerPortal } from "@/utils";
import { createResource } from "frappe-ui";
import { ref } from "vue";
import { useRoute } from "vue-router";
import LucideBookOpen from "~icons/lucide/book-open";

defineProps<{
  isExpanded: boolean;
}>();

const route = useRoute();
const { enableWiki } = useConfigStore();
const openGroups = ref<Set<string>>(new Set());

const wikiData = createResource({
  url: "helpdesk.api.wiki.get_wiki_sidebar_data",
  auto: true,
  cache: ["wikiSidebarData"],
});

function toggleGroup(groupName: string) {
  if (openGroups.value.has(groupName)) {
    openGroups.value.delete(groupName);
  } else {
    openGroups.value.add(groupName);
  }
}

function getPageRoute(pageName: string) {
  return {
    name: isCustomerPortal.value ? "WikiPageCustomer" : "WikiPageAgent",
    params: { pageId: pageName },
  };
}

function isActivePage(pageName: string) {
  return (
    route.params.pageId === pageName &&
    (route.name === "WikiPageAgent" || route.name === "WikiPageCustomer")
  );
}
</script>
