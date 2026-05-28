<template>
  <TextEditor
    ref="editorRef"
    :editor-class="[
      'prose-sm max-w-full mx-6 md:mx-10 max-h-[50vh] py-3',
      'min-h-[7rem]',
      getFontFamily(newEmail),
      editable && '!max-h-[35vh] overflow-y-auto',
    ]"
    :content="newEmail"
    :starterkit-options="{ heading: { levels: [2, 3, 4, 5, 6] } }"
    :placeholder="placeholder"
    :editable="editable"
    @change="editable ? (newEmail = $event) : null"
    :extensions="ghostExtensions"
    :uploadFunction="(file:any)=>uploadFunction(file, doctype, ticketId)"
  >
    <template #top>
      <div class="mx-6 md:mx-10 flex items-center gap-2 border-y py-2.5">
        <span class="text-xs text-gray-500">TO:</span>
        <MultiSelectInput
          v-model="toEmailsClone"
          class="flex-1"
          :validate="validateEmailWithZod"
          :error-message="(value) => `${value} is an invalid email address`"
        />
        <Button
          :label="'CC'"
          :class="[cc ? 'bg-gray-300 hover:bg-gray-200' : '']"
          @click="toggleCC()"
        />
        <Button
          :label="'BCC'"
          :class="[bcc ? 'bg-gray-300 hover:bg-gray-200' : '']"
          @click="toggleBCC()"
        />
      </div>
      <div
        v-if="showCC || cc"
        class="mx-10 flex items-center gap-2 py-2.5"
        :class="cc || showCC ? 'border-b' : ''"
      >
        <span class="text-xs text-gray-500">CC:</span>
        <MultiSelectInput
          ref="ccInput"
          v-model="ccEmailsClone"
          class="flex-1"
          :validate="validateEmailWithZod"
          :error-message="(value) => `${value} is an invalid email address`"
        />
      </div>
      <div
        v-if="showBCC || bcc"
        class="mx-10 flex items-center gap-2 py-2.5"
        :class="bcc || showBCC ? 'border-b' : ''"
      >
        <span class="text-xs text-gray-500">BCC:</span>
        <MultiSelectInput
          ref="bccInput"
          v-model="bccEmailsClone"
          class="flex-1"
          :validate="validateEmailWithZod"
          :error-message="(value) => `${value} is an invalid email address`"
        />
      </div>
    </template>
    <!-- <template v-slot:editor="{ _editor }">
      <EditorContent
        :class="[editable && 'max-h-[35vh] overflow-y-auto']"
        :editor="_editor"
      />
    </template> -->
    <template #bottom>
      <!-- Attachments -->
      <div class="flex flex-wrap gap-2 px-10">
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
              @click.self.stop="removeAttachment(a)"
            />
          </template>
        </AttachmentItem>
      </div>
      <!-- NextAI inline ghost status (FIX D, 2026-05-26).
           Always rendered so toggling its content doesn't shift the layout;
           v-show keeps the space allocated only while loading/visible. -->
      <div v-show="ghostLoading || ghostVisible" class="flex px-10 mt-1">
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
      <!-- TextEditor Fixed Menu -->
      <div
        class="flex justify-between overflow-scroll pl-10 py-2.5 items-center"
      >
        <div class="flex items-center overflow-x-auto w-[60%]">
          <div class="flex gap-1">
            <FileUploader
              :upload-args="{
                doctype: doctype,
                docname: ticketId,
                private: true,
              }"
              @success="
                (f) => {
                  attachments.push(f);
                }
              "
            >
              <template #default="{ openFileSelector, uploading }">
                {{ void (isUploading = uploading) }}
                <Button
                  variant="ghost"
                  @click="openFileSelector()"
                  :loading="uploading"
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
          <Button
            variant="ghost"
            @click="showSavedRepliesSelectorModal = true"
          >
              <template #icon>
                <SavedReplyIcon class="h-4" />
              </template>
            </Button>
            <Button
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
          <TextEditorFixedMenu class="ml-1" :buttons="textEditorMenuButtons" />
        </div>
        <div
          class="flex items-center justify-end space-x-2 sm:mt-0 w-[40%] mr-9"
        >
          <Button label="Discard" @click="handleDiscard" />
          <Button
            variant="solid"
            :disabled="isDisabled"
            :loading="sendMail.loading"
            :label="label"
            @click="
              () => {
                submitMail();
              }
            "
          />
        </div>
      </div>
    </template>
  </TextEditor>
  <SavedRepliesSelectorModal
    v-if="showSavedRepliesSelectorModal"
    v-model="showSavedRepliesSelectorModal"
    :doctype="doctype"
    @apply="applySavedReplies"
    :ticketId="ticketId"
  />
</template>

<script setup lang="ts">
import {
  AttachmentItem,
  SavedRepliesSelectorModal,
  MultiSelectInput,
} from "@/components";
import { AttachmentIcon } from "@/components/icons";
import { useTyping } from "@/composables/realtime";
import { useAuthStore } from "@/stores/auth";
import { PreserveVideoControls } from "@/tiptap-extensions";
import {
  getFontFamily,
  isContentEmpty,
  removeAttachmentFromServer,
  textEditorMenuButtons,
  uploadFunction,
  validateEmailWithZod,
} from "@/utils";
// import { EditorContent } from "@tiptap/vue-3";
import { useStorage } from "@vueuse/core";
import {
  FileUploader,
  TextEditor,
  TextEditorFixedMenu,
  createResource,
  toast,
} from "frappe-ui";
import { useOnboarding } from "frappe-ui/frappe";
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import SavedReplyIcon from "./icons/SavedReplyIcon.vue";
import Sparkles from "~icons/lucide/sparkles";
import {
  InlineGhostSuggestion,
  InlineGhostKey,
} from "@/components/openclaw/InlineGhostSuggestion";

const editorRef = ref(null);
const showSavedRepliesSelectorModal = ref(false);

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
    default: "Send",
  },
  editable: {
    type: Boolean,
    default: true,
  },
  doctype: {
    type: String,
    default: "HD Ticket",
  },
  toEmails: {
    type: Array,
    default: () => [],
  },
  ccEmails: {
    type: Array,
    default: () => [],
  },
  bccEmails: {
    type: Array,
    default: () => [],
  },
});

const label = computed(() => {
  return sendMail.loading ? "Sending..." : props.label;
});

const emit = defineEmits(["submit", "discard", "request-ai"]);

const newEmail = useStorage<null | string>(
  "emailBoxContent" + props.ticketId,
  null
);
const { updateOnboardingStep } = useOnboarding("helpdesk");
const { isManager } = useAuthStore();

// Initialize typing composable
const { onUserType, cleanup } = useTyping(props.ticketId);

const attachments = ref([]);
const isUploading = ref(false);
const isDisabled = computed(() => {
  return (
    isContentEmpty(newEmail.value) || sendMail.loading || isUploading.value
  );
});

// Watch for changes in email content to trigger typing events
watch(newEmail, (newValue, oldValue) => {
  if (newValue !== oldValue && newValue) {
    onUserType();
  }
});

onBeforeUnmount(() => {
  cleanup();
});

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

// Reflect the InlineGhost plugin's `loading` flag so the parent component
// can show a spinner on the "Draft with NextAI" button. Hooked up after the
// inner tiptap editor is created (see watcher below).
const ghostLoading = ref(false);
// Reflect whether a ghost suggestion is currently rendered after the caret.
// Drives the "Tab to accept · Esc to dismiss" hint chip (FIX D, 2026-05-26)
// so the user knows the inline draft is keyboard-actionable.
const ghostVisible = ref(false);
let ghostTxnUnsubscribe: (() => void) | null = null;

function bindGhostLoadingSubscription(ed: any) {
  if (!ed) return;
  const handler = () => {
    const ps = InlineGhostKey.getState(ed.state);
    ghostLoading.value = !!ps?.loading;
    // ghostVisible derives from the same plugin state: a ghost is visible
    // when both the text exists AND it's anchored to a caret position.
    ghostVisible.value = !!(ps?.ghost && ps?.anchorPos != null);
  };
  ed.on("transaction", handler);
  ghostTxnUnsubscribe = () => {
    try {
      ed.off("transaction", handler);
    } catch {
      // ignore — editor already destroyed
    }
  };
}

function triggerInlineGhost(prefixOverride?: string) {
  const ed = editorRef.value?.editor;
  if (!ed) return;
  // chain() rebuilds command list; call the raw command directly.
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

const toEmailsClone = ref([...props.toEmails]);
const ccEmailsClone = ref([...props.ccEmails]);
const bccEmailsClone = ref([...props.bccEmails]);
const showCC = ref(false);
const showBCC = ref(false);
const cc = computed(() => (ccEmailsClone.value?.length ? true : false));
const bcc = computed(() => (bccEmailsClone.value?.length ? true : false));
const ccInput = ref(null);
const bccInput = ref(null);

function applySavedReplies(template: string) {
  isContentEmpty(newEmail.value)
    ? (newEmail.value = template)
    : (newEmail.value = newEmail.value + "\n" + template);
  showSavedRepliesSelectorModal.value = false;
}

function insertDraft(template: string) {
  if (!template) return;

  newEmail.value = isContentEmpty(newEmail.value)
    ? template
    : `${newEmail.value}\n\n${template}`;

  nextTick(() => {
    editorRef.value?.editor?.commands?.focus("end");
  });
}

const sendMail = createResource({
  url: "run_doc_method",
  makeParams: () => ({
    dt: props.doctype,
    dn: props.ticketId,
    method: "reply_via_agent",
    args: {
      attachments: attachments.value.map((x) => x.name),
      to: toEmailsClone.value.join(","),
      cc: ccEmailsClone.value?.join(","),
      bcc: bccEmailsClone.value?.join(","),
      message: newEmail.value,
    },
  }),
  onSuccess: () => {
    resetState();
    emit("submit");

    if (isManager) {
      updateOnboardingStep("reply_on_ticket");
    }
  },
  debounce: 300,
});

function submitMail() {
  if (isContentEmpty(newEmail.value)) {
    return false;
  }
  if (!toEmailsClone.value.length) {
    toast.warning(
      "Email has no recipients. Please add at least one email address in the 'TO' field."
    );
    return false;
  }

  sendMail.submit();
}

function toggleCC() {
  showCC.value = !showCC.value;

  showCC.value &&
    nextTick(() => {
      ccInput.value.setFocus();
    });
}

function toggleBCC() {
  showBCC.value = !showBCC.value;
  showBCC.value &&
    nextTick(() => {
      bccInput.value.setFocus();
    });
}

async function removeAttachment(attachment) {
  attachments.value = attachments.value.filter((a) => a !== attachment);
  await removeAttachmentFromServer(attachment.name);
}

function addToReply(
  body: string,
  toEmails: string[],
  ccEmails: string[],
  bccEmails: string[]
) {
  toEmailsClone.value = toEmails;
  ccEmailsClone.value = ccEmails;
  bccEmailsClone.value = bccEmails;
  editorRef.value.editor
    .chain()
    .clearContent()
    .insertContent(body)
    .focus("all")
    .setBlockquote()
    .insertContentAt(0, { type: "paragraph" })
    .focus("start")
    .run();
}

function resetState() {
  newEmail.value = null;
  attachments.value = [];
}

function handleDiscard() {
  attachments.value = [];
  newEmail.value = null;

  ccEmailsClone.value = [];
  bccEmailsClone.value = [];
  ccEmailsClone.value = [];
  showCC.value = false;
  showBCC.value = false;

  emit("discard");
}

const editor = computed(() => {
  return editorRef.value.editor;
});

defineExpose({
  addToReply,
  insertDraft,
  editor,
  submitMail,
  triggerInlineGhost,
  ghostLoading,
  ghostVisible,
});
</script>

<style>
/* Inline ghost-text suggestion (Gmail Smart Compose / Gemini style).
   The widget decoration is rendered globally on the editor DOM so we use a
   non-scoped block here. */
.oc-inline-ghost {
  opacity: 0.4;
  font-style: italic;
  pointer-events: none;
  user-select: none;
}
</style>
