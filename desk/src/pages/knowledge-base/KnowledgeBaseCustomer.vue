<template>
  <div class="p-5 pb-10 px-10 w-full overflow-scroll items-center">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
    </LayoutHeader>
    <div
      class="max-w-4xl 2xl:max-w-5xl pt-4 sm:px-5 w-full flex flex-col gap-4"
    >
      <SearchPopover
        :popoverClass="[
          'max-w-[310px] md:max-w-[856px] !top-1 md:min-w-[856px]',
        ]"
        v-model="query"
        placeholder="Ask a question..."
        size="md"
        :autofocus="true"
      />

      <!-- Tab Switcher -->
      <div class="flex gap-4 border-b border-gray-200">
        <button
          class="pb-2 text-sm font-medium transition-colors"
          :class="activeTab === 'faq' ? 'text-gray-900 border-b-2 border-gray-900' : 'text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'faq'"
        >
          {{ __("FAQ") }}
        </button>
        <button
          class="pb-2 text-sm font-medium transition-colors"
          :class="activeTab === 'categories' ? 'text-gray-900 border-b-2 border-gray-900' : 'text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'categories'"
        >
          {{ __("Categories") }}
        </button>
      </div>

      <!-- FAQ Articles -->
      <section v-if="activeTab === 'faq'" class="flex flex-col gap-3">
        <div v-if="allArticles.loading" class="flex justify-center py-8">
          <Spinner class="h-5 w-5 text-gray-500" />
        </div>
        <div
          v-else-if="allArticles.data?.length"
          class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-5"
        >
          <ArticleCard
            v-for="article in allArticles.data"
            :article="article"
            :key="article.name"
          />
        </div>
        <div v-else class="text-sm text-gray-500 py-4">
          {{ __("No articles published yet.") }}
        </div>
      </section>

      <!-- Categories Folder -->
      <section v-if="activeTab === 'categories'" class="flex flex-col gap-3">
        <p class="text-lg text-gray-900">{{ __("Categories") }}</p>
        <CategoryFolderContainer />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { createResource, Breadcrumbs, Spinner, usePageMeta } from "frappe-ui";

import { LayoutHeader } from "@/components";
import CategoryFolderContainer from "@/components/knowledge-base/CategoryFolderContainer.vue";
import ArticleCard from "@/components/knowledge-base/ArticleCard.vue";
import SearchPopover from "@/components/SearchPopover.vue";
import { capture } from "@/telemetry";
import { __ } from "@/translation";

const query = ref("");
const activeTab = ref<"faq" | "categories">("faq");

const allArticles = createResource({
  url: "helpdesk.api.knowledge_base.get_all_published_articles",
  auto: true,
});

const breadcrumbs = computed(() => [
  {
    label: __("Get Started"),
    route: {
      name: "CustomerKnowledgeBase",
    },
  },
]);

onMounted(() => {
  capture("kb_customer_page_viewed");
});
usePageMeta(() => {
  return {
    title: __("Get Started"),
  };
});
</script>
