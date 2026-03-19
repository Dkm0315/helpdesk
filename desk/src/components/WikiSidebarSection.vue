<template>
  <div v-if="enableWiki && wikiData.data?.length">
    <!-- Top-level Wiki toggle -->
    <div
      class="-all flex h-7 cursor-pointer items-center rounded pl-2 pr-1 text-gray-800 duration-300 ease-in-out"
      :class="{
        'w-full': isExpanded,
        'w-8': !isExpanded,
        'hover:bg-gray-100': true,
      }"
      @click="handleClick"
    >
      <Tooltip :text="__('Wiki')" v-if="!isExpanded">
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
        {{ __("Wiki") }}
        <FeatherIcon
          name="chevron-right"
          class="h-3.5 text-gray-600 transition-all duration-300 ease-in-out"
          :class="{ 'rotate-90': isOpen }"
        />
      </div>
    </div>

    <!-- Expandable wiki pages -->
    <div
      v-show="isOpen && isExpanded"
      class="ml-3 border-l border-gray-200 pl-1"
    >
      <div v-for="space in wikiData.data" :key="space.route">
        <div
          v-for="(pages, groupName) in space.groups"
          :key="groupName"
        >
          <div
            class="px-2 py-1 text-xs font-medium text-gray-500 uppercase tracking-wide truncate"
          >
            {{ groupName }}
          </div>
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
import { __ } from "@/translation";
import { createResource } from "frappe-ui";
import { ref } from "vue";
import { useRoute } from "vue-router";
import LucideBookOpen from "~icons/lucide/book-open";

defineProps<{
  isExpanded: boolean;
}>();

const route = useRoute();
const { enableWiki } = useConfigStore();
const isOpen = ref(false);

const wikiData = createResource({
  url: "helpdesk.api.wiki.get_wiki_sidebar_data",
  auto: true,
  cache: ["wikiSidebarData"],
});

function handleClick() {
  isOpen.value = !isOpen.value;
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
