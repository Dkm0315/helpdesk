<template>
  <div class="pb-8">
    <Holidays v-if="holidayListActiveScreen.screen == 'list'" />
    <SimpleHolidayView v-else-if="holidayListActiveScreen.screen == 'view'" />
  </div>
</template>

<script setup lang="ts">
import { holidayListActiveScreen } from "@/stores/holidayList";
import Holidays from "./Holidays.vue";
import SimpleHolidayView from "./SimpleHolidayView.vue";
import { createListResource } from "frappe-ui";
import { provide } from "vue";

const holidayListData = createListResource({
  doctype: "Holidays",
  fields: ["name", "holiday_name", "date", "type", "official_location", "repeat_next_year"],
  orderBy: "date desc",
  start: 0,
  pageLength: 999,
  auto: true,
});

provide("holidayList", holidayListData);
</script>
