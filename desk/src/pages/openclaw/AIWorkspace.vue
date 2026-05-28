<template>
  <div class="flex h-full flex-col bg-surface-gray-1">
    <div class="border-b bg-white px-6 py-4">
      <div class="flex items-center justify-between gap-4">
        <div>
          <h1 class="text-xl font-semibold text-ink-gray-9">NextAI</h1>
          <p class="mt-1 text-sm leading-6 text-ink-gray-5">
            A free OpenClaw workspace for support, artifacts, architecture, implementation planning, and follow-up questions.
          </p>
        </div>
        <Badge label="OpenClaw runtime" theme="gray" />
      </div>
    </div>

    <div class="flex flex-1 items-center justify-center p-6">
      <div class="max-w-2xl rounded-3xl border bg-white p-6 text-center shadow-sm">
        <div class="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-surface-gray-2">
          <Sparkles class="h-5 w-5 text-ink-gray-8" />
        </div>
        <h2 class="text-base font-semibold text-ink-gray-9">Use the same NextAI composer everywhere</h2>
        <p class="mt-2 text-sm leading-6 text-ink-gray-5">
          Type <strong>/</strong> for commands, <strong>@</strong> for agents, attach files, steer or stop runs, and continue the thread without leaving Helpdesk.
        </p>
      </div>
    </div>

    <NextAIPanel
      :open="true"
      surface="helpdesk_workspace"
      reference-doctype="User"
      :reference-name="currentUser"
      :get-parent-editor="() => null"
      :on-insert="onInsertWorkspace"
      @update:open="onClose"
    />

    <div v-if="lastInsertedText" class="fixed bottom-5 left-1/2 z-50 max-w-xl -translate-x-1/2 rounded-xl border bg-white px-4 py-3 text-sm shadow-lg">
      <div class="font-medium text-ink-gray-8">Last inserted result</div>
      <div class="mt-1 line-clamp-3 whitespace-pre-wrap text-ink-gray-6">{{ lastInsertedText }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Badge, usePageMeta } from 'frappe-ui'
import Sparkles from '~icons/lucide/sparkles'
import NextAIPanel from '@/components/openclaw/NextAIPanel.vue'

const currentUser = (window as any).frappe?.session?.user || 'Administrator'
const lastInsertedText = ref('')

function onInsertWorkspace(text: string) {
  lastInsertedText.value = text
}

function onClose() {
  // Standalone workspace keeps the primary AI composer open.
}

usePageMeta(() => ({ title: 'NextAI' }))
</script>
