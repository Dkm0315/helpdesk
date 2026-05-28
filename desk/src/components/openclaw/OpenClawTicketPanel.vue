<template>
  <NextAIPanel
    :open="modelValue"
    surface="helpdesk_ticket"
    reference-doctype="HD Ticket"
    :reference-name="ticketId"
    :initial-prompt="initialPrompt"
    :get-parent-editor="getParentEditor"
    :on-insert="handleInsertFallback"
    @update:open="(v) => emit('update:modelValue', v)"
    @inserted="onInserted"
  />
</template>

<script setup lang="ts">
import NextAIPanel from "./NextAIPanel.vue";

const props = defineProps<{
  modelValue: boolean;
  ticketId: string;
  initialPrompt?: string;
  /** Optional accessor to a parent (reply/comment) editor instance, passed down. */
  parentEditor?: any | null;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  "insert-reply": [content: string];
  "insert-comment": [content: string];
}>();

function getParentEditor() {
  return props.parentEditor || null;
}

function handleInsertFallback(text: string) {
  // Fallback path: if no parent editor available, ask the host (TicketAgent) to
  // route the text into the reply composer.
  emit("insert-reply", text);
}

function onInserted(_text: string) {
  /* parent already received text; keep panel open so the user can iterate */
}
</script>
