<template>
  <div class="h-full min-h-0 bg-surface-gray-1 p-3 sm:p-4">
    <NextAIPanel
      :open="true"
      layout="workspace"
      context-label="Helpdesk"
      surface="helpdesk_workspace"
      reference-doctype="User"
      :reference-name="currentUser"
      :get-parent-editor="() => null"
      @update:open="onClose"
    />
  </div>
</template>

<script setup lang="ts">
import { usePageMeta } from 'frappe-ui'
import NextAIPanel from '@/components/openclaw/NextAIPanel.vue'

const currentUser = (window as any).frappe?.session?.user || 'Administrator'

function onClose() {
  // The standalone workspace remains open by design.
}

usePageMeta(() => ({ title: 'Muster' }))
</script>
