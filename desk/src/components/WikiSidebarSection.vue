<template>
  <div v-if="enableWiki && wikiPages.length">
    <!-- Documentation toggle -->
    <div
      class="-all flex h-7 cursor-pointer items-center rounded pl-2 pr-1 text-gray-800 duration-300 ease-in-out"
      :class="{
        'w-full': isExpanded,
        'w-8': !isExpanded,
        'hover:bg-gray-100': true,
      }"
      @click="isOpen = !isOpen"
    >
      <Tooltip :text="__('Documentation')" v-if="!isExpanded">
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
        {{ __("Documentation") }}
        <FeatherIcon
          name="chevron-right"
          class="h-3.5 text-gray-600 transition-all duration-300 ease-in-out"
          :class="{ 'rotate-90': isOpen }"
        />
      </div>
    </div>

    <!-- All wiki pages flat list -->
    <div
      v-show="isOpen && isExpanded"
      class="ml-3 border-l border-gray-200 pl-1"
    >
      <SidebarLink
        v-for="page in wikiPages"
        :key="page.name"
        :label="page.title"
        :to="getPageRoute(page.name)"
        :is-expanded="isExpanded"
        :is-active="isActivePage(page.name)"
        class="my-0.5"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import SidebarLink from "@/components/SidebarLink.vue";
import { useConfigStore } from "@/stores/config";
import { isCustomerPortal } from "@/utils";
import { __ } from "@/translation";
import { createResource } from "frappe-ui";
import { computed, ref } from "vue";
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

// Flatten all pages from all spaces and groups into one list
const wikiPages = computed(() => {
  if (!wikiData.data?.length) return [];
  const pages: { name: string; title: string }[] = [];
  for (const space of wikiData.data) {
    for (const groupPages of Object.values(space.groups) as any[]) {
      for (const page of groupPages) {
        pages.push(page);
      }
    }
  }
  return pages;
});

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
