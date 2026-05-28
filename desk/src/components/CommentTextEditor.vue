<template>
  <TextEditor
    v-if="agentsList.data"
    ref="editorRef"
    :editor-class="[
      'prose-sm max-w-none',
      editable &&
        'min-h-[7rem] mx-6 md:ml-10 md:mr-9 max-h-[50vh] overflow-y-auto border-t py-3',
      getFontFamily(newComment),
    ]"
    :content="newComment"
    :starterkit-options="{ heading: { levels: [2, 3, 4, 5, 6] } }"
    :placeholder="placeholder"
    :editable="editable"
    :mentions="dropdown"
    @change="editable ? (newComment = $event) : null"
    :extensions="ghostExtensions"
    :uploadFunction="(file:any)=>uploadFunction(file, doctype, ticketId)"
  >
    <template #bottom>
      <div v-if="editable" class="flex flex-col gap-2 px-6 md:pl-10 md:pr-9">
        <!-- Attachments -->
        <div class="flex flex-wrap gap-2">
          <AttachmentItem
            v-for="a in attachments"
            :key="a.file_url"
            :label="a.file_name"
            :url="!['MOV', 'MP4'].includes(a.file_type) ? a.file_url : null"
          >
            <template #suffix>
              <FeatherIcon
                class="h-3.5"
                name="x"
                @click.stop="removeAttachment(a)"
              />
            </template>
          </AttachmentItem>
        </div>
        <!-- NextAI inline ghost status (FIX D, 2026-05-26).
             Same chip as EmailEditor: keeps the user informed that the
             current grey-italic continuation is keyboard-actionable. -->
        <div v-show="ghostLoading || ghostVisible" class="flex">
          <span class="inline-flex items-center gap-1 rounded-md border bg-surface-gray-1 px-2 py-1 text-xs text-ink-gray-5">
            <Sparkles
              class="h-3 w-3"
              :class="ghostLoading ? 'animate-pulse' : ''"
            />
            <template v-if="ghostLoading">NextAI is drafting...</template>
            <template v-else>
              <kbd class="rounded border bg-white px-1 py-0.5 text-[10px] text-ink-gray-7">Tab</kbd>
              to accept ·
              <kbd class="rounded border bg-white px-1 py-0.5 text-[10px] text-ink-gray-7">Esc</kbd>
              to dismiss
            </template>
          </span>
        </div>
        <!-- Fixed Menu -->
        <div class="flex justify-between overflow-hidden border-t py-2.5">
          <div class="flex items-center overflow-x-auto w-[60%]">
            <FileUploader
              :upload-args="{
                doctype: doctype,
                docname: ticketId,
                private: true,
              }"
              @success="(f) => attachments.push(f)"
            >
              <template #default="{ openFileSelector, uploading }">
                {{ void (loading = uploading) }}
                <Button
                  theme="gray"
                  variant="ghost"
                  @click="openFileSelector()"
                >
                  <template #icon>
                    <AttachmentIcon
                      class="h-4"
                      style="color: #000000; stroke-width: 1.5 !important"
                    />
                  </template>
                </Button>
              </template>
            </FileUploader>
            <TextEditorFixedMenu
              class="-ml-0.5"
              :buttons="textEditorMenuButtons"
            />
            <Button
              theme="gray"
              variant="subtle"
              class="ml-1 shrink-0"
              :loading="ghostLoading"
              @click="emit('request-ai')"
            >
              <template #icon>
                <Sparkles class="h-4 w-4" />
              </template>
              Draft with NextAI
            </Button>
          </div>
          <div class="flex items-center justify-end space-x-2 w-[40%]">
            <Button
              label="Discard"
              @click="
                () => {
                  newComment = '';
                  attachments = [];
                  emit('discard');
                }
              "
            />
            <Button
              variant="solid"
              :label="label"
              :disabled="isDisabled"
              :loading="loading"
              @click="
                () => {
                  loading = true;
                  submitComment();
                  newComment = '';
                }
              "
            />
          </div>
        </div>
      </div>
    </template>
  </TextEditor>
</template>
<script setup lang="ts">
import {
  FileUploader,
  TextEditor,
  TextEditorFixedMenu,
  createResource,
} from "frappe-ui";
import { useOnboarding } from "frappe-ui/frappe";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { AttachmentItem } from "@/components/";
import { AttachmentIcon } from "@/components/icons/";
import { useTyping } from "@/composables/realtime";
import { useAgentStore } from "@/stores/agent";
import { useAuthStore } from "@/stores/auth";
import { PreserveVideoControls } from "@/tiptap-extensions";
import {
  getFontFamily,
  isContentEmpty,
  removeAttachmentFromServer,
  textEditorMenuButtons,
  uploadFunction,
} from "@/utils";
import { useStorage } from "@vueuse/core";
import { storeToRefs } from "pinia";
import Sparkles from "~icons/lucide/sparkles";
import {
  InlineGhostSuggestion,
  InlineGhostKey,
} from "@/components/openclaw/InlineGhostSuggestion";

const { updateOnboardingStep } = useOnboarding("helpdesk");
const { agents: agentsList, dropdown } = storeToRefs(useAgentStore());
const { isManager } = useAuthStore();

const props = defineProps({
  ticketId: {
    type: String,
    default: null,
  },
  placeholder: {
    type: String,
    default: null,
  },
  label: {
    type: String,
    default: "Comment",
  },
  editable: {
    type: Boolean,
    default: true,
  },
  doctype: {
    type: String,
    default: "HD Ticket",
  },
});

const emit = defineEmits(["submit", "discard", "request-ai"]);

const newComment = useStorage("commentBoxContent" + props.ticketId, null);

// Initialize typing composable
const { onUserType, cleanup } = useTyping(props.ticketId);

const attachments = ref([]);
const isDisabled = computed(() => {
  return isContentEmpty(newComment.value) || loading.value;
});
const loading = ref(false);

// Watch for changes in comment content to trigger typing events
watch(newComment, (newValue, oldValue) => {
  if (newValue !== oldValue && newValue) {
    onUserType();
  }
});

onBeforeUnmount(() => {
  cleanup();
});

const label = computed(() => {
  return loading.value ? "Sending..." : props.label;
});

function removeAttachment(attachment) {
  attachments.value = attachments.value.filter((a) => a !== attachment);
  removeAttachmentFromServer(attachment.name);
}

function insertDraft(template: string) {
  if (!template) return;

  newComment.value = isContentEmpty(newComment.value)
    ? template
    : `${newComment.value}\n\n${template}`;
}

async function submitComment() {
  if (isContentEmpty(newComment.value)) {
    return false;
  }
  const comment = createResource({
    url: "run_doc_method",
    makeParams: () => ({
      dt: props.doctype,
      dn: props.ticketId,
      method: "new_comment",
      args: {
        content: newComment.value,
        attachments: attachments.value,
      },
    }),
    onSuccess: () => {
      if (isManager) {
        updateOnboardingStep("comment_on_ticket");
      }
      emit("submit");
      loading.value = false;
      attachments.value = [];
      newComment.value = null;
    },
    onError: () => {
      loading.value = false;
    },
  });

  comment.submit();
}

const editorRef = ref(null);
const editor = computed(() => editorRef.value?.editor);

// --- Inline ghost-text completion (Gmail Smart Compose style) ----------
const ghostSessionKey = ref<string | null>(null);

async function fetchInlineCompletion(prefix: string): Promise<string> {
  if (!props.ticketId) return "";
  try {
    const res = await fetch(
      "/api/method/quant_customizations.api.openclaw_ai.suggest_inline_completion",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": (window as any).csrf_token || "",
        },
        credentials: "same-origin",
        body: JSON.stringify({
          prefix,
          source_doctype: props.doctype || "HD Ticket",
          source_name: props.ticketId,
          session_key: ghostSessionKey.value || undefined,
        }),
      }
    );
    if (!res.ok) return "";
    const data = await res.json();
    const message = data.message || data;
    if (message?.session_key) ghostSessionKey.value = message.session_key;
    return message?.completion || "";
  } catch {
    return "";
  }
}

const ghostExtensions = computed(() => [
  PreserveVideoControls,
  InlineGhostSuggestion.configure({
    fetchCompletion: fetchInlineCompletion,
    debounceMs: 500,
    minPrefixChars: 12,
    maxPrefixChars: 4000,
    enabled: () => true,
  }),
]);

const ghostLoading = ref(false);
// FIX D (2026-05-26): expose whether an inline ghost is currently rendered.
// Drives the "Tab to accept · Esc to dismiss" hint so users know the
// suggestion is keyboard-actionable.
const ghostVisible = ref(false);
let ghostTxnUnsubscribe: (() => void) | null = null;

function bindGhostLoadingSubscription(ed: any) {
  if (!ed) return;
  const handler = () => {
    const ps = InlineGhostKey.getState(ed.state);
    ghostLoading.value = !!ps?.loading;
    ghostVisible.value = !!(ps?.ghost && ps?.anchorPos != null);
  };
  ed.on("transaction", handler);
  ghostTxnUnsubscribe = () => {
    try {
      ed.off("transaction", handler);
    } catch {
      // ignore
    }
  };
}

function triggerInlineGhost(prefixOverride?: string) {
  const ed = editorRef.value?.editor;
  if (!ed) return;
  (ed.commands as any).triggerInlineGhost?.(prefixOverride);
}

watch(
  () => editorRef.value?.editor,
  (ed) => {
    if (ghostTxnUnsubscribe) {
      ghostTxnUnsubscribe();
      ghostTxnUnsubscribe = null;
    }
    if (ed) bindGhostLoadingSubscription(ed);
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  if (ghostTxnUnsubscribe) {
    ghostTxnUnsubscribe();
    ghostTxnUnsubscribe = null;
  }
});

onMounted(() => {
  if (
    agentsList.value.loading ||
    agentsList.value.data?.length ||
    agentsList.value.list.promise
  ) {
    return;
  }
  agentsList.value.fetch();
});

defineExpose({
  submitComment,
  insertDraft,
  editor,
  triggerInlineGhost,
  ghostLoading,
  ghostVisible,
});
</script>
