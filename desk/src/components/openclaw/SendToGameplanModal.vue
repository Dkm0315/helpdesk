<template>
  <Dialog
    v-model="isOpen"
    :options="{ size: '3xl', title: 'Send to Gameplan' }"
    @after-leave="reset"
  >
    <template #body-content>
      <div class="space-y-4">
        <!-- Header banner: shows source ticket -->
        <div class="rounded-lg border bg-surface-gray-1 px-3 py-2 text-sm">
          <span class="text-ink-gray-5">Source:</span>
          <span class="font-medium text-ink-gray-8">Helpdesk Ticket {{ ticketName }}</span>
          <span v-if="ticketSubject" class="text-ink-gray-6">— {{ ticketSubject }}</span>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="rounded-lg border bg-white p-4">
          <div class="flex items-center gap-3 text-sm text-ink-gray-6">
            <div class="flex gap-1">
              <span class="h-2 w-2 animate-bounce rounded-full bg-ink-gray-4" />
              <span class="h-2 w-2 animate-bounce rounded-full bg-ink-gray-4 [animation-delay:120ms]" />
              <span class="h-2 w-2 animate-bounce rounded-full bg-ink-gray-4 [animation-delay:240ms]" />
            </div>
            NextAI is drafting the handoff template from the ticket context...
          </div>
        </div>

        <!-- Error state -->
        <div
          v-if="error && !loading"
          class="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-ink-gray-7"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="font-medium">Could not draft the template</div>
              <div class="mt-1 text-ink-gray-6">{{ error }}</div>
              <div v-if="rawDraft" class="mt-2 text-xs text-ink-gray-5">
                Raw model output (first 300 chars):
                <pre class="mt-1 whitespace-pre-wrap rounded bg-white p-2 font-mono">{{ rawDraft.slice(0, 300) }}</pre>
              </div>
            </div>
            <Button label="Retry" variant="subtle" @click="loadDraft" />
          </div>
        </div>

        <!-- Form (only when template is loaded) -->
        <div v-if="template && !loading" class="space-y-3">
          <FormControl
            v-model="template.key_issue"
            label="Key Issue"
            type="text"
            placeholder="One short sentence stating the core problem"
          />

          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Acceptance Criteria (one per line)</label>
            <textarea
              v-model="acceptanceText"
              rows="4"
              class="block w-full resize-y rounded-md border border-outline-gray-2 px-3 py-2 text-sm"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <FormControl
              v-model="template.severity"
              label="Severity"
              type="select"
              :options="['Low', 'Medium', 'High', 'Critical']"
            />
            <FormControl
              v-model="template.suggested_assignee"
              label="Suggested Assignee (User)"
              type="text"
              placeholder="user@example.com"
            />
          </div>

          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Reproduction Steps (one per line)</label>
            <textarea
              v-model="reproText"
              rows="3"
              class="block w-full resize-y rounded-md border border-outline-gray-2 px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Workarounds (one per line)</label>
            <textarea
              v-model="workaroundsText"
              rows="2"
              class="block w-full resize-y rounded-md border border-outline-gray-2 px-3 py-2 text-sm"
            />
          </div>

          <FormControl
            v-model="template.affected_components_text"
            label="Affected Components (comma-separated)"
            type="text"
            placeholder="helpdesk, openclaw-gateway, etc."
          />

          <div class="grid grid-cols-2 gap-3">
            <FormControl
              v-model="project"
              label="Gameplan Project"
              type="autocomplete"
              :options="projectOptions"
              placeholder="Pick a project"
            />
            <FormControl
              v-model="sprint"
              label="Sprint (optional)"
              type="text"
              placeholder="Active sprint name if any"
            />
          </div>

          <!-- Coding agent toggle -->
          <div class="rounded-lg border border-violet-200 bg-violet-50 p-3 text-sm">
            <label class="flex items-start gap-2">
              <input v-model="triggerAgent" type="checkbox" class="mt-1" />
              <span>
                <span class="font-medium text-ink-gray-8">Also draft code &amp; raise a PR (beta)</span>
                <span class="mt-1 block text-xs text-ink-gray-6">
                  The Gameplan coding agent will investigate the codebase, plan the fix, and (Phase 2) open a PR.
                  Phase 1 stores a written plan on the handoff record you can review.
                </span>
              </span>
            </label>
          </div>
        </div>

        <!-- Progress after send -->
        <div v-if="afterSend" class="rounded-lg border bg-white p-3 text-sm">
          <div class="font-medium text-ink-gray-8">Handoff created</div>
          <div class="mt-1 text-ink-gray-6">
            Gameplan task:
            <a :href="`/g/space/1/tasks/${afterSend.gp_task}`" target="_blank" class="underline">{{ afterSend.gp_task }}</a>
          </div>
          <div v-if="afterSend.handoff" class="mt-1 text-ink-gray-6">
            Audit record:
            <a :href="`/app/openclaw-handoff/${afterSend.handoff}`" target="_blank" class="underline">{{ afterSend.handoff }}</a>
          </div>
          <div v-if="agentStatus" class="mt-2 rounded bg-violet-50 px-2 py-1 text-xs text-violet-700">
            Coding agent: <span class="font-medium">{{ agentStatus.agent_run_status }}</span>
            <span v-if="agentStatus.pr_url"> · <a :href="agentStatus.pr_url" target="_blank" class="underline">View PR</a></span>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex justify-end gap-2">
        <Button v-if="!afterSend" label="Cancel" variant="subtle" @click="isOpen = false" />
        <Button
          v-if="!afterSend"
          label="Regenerate"
          variant="subtle"
          :disabled="loading"
          @click="loadDraft"
        />
        <Button
          v-if="!afterSend"
          label="Send to Gameplan"
          variant="solid"
          theme="primary"
          :disabled="!canSend || sending"
          :loading="sending"
          @click="send"
        />
        <Button v-else label="Close" variant="solid" @click="isOpen = false" />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { Button, Dialog, FormControl, toast } from "frappe-ui";

interface HandoffTemplate {
  key_issue: string;
  acceptance_criteria: string[];
  severity: string;
  repro_steps: string[];
  workarounds: string[];
  suggested_assignee: string | null;
  suggested_project: string | null;
  suggested_sprint: string | null;
  affected_components?: string[];
  affected_components_text?: string;
}

const props = defineProps<{
  modelValue: boolean;
  ticketName: string;
  ticketSubject?: string;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  success: [payload: { gp_task: string; handoff: string }];
}>();

const isOpen = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

const loading = ref(false);
const sending = ref(false);
const error = ref("");
const rawDraft = ref("");
const template = ref<HandoffTemplate | null>(null);
const aiRun = ref<string | null>(null);

type ProjectOption = { label: string; value: string };

const project = ref<ProjectOption | string | null>(null);
const sprint = ref("");
const triggerAgent = ref(false);
const projectOptions = ref<ProjectOption[]>([]);

const afterSend = ref<{ gp_task: string; handoff: string } | null>(null);
const agentStatus = ref<any>(null);
let pollTimer: number | null = null;

const acceptanceText = ref("");
const reproText = ref("");
const workaroundsText = ref("");

watch(template, (t) => {
  if (!t) return;
  acceptanceText.value = (t.acceptance_criteria || []).join("\n");
  reproText.value = (t.repro_steps || []).join("\n");
  workaroundsText.value = (t.workarounds || []).join("\n");
  if (t.suggested_project && !project.value) {
    const match = projectOptions.value.find(
      (option) => option.value === t.suggested_project || option.label === t.suggested_project,
    );
    if (match) project.value = match;
  }
  if (t.suggested_sprint && !sprint.value) sprint.value = t.suggested_sprint;
  if (t.affected_components) t.affected_components_text = t.affected_components.join(", ");
});

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      reset();
      loadDraft();
      loadProjectOptions();
    }
  },
);

// The parent uses `v-if="showHandoffModal"` + `v-model:open="showHandoffModal"`
// so the modal mounts already in the open state. The watch above only fires on
// CHANGES (immediate: false by default), so the initial open won't trigger
// loadDraft.  Run on mount when already open.
onMounted(() => {
  if (props.modelValue) {
    reset();
    loadDraft();
    loadProjectOptions();
  }
});

const canSend = computed(
  () => !!template.value && !!template.value.key_issue && !!projectName.value && !sending.value,
);

const projectName = computed(() => {
  const value = project.value;
  if (!value) return "";
  if (typeof value === "string") return value;
  return value.value || "";
});

async function loadDraft() {
  loading.value = true;
  error.value = "";
  rawDraft.value = "";
  template.value = null;
  aiRun.value = null;
  try {
    const res = await fetch("/api/method/quant_customizations.api.openclaw_handoff.draft_handoff", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": (window as any).csrf_token || "",
      },
      credentials: "same-origin",
      body: JSON.stringify({ ticket_name: props.ticketName }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const msg = (data.message ?? data) as any;
    if (msg.error) {
      error.value = msg.error;
      rawDraft.value = msg.raw || "";
      return;
    }
    aiRun.value = msg.ai_run || null;
    template.value = msg.template as HandoffTemplate;
  } catch (e: any) {
    error.value = e?.message || "Network error";
  } finally {
    loading.value = false;
  }
}

async function loadProjectOptions() {
  try {
    const res = await fetch(
      "/api/method/quant_customizations.api.openclaw_handoff.list_gameplan_projects",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": (window as any).csrf_token || "",
        },
        credentials: "same-origin",
        body: JSON.stringify({ query: "" }),
      },
    );
    if (!res.ok) return;
    const data = await res.json();
    const rows = (data.message || []) as Array<{ name: string; title?: string }>;
    projectOptions.value = rows.map((r) => ({
      label: r.title ? `${r.title} (${r.name})` : String(r.name),
      value: String(r.name),
    }));
    if (!project.value && projectOptions.value.length === 1) {
      project.value = projectOptions.value[0];
    }
  } catch {
    /* non-fatal */
  }
}

async function send() {
  if (!template.value || !projectName.value) return;
  sending.value = true;
  try {
    const fullTemplate: HandoffTemplate = {
      ...template.value,
      acceptance_criteria: acceptanceText.value
        .split(/\r?\n/)
        .map((s) => s.trim())
        .filter(Boolean),
      repro_steps: reproText.value
        .split(/\r?\n/)
        .map((s) => s.trim())
        .filter(Boolean),
      workarounds: workaroundsText.value
        .split(/\r?\n/)
        .map((s) => s.trim())
        .filter(Boolean),
      affected_components: (template.value.affected_components_text || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    };
    const res = await fetch(
      "/api/method/quant_customizations.api.openclaw_handoff.send_to_gameplan",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": (window as any).csrf_token || "",
        },
        credentials: "same-origin",
        body: JSON.stringify({
          ticket_name: props.ticketName,
          project: projectName.value,
          sprint: sprint.value || null,
          template: fullTemplate,
          ai_run: aiRun.value,
          trigger_agent: triggerAgent.value ? 1 : 0,
        }),
      },
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const msg = (data.message ?? data) as { gp_task: string; handoff: string };
    afterSend.value = msg;
    toast.success(`Handed off to ${msg.gp_task}`);
    emit("success", msg);
    if (triggerAgent.value && msg.handoff) {
      startPollingAgentStatus(msg.handoff);
    }
  } catch (e: any) {
    toast.error(e?.message || "Send failed");
  } finally {
    sending.value = false;
  }
}

function startPollingAgentStatus(handoff: string) {
  if (pollTimer) {
    window.clearInterval(pollTimer);
  }
  let attempts = 0;
  pollTimer = window.setInterval(async () => {
    attempts += 1;
    if (attempts > 360) {
      // 30 min cap @ 5s
      window.clearInterval(pollTimer!);
      pollTimer = null;
      return;
    }
    try {
      const res = await fetch(
        "/api/method/quant_customizations.api.openclaw_handoff.get_handoff_status",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": (window as any).csrf_token || "",
          },
          credentials: "same-origin",
          body: JSON.stringify({ handoff_name: handoff }),
        },
      );
      if (!res.ok) return;
      const data = await res.json();
      agentStatus.value = data.message ?? data;
      if (["Opened PR", "Failed", "Cancelled"].includes(agentStatus.value?.agent_run_status)) {
        window.clearInterval(pollTimer!);
        pollTimer = null;
      }
    } catch {
      /* keep polling */
    }
  }, 5000) as unknown as number;
}

function reset() {
  loading.value = false;
  sending.value = false;
  error.value = "";
  rawDraft.value = "";
  template.value = null;
  aiRun.value = null;
  project.value = null;
  sprint.value = "";
  triggerAgent.value = false;
  afterSend.value = null;
  agentStatus.value = null;
  if (pollTimer) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
}
</script>
