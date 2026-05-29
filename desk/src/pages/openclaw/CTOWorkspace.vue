<template>
  <div class="min-h-full bg-surface-gray-1">
    <div class="border-b bg-white px-6 py-4">
      <div class="flex items-center justify-between gap-4">
        <div>
          <h1 class="text-xl font-semibold text-ink-gray-9">CTO Workspace</h1>
          <p class="mt-1 text-sm leading-6 text-ink-gray-5">
            Customer environments, support-hour risk, handoffs, and review-only air-gap command packs.
          </p>
        </div>
        <Button label="Refresh" @click="dashboard.reload()" />
      </div>
    </div>

    <div class="space-y-5 p-6">
      <ErrorMessage v-if="dashboard.error" :message="dashboard.error.messages?.[0] || dashboard.error.message" />
      <div v-if="dashboard.loading" class="rounded-2xl border bg-white p-6 text-sm text-ink-gray-5">Loading CTO context...</div>

      <div v-else class="grid gap-4 md:grid-cols-4">
        <div v-for="card in cards" :key="card.label" class="rounded-2xl border bg-white p-4 shadow-sm">
          <div class="text-sm text-ink-gray-5">{{ card.label }}</div>
          <div class="mt-2 text-3xl font-semibold text-ink-gray-9">{{ card.value }}</div>
        </div>
      </div>

      <div class="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <section class="rounded-2xl border bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <h2 class="font-semibold text-ink-gray-9">Customer Environments</h2>
            <Badge label="Sizing Profiles" theme="gray" />
          </div>
          <div class="overflow-hidden rounded-xl border">
            <table class="w-full text-left text-sm">
              <thead class="bg-surface-gray-2 text-ink-gray-5">
                <tr>
                  <th class="px-3 py-2">Customer</th>
                  <th class="px-3 py-2">Environment</th>
                  <th class="px-3 py-2">Engine</th>
                  <th class="px-3 py-2">Topology</th>
                  <th class="px-3 py-2">Nodes</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="env in dashboard.data?.environments || []" :key="env.name" class="border-t">
                  <td class="px-3 py-2 font-medium text-ink-gray-8">{{ env.customer }}</td>
                  <td class="px-3 py-2">{{ env.environment_label }}</td>
                  <td class="px-3 py-2">{{ env.engine || '-' }}</td>
                  <td class="px-3 py-2">{{ env.topology || '-' }}</td>
                  <td class="px-3 py-2">{{ env.nodes || '-' }}</td>
                </tr>
                <tr v-if="!(dashboard.data?.environments || []).length">
                  <td colspan="5" class="px-3 py-6 text-center text-ink-gray-5">No sizing profiles yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="rounded-2xl border bg-white p-4 shadow-sm">
          <h2 class="font-semibold text-ink-gray-9">Generate Review Commands</h2>
          <p class="mt-1 text-sm text-ink-gray-5">Commands are generated for review only. Nothing is executed.</p>
          <div class="mt-4 space-y-3">
            <FormControl
              v-model="commandForm.customer"
              type="autocomplete"
              label="Customer"
              :options="customerOptions"
              placeholder="Select customer"
            />
            <FormControl
              v-model="commandForm.environment"
              type="autocomplete"
              label="Environment"
              :options="environmentOptions"
              :disabled="!selectedCustomer"
              placeholder="Select environment"
            />
            <FormControl v-model="commandForm.task" label="Task" placeholder="install qdrant, collect diagnostics..." />
            <Button
              label="Generate Commands"
              theme="gray"
              :loading="commands.loading"
              :disabled="!selectedCustomer || !selectedEnvironment || !commandForm.task"
              @click="generateCommands"
            />
          </div>
          <pre v-if="commandOutput" class="mt-4 max-h-80 overflow-auto rounded-xl bg-surface-gray-2 p-3 text-xs text-ink-gray-8">{{ commandOutput }}</pre>
        </section>
      </div>

      <section class="rounded-2xl border bg-white p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="font-semibold text-ink-gray-9">Recent Dev Handoffs</h2>
          <Badge label="Human approval required" theme="orange" />
        </div>
        <div class="grid gap-3 md:grid-cols-2">
          <div v-for="handoff in dashboard.data?.recent_handoffs || []" :key="handoff.name" class="rounded-xl border p-3">
            <div class="font-medium text-ink-gray-9">{{ handoff.name }}</div>
            <div class="mt-1 text-sm text-ink-gray-5">Ticket {{ handoff.source_name }} → {{ handoff.target_name || 'pending' }}</div>
            <div class="mt-2 text-xs text-ink-gray-5">Agent: {{ handoff.agent_run_status || 'Not started' }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { Badge, Button, ErrorMessage, FormControl, createResource, usePageMeta } from 'frappe-ui'

type SelectOption = { label: string; value: string }

const commandForm = reactive<{ customer: string; environment: string; task: string }>({
  customer: '',
  environment: '',
  task: '',
})
const commandOutput = ref('')

const dashboard = createResource({
  url: 'quant_customizations.api.cto_workspace.get_cto_dashboard',
  auto: true,
})

const commandOptions = createResource({
  url: 'quant_customizations.api.cto_workspace.get_command_options',
  auto: true,
})

const commands = createResource({
  url: 'quant_customizations.api.airgap_commands.generate_commands',
  makeParams() {
    return {
      customer: selectedCustomer.value,
      env_label: selectedEnvironment.value,
      task: commandForm.task,
    }
  },
  onSuccess(data) {
    commandOutput.value = (data.commands || []).join('\n')
  },
})

const cards = computed(() => {
  const data = dashboard.data?.cards || {}
  return [
    { label: 'Customers', value: data.customers ?? 0 },
    { label: 'Expiring Licenses', value: data.expiring_licenses ?? 0 },
    { label: 'Active Handoffs', value: data.active_handoffs ?? 0 },
    { label: 'Low Hour Ledgers', value: data.low_balance_ledgers ?? 0 },
  ]
})

const selectedCustomer = computed(() => optionValue(commandForm.customer))
const selectedEnvironment = computed(() => optionValue(commandForm.environment))

const customerOptions = computed<SelectOption[]>(() => {
  return (commandOptions.data?.customers || []).map((customer: any) => ({
    label: customer.customer_name ? `${customer.customer_name} (${customer.name})` : String(customer.name),
    value: String(customer.name),
  }))
})

const environmentOptions = computed<SelectOption[]>(() => {
  const customer = selectedCustomer.value
  return (commandOptions.data?.environments || [])
    .filter((env: any) => !customer || env.customer === customer)
    .map((env: any) => ({
      label: [
        env.environment_label,
        env.engine ? `Engine: ${env.engine}` : '',
        env.topology ? `Topology: ${env.topology}` : '',
      ].filter(Boolean).join(' · '),
      value: String(env.name),
    }))
})

watch(
  () => selectedCustomer.value,
  () => {
    commandForm.environment = ''
    commandOutput.value = ''
  },
)

function optionValue(value: string): string {
  return value || ''
}

function generateCommands() {
  commandOutput.value = ''
  commands.submit()
}

usePageMeta(() => ({ title: 'CTO Workspace' }))
</script>
