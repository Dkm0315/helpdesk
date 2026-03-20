<template>
  <div class="flex flex-col">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
    </LayoutHeader>

    <div v-if="pageContent.loading" class="flex justify-center py-20">
      <Spinner class="h-5 w-5 text-gray-500" />
    </div>

    <div
      v-else-if="pageContent.data"
      class="py-4 mx-auto w-full max-w-3xl px-5 flex flex-col"
    >
      <h1
        class="text-3xl font-bold pb-3 border-b border-gray-200"
      >
        {{ pageContent.data.page_title }}
      </h1>
      <div
        ref="wikiContentRef"
        class="wiki-content prose prose-sm max-w-none mt-4"
        v-html="pageContent.data.content"
        @click="handleContentClick"
      />
    </div>

    <div
      v-else
      class="flex flex-col items-center justify-center py-20 text-gray-500"
    >
      <p>{{ __("Wiki page not found") }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import LayoutHeader from "@/components/LayoutHeader.vue";
import { __ } from "@/translation";
import { isCustomerPortal } from "@/utils";
import { Breadcrumbs, call, createResource, Spinner, usePageMeta } from "frappe-ui";
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";

const props = defineProps<{
  pageId: string;
}>();

const router = useRouter();
const wikiContentRef = ref<HTMLElement | null>(null);

async function handleContentClick(e: MouseEvent) {
  const target = (e.target as HTMLElement).closest("a");
  if (!target) return;

  const href = target.getAttribute("href");
  if (!href) return;

  // Only intercept same-origin links (relative or absolute to same host)
  let pathname: string;
  try {
    const url = new URL(href, window.location.origin);
    if (url.origin !== window.location.origin) return; // external link, let it go
    pathname = url.pathname;
  } catch {
    pathname = href;
  }

  // Strip leading slash for route lookup
  const route = pathname.replace(/^\//, "");
  if (!route) return;

  // Skip links that are already helpdesk internal routes
  if (route.startsWith("helpdesk/")) return;

  // Try to resolve this as a wiki page
  e.preventDefault();
  try {
    const pageName = await call("helpdesk.api.wiki.resolve_wiki_route", { route });
    if (pageName) {
      const routeName = isCustomerPortal.value ? "WikiPageCustomer" : "WikiPageAgent";
      router.push({ name: routeName, params: { pageId: pageName } });
    } else {
      // Not a wiki page, navigate normally
      window.location.href = href;
    }
  } catch {
    window.location.href = href;
  }
}

const pageContent = createResource({
  url: "helpdesk.api.wiki.get_wiki_page_content",
  params: { wiki_page_name: props.pageId },
  auto: true,
});

watch(
  () => props.pageId,
  (newId) => {
    pageContent.update({ params: { wiki_page_name: newId } });
    pageContent.reload();
  }
);

const breadcrumbs = computed(() => {
  const items = [{ label: __("Documentation"), route: { name: "TicketsAgent" } }];
  if (pageContent.data?.page_title) {
    items.push({
      label: pageContent.data.page_title,
      route: {},
    });
  }
  return items;
});

usePageMeta(() => ({
  title: pageContent.data?.page_title || __("Documentation"),
}));
</script>

<style>
.wiki-content h1 {
  @apply text-2xl font-bold mt-6 mb-3;
}
.wiki-content h2 {
  @apply text-xl font-semibold mt-5 mb-2;
}
.wiki-content h3 {
  @apply text-lg font-semibold mt-4 mb-2;
}
.wiki-content p {
  @apply my-2 leading-relaxed;
}
.wiki-content ul {
  @apply list-disc pl-6 my-2;
}
.wiki-content ol {
  @apply list-decimal pl-6 my-2;
}
.wiki-content li {
  @apply my-1;
}
.wiki-content code {
  @apply bg-gray-100 text-gray-800 rounded px-1 py-0.5 text-sm;
}
.wiki-content pre {
  @apply bg-gray-100 text-gray-800 rounded p-3 overflow-x-auto my-3;
}
.wiki-content pre code {
  @apply bg-transparent p-0;
}
.wiki-content blockquote {
  @apply border-l-4 border-gray-300 pl-4 my-3 text-gray-600;
}
.wiki-content a {
  @apply text-blue-600 hover:underline;
}
.wiki-content table {
  @apply border-collapse w-full my-3;
}
.wiki-content th,
.wiki-content td {
  @apply border border-gray-300 px-3 py-2 text-left;
}
.wiki-content th {
  @apply bg-gray-50 font-semibold;
}
.wiki-content img {
  @apply max-w-full rounded my-3;
}
</style>
