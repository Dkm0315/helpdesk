<template>
  <div class="comm-area">
    <div
      class="flex justify-between gap-3 border-t px-6 md:px-10 py-4 md:py-2.5"
    >
      <div class="flex gap-1.5 items-center">
        <Button
          ref="sendEmailRef"
          variant="ghost"
          label="Reply"
          :class="[showEmailBox ? '!bg-gray-300 hover:!bg-gray-200' : '']"
          @click="toggleEmailBox()"
        >
          <template #prefix>
            <EmailIcon class="h-4" />
          </template>
        </Button>
        <Button
          variant="ghost"
          label="Comment"
          :class="[showCommentBox ? '!bg-gray-300 hover:!bg-gray-200' : '']"
          @click="toggleCommentBox()"
        >
          <template #prefix>
            <CommentIcon class="h-4" />
          </template>
        </Button>
        <Button
          v-if="showEmailBox"
          variant="subtle"
          label="Draft with NextAI"
          :loading="emailGhostLoading"
          @click="generateInlineDraft('reply')"
        >
          <template #prefix>
            <Sparkles class="h-4 w-4" />
          </template>
        </Button>
        <Button
          v-if="showCommentBox"
          variant="subtle"
          label="Draft with NextAI"
          :loading="commentGhostLoading"
          @click="generateInlineDraft('comment')"
        >
          <template #prefix>
            <Sparkles class="h-4 w-4" />
          </template>
        </Button>
        <TypingIndicator :ticketId="ticketId" />
      </div>
    </div>
    <div
      ref="emailBoxRef"
      v-show="showEmailBox"
      class="flex flex-col gap-1.5 flex-1"
      @keydown.ctrl.enter.capture.stop="submitEmail"
      @keydown.meta.enter.capture.stop="submitEmail"
    >
      <EmailEditor
        ref="emailEditorRef"
        :label="
          isMobileView ? 'Send' : isMac ? 'Send (⌘ + ⏎)' : 'Send (Ctrl + ⏎)'
        "
        v-model:content="content"
        placeholder="Hi John, we are looking into this issue."
        :ticketId="ticketId"
        :to-emails="toEmails"
        :cc-emails="ccEmails"
        :bcc-emails="bccEmails"
        @request-ai="generateInlineDraft('reply')"
        @submit="
          () => {
            showEmailBox = false;
            emit('update');
          }
        "
        @discard="
          () => {
            showEmailBox = false;
          }
        "
      />
    </div>
    <div
      ref="commentBoxRef"
      v-show="showCommentBox"
      class="flex flex-col"
      @keydown.ctrl.enter.capture.stop="submitComment"
      @keydown.meta.enter.capture.stop="submitComment"
    >
      <CommentTextEditor
        ref="commentTextEditorRef"
        :label="
          isMobileView
            ? 'Comment'
            : isMac
            ? 'Comment (⌘ + ⏎)'
            : 'Comment (Ctrl + ⏎)'
        "
        :ticketId="ticketId"
        :editable="showCommentBox"
        :doctype="doctype"
        placeholder="@John could you please look into this?"
        @request-ai="generateInlineDraft('comment')"
        @submit="
          () => {
            showCommentBox = false;
            emit('update');
          }
        "
        @discard="
          () => {
            showCommentBox = false;
          }
        "
      />
    </div>
    <!-- Floating NextAI drawer: teleported to <body>, slides in from the right.
         The Reply/Comment buttons trigger ghost text in the inline composer
         instead — this drawer is opened from the floating launcher (see
         OpenClawLauncher mounted in TicketAgent.vue) and from the legacy
         header "Open NextAI" path. -->
    <NextAIPanel
      :open="aiDrawerOpen"
      :surface="aiDrawerSurface"
      reference-doctype="HD Ticket"
      :reference-name="ticketId"
      :get-parent-editor="aiDrawerSurface === 'helpdesk_comment' ? getCommentEditor : getReplyEditor"
      :on-insert="(t) => (aiDrawerSurface === 'helpdesk_comment' ? insertCommentDraft(t) : insertEmailDraft(t))"
      @update:open="(v) => (aiDrawerOpen = v)"
    />
  </div>
</template>

<script setup lang="ts">
import { CommentTextEditor, EmailEditor, TypingIndicator } from "@/components";
import { CommentIcon, EmailIcon } from "@/components/icons/";
import { useDevice } from "@/composables";
import { useScreenSize } from "@/composables/screen";
import { useShortcut } from "@/composables/shortcuts";
import NextAIPanel from "@/components/openclaw/NextAIPanel.vue";
import { showCommentBox, showEmailBox } from "@/pages/ticket/modalStates";
import { computed, inject, ref, watch } from "vue";
import { onClickOutside } from "@vueuse/core";
import Sparkles from "~icons/lucide/sparkles";
import { TicketContactSymbol, TicketSymbol } from "@/types";

const emit = defineEmits(["update", "open-ai"]);
const content = defineModel("content");
const { isMac } = useDevice();
const { isMobileView } = useScreenSize();
let doc = defineModel();
// let doc = inject(TicketSymbol)?.value.doc
const emailEditorRef = ref(null);
const commentTextEditorRef = ref(null);
const emailBoxRef = ref(null);
const commentBoxRef = ref(null);

function unwrapMaybeRef(v: any): any {
  if (v == null) return v;
  if (typeof v === "object" && "value" in v) return v.value;
  return v;
}

const emailGhostLoading = computed(() =>
  !!unwrapMaybeRef(emailEditorRef.value?.ghostLoading)
);
const commentGhostLoading = computed(() =>
  !!unwrapMaybeRef(commentTextEditorRef.value?.ghostLoading)
);

// Floating drawer state (replaces the old inline aiReplyOpen / aiCommentOpen).
const aiDrawerOpen = ref(false);
const aiDrawerSurface = ref<"helpdesk_ticket" | "helpdesk_comment">(
  "helpdesk_ticket"
);

// Resolve a friendly contact greeting for the ghost-text prefix.
const ticketResource = inject(TicketSymbol, null);
const contactResource = inject(TicketContactSymbol, null);
const contactGreeting = computed(() => {
  const contactName =
    (contactResource as any)?.value?.data?.full_name ||
    (contactResource as any)?.value?.data?.first_name ||
    (contactResource as any)?.value?.data?.name ||
    (ticketResource as any)?.value?.doc?.contact ||
    (ticketResource as any)?.value?.doc?.customer ||
    "";
  if (contactName) {
    // Just the first name token to keep the salutation natural.
    const first = String(contactName).trim().split(/\s+/)[0];
    if (first) return `Hi ${first}, `;
  }
  return "Hi, ";
});

function getReplyEditor() {
  return emailEditorRef.value?.editor || null;
}

function getCommentEditor() {
  return commentTextEditorRef.value?.editor || null;
}

function toggleEmailBox() {
  if (showCommentBox.value) {
    showCommentBox.value = false;
  }
  showEmailBox.value = !showEmailBox.value;
}

function toggleCommentBox() {
  if (showEmailBox.value) {
    showEmailBox.value = false;
  }
  showCommentBox.value = !showCommentBox.value;
}

function submitEmail() {
  if (emailEditorRef.value.submitMail()) {
    emit("update");
  }
}

function submitComment() {
  if (commentTextEditorRef.value.submitComment()) {
    emit("update");
  }
}

function splitIfString(str: string | string[]) {
  if (typeof str === "string") {
    return str.split(",");
  }
  return str;
}

function replyToEmail(data: object) {
  showEmailBox.value = true;

  emailEditorRef.value.addToReply(
    data.content,
    splitIfString(data.to),
    splitIfString(data.cc),
    splitIfString(data.bcc)
  );
}

function insertEmailDraft(content: string) {
  showCommentBox.value = false;
  showEmailBox.value = true;
  emailEditorRef.value?.insertDraft?.(content);
}

function insertCommentDraft(content: string) {
  showEmailBox.value = false;
  showCommentBox.value = true;
  commentTextEditorRef.value?.insertDraft?.(content);
}

// "Draft with NextAI" toolbar buttons trigger inline ghost text in the live
// composer (Gmail Smart Compose style). The user accepts with Tab. No drawer
// involvement — the floating launcher (mounted on the ticket page) is the
// dedicated entry point for the full chat UI.
function generateInlineDraft(mode: "reply" | "comment") {
  if (mode === "reply") {
    showCommentBox.value = false;
    showEmailBox.value = true;
    requestGhostInComposer(emailEditorRef);
  } else {
    showEmailBox.value = false;
    showCommentBox.value = true;
    requestGhostInComposer(commentTextEditorRef);
  }
}

function requestGhostInComposer(editorRef: any) {
  // Wait a tick so the box has rendered and the inner editor exists.
  setTimeout(() => {
    const inner = editorRef.value?.editor;
    if (!inner) return;
    inner.commands.focus("end");
    const text = (inner.getText?.() || "").trim();
    // Pass the editor's current content (or our greeting prefill) so the
    // backend can build a coherent continuation; the InlineGhost extension
    // tracks ghostLoading via its plugin meta.
    let prefix: string;
    if (text.length === 0) {
      prefix = contactGreeting.value;
      // Seed the editor so the ghost has somewhere to attach after the
      // caret. The greeting itself shouldn't be overwritten when the ghost
      // arrives — InlineGhost renders the suggestion AFTER the caret.
      inner.commands.insertContent(prefix);
    } else {
      prefix = inner.state.doc.textBetween(
        0,
        inner.state.selection.from,
        "\n"
      );
    }
    editorRef.value?.triggerInlineGhost?.(prefix);
  }, 0);
}

function toggleAIDrawer(surface?: "helpdesk_ticket" | "helpdesk_comment") {
  if (surface) aiDrawerSurface.value = surface;
  aiDrawerOpen.value = !aiDrawerOpen.value;
}

const props = defineProps({
  doctype: {
    type: String,
    default: "HD Ticket",
  },
  ticketId: {
    type: String,
    default: null,
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

watch(
  () => showEmailBox.value,
  (value) => {
    if (value) {
      emailEditorRef.value?.editor?.commands?.focus();
    }
  }
);

watch(
  () => showCommentBox.value,
  (value) => {
    if (value) {
      commentTextEditorRef.value?.editor?.commands?.focus();
    }
  }
);

useShortcut("r", () => {
  toggleEmailBox();
});
useShortcut("c", () => {
  toggleCommentBox();
});

function openAIFromComposer(mode: "reply" | "comment") {
  generateInlineDraft(mode);
}

defineExpose({
  replyToEmail,
  insertEmailDraft,
  insertCommentDraft,
  toggleEmailBox,
  toggleCommentBox,
  openAIFromComposer,
  toggleAIDrawer,
  aiDrawerOpen,
  editor: emailEditorRef,
});

onClickOutside(
  emailBoxRef,
  () => {
    if (showEmailBox.value) {
      showEmailBox.value = false;
    }
  },
  {
    ignore: [".tippy-box", ".tippy-content", ".PopoverContent"],
  }
);

onClickOutside(
  commentBoxRef,
  () => {
    if (showCommentBox.value) {
      showCommentBox.value = false;
    }
  },
  {
    ignore: [".tippy-box", ".tippy-content", ".PopoverContent"],
  }
);
</script>

<style>
@media screen and (max-width: 640px) {
  .comm-area {
    width: 100vw;
  }
}
</style>
