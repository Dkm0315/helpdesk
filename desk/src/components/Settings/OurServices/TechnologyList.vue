<template>
  <SettingsLayoutBase>
    <template #title>
      <h1 class="text-lg font-semibold text-ink-gray-8">
        {{ __("Our Services") }}
      </h1>
    </template>
    <template #description>
      <p class="text-p-sm max-w-md text-ink-gray-6">
        {{
          __(
            "Manage the technologies and services displayed on the Our Services page."
          )
        }}
      </p>
    </template>
    <template #header-actions>
      <Button
        :label="__('New')"
        theme="gray"
        variant="solid"
        @click="goToNew()"
        icon-left="plus"
      />
    </template>
    <template
      v-if="techList.data?.length > 9 || searchQuery.length"
      #header-bottom
    >
      <div class="relative">
        <Input
          :model-value="searchQuery"
          @input="searchQuery = $event"
          :placeholder="__('Search')"
          type="text"
          class="bg-white hover:bg-white focus:ring-0 border-outline-gray-2"
          icon-left="search"
          debounce="300"
          inputClass="p-4 pr-12"
        />
        <Button
          v-if="searchQuery"
          icon="x"
          variant="ghost"
          @click="searchQuery = ''"
          class="absolute right-1 top-1/2 -translate-y-1/2"
        />
      </div>
    </template>
    <template #content>
      <div
        v-if="techList.list.loading && !techList.list.data"
        class="flex items-center justify-center mt-12"
      >
        <LoadingIndicator class="w-4" />
      </div>
      <div v-else class="grow">
        <div
          v-if="!techList.list.loading && !techList.list.data?.length"
          class="flex flex-col items-center justify-center gap-4 h-full"
        >
          <div
            class="p-4 size-14.5 rounded-full bg-surface-gray-1 flex justify-center items-center"
          >
            <LucideBriefcase class="size-6 text-ink-gray-6" />
          </div>
          <div class="flex flex-col items-center gap-1">
            <div class="text-base font-medium text-ink-gray-6">
              {{ __("No technologies found") }}
            </div>
            <div class="text-p-sm text-ink-gray-5 max-w-60 text-center">
              {{ __("Add one to get started.") }}
            </div>
          </div>
          <Button
            :label="__('New')"
            variant="outline"
            icon-left="plus"
            @click="goToNew()"
          />
        </div>
        <div v-else class="-ml-2">
          <div
            class="grid grid-cols-6 items-center gap-3 text-sm text-gray-600 ml-2"
          >
            <div class="col-span-3">{{ __("Technology") }}</div>
            <div class="col-span-1">{{ __("Order") }}</div>
            <div class="col-span-1">{{ __("Enabled") }}</div>
            <div class="col-span-1"></div>
          </div>
          <hr class="mt-2 mx-2" />
          <div
            v-for="(tech, index) in techList.list.data"
            :key="tech.name"
          >
            <TechnologyListItem :data="tech" />
            <hr
              v-if="index !== techList.list.data.length - 1"
              class="mx-2"
            />
          </div>
        </div>
      </div>
    </template>
  </SettingsLayoutBase>
</template>

<script setup lang="ts">
import { Button, Input, LoadingIndicator } from "frappe-ui";
import TechnologyListItem from "./TechnologyListItem.vue";
import { inject, Ref, watch } from "vue";
import SettingsLayoutBase from "@/components/layouts/SettingsLayoutBase.vue";
import { __ } from "@/translation";
import LucideBriefcase from "~icons/lucide/briefcase";

const techList = inject<any>("techListResource");
const activeScreen = inject<any>("techActiveScreen");
const searchQuery = inject<Ref<string>>("techSearchQuery");

const goToNew = () => {
  activeScreen.value = {
    screen: "view",
    data: null,
  };
};

watch(searchQuery, (newValue) => {
  techList.filters = {
    technology_name: ["like", `%${newValue}%`],
  };
  if (!newValue) {
    techList.start = 0;
    techList.pageLength = 999;
  }
  techList.reload();
});
</script>
