/**
 * Tiptap extension that renders an inline "ghost text" continuation suggestion
 * after the caret, like Gmail Smart Compose / Gemini "Help me write".
 *
 * Behavior:
 *  - After the user pauses typing for `debounceMs` (default 500ms), if the
 *    prefix ends on a word boundary and is long enough, calls
 *    `fetchCompletion(prefix)` and shows the returned text as a grey italic
 *    widget decoration directly after the cursor.
 *  - `Tab` inserts the ghost into the document and moves the caret to the
 *    end of the inserted text. If there is no ghost, Tab is NOT swallowed
 *    (returns false → other extensions / browser handle it normally).
 *  - `Escape` dismisses the ghost without inserting (only consumed when a
 *    ghost is visible).
 *  - Any document change clears the current ghost so stale suggestions never
 *    linger.
 *  - The ghost is a ProseMirror widget Decoration — NOT a node — so it
 *    counts as zero document content.
 *  - `Editor.commands.triggerInlineGhost(prefixOverride?)` imperatively
 *    requests a fresh ghost RIGHT NOW (bypasses the 500ms idle debounce).
 *    Used by the "Draft with NextAI" toolbar button.
 *  - Plugin state carries a `loading` boolean so parent Vue code can show
 *    a button spinner while the LLM is responding.
 */

import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

export interface InlineGhostOptions {
  fetchCompletion: (prefix: string) => Promise<string>
  debounceMs: number
  minPrefixChars: number
  maxPrefixChars: number
  enabled: () => boolean
}

interface PluginState {
  ghost: string
  anchorPos: number | null
  ghostId: number
  loading: boolean
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    inlineGhostSuggestion: {
      /**
       * Force-trigger an inline ghost-text fetch right now (skips the idle
       * debounce). Pass `prefixOverride` to bias the LLM with a custom
       * prefix (e.g. "Hi John, ") instead of using the editor content up
       * to the caret.
       */
      triggerInlineGhost: (prefixOverride?: string) => ReturnType
    }
  }
}

export const InlineGhostKey = new PluginKey<PluginState>('inlineGhost')

export const InlineGhostSuggestion = Extension.create<InlineGhostOptions>({
  name: 'inlineGhostSuggestion',

  addOptions() {
    return {
      fetchCompletion: async () => '',
      debounceMs: 500,
      minPrefixChars: 12,
      maxPrefixChars: 4000,
      enabled: () => true,
    }
  },

  addKeyboardShortcuts() {
    return {
      Tab: ({ editor }) => {
        const state = InlineGhostKey.getState(editor.state)
        if (!state?.ghost) return false
        const ghost = state.ghost
        editor.chain().focus().insertContent(ghost).run()
        editor.view.dispatch(
          editor.state.tr.setMeta(InlineGhostKey, { type: 'clear' }),
        )
        return true
      },
      Escape: ({ editor }) => {
        const state = InlineGhostKey.getState(editor.state)
        if (!state?.ghost) return false
        editor.view.dispatch(
          editor.state.tr.setMeta(InlineGhostKey, { type: 'clear' }),
        )
        return true
      },
    }
  },

  addCommands() {
    const opts = this.options
    // Track the manual-trigger request id separately from the debounced one
    // so a button click always wins over an in-flight idle fetch.
    let manualRequestId = 0
    return {
      triggerInlineGhost:
        (prefixOverride?: string) =>
        ({ editor }) => {
          if (!opts.enabled()) return false
          const view = editor.view
          const { from } = view.state.selection
          const docText = view.state.doc.textBetween(0, from, '\n')
          const prefix =
            prefixOverride !== undefined && prefixOverride !== null
              ? String(prefixOverride)
              : docText
          // Mark loading: true so the UI can show a spinner.
          const psBefore = InlineGhostKey.getState(view.state)
          view.dispatch(
            view.state.tr.setMeta(InlineGhostKey, {
              type: 'loading',
              loading: true,
              ghostId: psBefore?.ghostId ?? 0,
            }),
          )
          const myId = ++manualRequestId
          ;(async () => {
            let completion = ''
            try {
              completion = await opts.fetchCompletion(
                prefix.slice(-opts.maxPrefixChars),
              )
            } catch {
              completion = ''
            }
            if (myId !== manualRequestId) return
            const psAfter = InlineGhostKey.getState(editor.state)
            const tr = editor.state.tr.setMeta(InlineGhostKey, {
              type: 'set',
              ghost: completion || '',
              anchorPos: editor.state.selection.from,
              ghostId: psAfter?.ghostId ?? 0,
              loading: false,
            })
            editor.view.dispatch(tr)
          })()
          return true
        },
    }
  },

  addProseMirrorPlugins() {
    const opts = this.options
    let debounceTimer: number | null = null
    let lastPrefix = ''
    let requestId = 0

    return [
      new Plugin<PluginState>({
        key: InlineGhostKey,
        state: {
          init: () => ({ ghost: '', anchorPos: null, ghostId: 0, loading: false }),
          apply(tr, prev) {
            const meta = tr.getMeta(InlineGhostKey) as
              | {
                  type: string
                  ghost?: string
                  anchorPos?: number
                  ghostId?: number
                  loading?: boolean
                }
              | undefined
            if (meta?.type === 'set' && (meta.ghostId === undefined || meta.ghostId === prev.ghostId)) {
              return {
                ghost: meta.ghost || '',
                anchorPos:
                  meta.anchorPos !== undefined && meta.anchorPos !== null
                    ? meta.anchorPos
                    : null,
                ghostId: prev.ghostId,
                // 'set' always clears loading (the fetch finished).
                loading: meta.loading === true ? true : false,
              }
            }
            if (meta?.type === 'clear') {
              return {
                ghost: '',
                anchorPos: null,
                ghostId: prev.ghostId + 1,
                loading: false,
              }
            }
            if (meta?.type === 'loading') {
              return {
                ...prev,
                loading: meta.loading === true,
              }
            }
            // Any doc-changing tr without an explicit set/clear meta invalidates
            // the current ghost — keeps stale suggestions from lingering across
            // unrelated edits.
            if (tr.docChanged) {
              return {
                ghost: '',
                anchorPos: null,
                ghostId: prev.ghostId + 1,
                loading: prev.loading,
              }
            }
            return prev
          },
        },
        props: {
          decorations(state) {
            const ps = InlineGhostKey.getState(state)
            if (!ps?.ghost || ps.anchorPos == null) return DecorationSet.empty
            const widget = Decoration.widget(
              ps.anchorPos,
              () => {
                const span = document.createElement('span')
                span.textContent = ps.ghost
                span.className = 'oc-inline-ghost'
                span.style.opacity = '0.4'
                span.style.fontStyle = 'italic'
                span.style.userSelect = 'none'
                span.style.pointerEvents = 'none'
                return span
              },
              { side: 1 },
            )
            return DecorationSet.create(state.doc, [widget])
          },
        },
        view(view) {
          const fetchAndShow = async () => {
            if (!opts.enabled()) return
            const { state } = view
            // Only at a collapsed cursor.
            if (state.selection.from !== state.selection.to) return
            const { from } = state.selection
            const prefix = state.doc.textBetween(0, from, '\n')
            if (prefix.length < opts.minPrefixChars) return
            // Only fire when the caret sits after whitespace or punctuation —
            // otherwise we'd suggest mid-word which looks broken.
            const lastChar = prefix.slice(-1)
            if (!/[\s.,;:!?]/.test(lastChar)) return
            if (prefix === lastPrefix) return
            lastPrefix = prefix
            const myId = ++requestId
            try {
              const completion = await opts.fetchCompletion(
                prefix.slice(-opts.maxPrefixChars),
              )
              if (myId !== requestId) return
              if (!completion) return
              const ps = InlineGhostKey.getState(view.state)
              view.dispatch(
                view.state.tr.setMeta(InlineGhostKey, {
                  type: 'set',
                  ghost: completion,
                  anchorPos: view.state.selection.from,
                  ghostId: ps?.ghostId ?? 0,
                }),
              )
            } catch {
              // Ghost text is best-effort — swallow.
            }
          }

          return {
            update() {
              if (debounceTimer) window.clearTimeout(debounceTimer)
              debounceTimer = window.setTimeout(
                fetchAndShow,
                opts.debounceMs,
              ) as unknown as number
            },
            destroy() {
              if (debounceTimer) window.clearTimeout(debounceTimer)
              requestId++ // invalidate any in-flight requests on teardown
            },
          }
        },
      }),
    ]
  },
})

export default InlineGhostSuggestion
