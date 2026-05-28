import { call } from "frappe-ui";
import { computed, onBeforeUnmount, ref, type ComputedRef, type Ref } from "vue";
import { socket } from "@/socket";

export type AIContext = {
  enabled: boolean;
  display_name: string;
  user: string;
  access_tier: string;
  surface: string;
  source_doctype?: string;
  source_name?: string;
  feature_flags: Record<string, boolean>;
};

export type AICommand = {
  name: string;
  label: string;
  description: string;
  surfaces: string[];
  requires_write: boolean;
};

export type StreamToolCall = {
  id: string;
  name: string;
  status: "start" | "done";
  args?: any;
  result?: any;
  startedAt: number;
  endedAt?: number;
};

export type StreamState = {
  thinkingLine: Ref<string>;
  tokens: Ref<string[]>;
  fullText: ComputedRef<string>;
  toolCalls: Ref<StreamToolCall[]>;
  running: Ref<boolean>;
  elapsedSec: Ref<number>;
  error: Ref<string>;
  finalText: Ref<string>;
  lastEventAt: Ref<number>;
  phase: Ref<string>;
};

export type StreamingRunHandle = {
  state: StreamState;
  start: (runName: string) => void;
  stop: (runName: string) => Promise<void>;
  steer: (runName: string, instruction: string) => Promise<void>;
  modify: (runName: string, instruction: string) => Promise<void>;
  cleanup: () => void;
};

export function getAIContext(params: {
  source_doctype?: string;
  source_name?: string;
  surface?: string;
}) {
  return call("quant_customizations.api.openclaw_ai.get_ai_context", params);
}

export function getCommandCatalog(params: {
  source_doctype?: string;
  source_name?: string;
  surface?: string;
}) {
  return call("quant_customizations.api.openclaw_ai.get_command_catalog", params);
}

export function startAIRun(params: {
  intent?: string;
  prompt?: string;
  source_doctype?: string;
  source_name?: string;
  surface?: string;
  persona?: string;
  track?: string;
  payload?: Record<string, unknown>;
  session_key?: string;
}) {
  return call("quant_customizations.api.openclaw_ai.start_run", {
    ...params,
    payload: params.payload ? JSON.stringify(params.payload) : undefined,
  });
}

export function getAIRunStatus(run: string) {
  return call("quant_customizations.api.openclaw_ai.get_run_status", { run });
}

export function getRunHistory(params: {
  source_doctype?: string;
  source_name?: string;
  surface?: string;
  session_key?: string;
  limit?: number;
}) {
  return call("quant_customizations.api.openclaw_ai.get_run_history", params);
}

export function stopAIRun(run: string) {
  return call("quant_customizations.api.openclaw_ai.stop_run", { run });
}

export function steerAIRun(run: string, instruction: string) {
  return call("quant_customizations.api.openclaw_ai.steer_run", { run, instruction });
}

export function modifyAIRun(run: string, instruction: string) {
  return call("quant_customizations.api.openclaw_ai.modify_run", { run, instruction });
}

export function createDevHandoff(params: {
  source_doctype: string;
  source_name: string;
  instruction?: string;
}) {
  return call("quant_customizations.api.openclaw_ai.create_dev_handoff", params);
}

/**
 * Per-doc OpenClaw session-key persistence keyed by {doctype}:{name}.
 * Stored in localStorage so a tab reload re-attaches to the same gateway session.
 */
const SESSION_PREFIX = "openclaw_session";

export function getStoredSessionKey(doctype?: string, name?: string): string | undefined {
  if (!doctype || !name) return undefined;
  try {
    return localStorage.getItem(`${SESSION_PREFIX}:${doctype}:${name}`) || undefined;
  } catch {
    return undefined;
  }
}

export function rememberSessionKey(doctype: string | undefined, name: string | undefined, key: string | undefined) {
  if (!doctype || !name || !key) return;
  try {
    localStorage.setItem(`${SESSION_PREFIX}:${doctype}:${name}`, key);
  } catch {
    /* ignore */
  }
}

/**
 * Token-by-token streaming over Frappe Socket.IO.
 *
 * Realtime contract (FIX A — 2026-05-26):
 *   Frappe's realtime server (`frappe_handlers.js`) has NO generic
 *   `socket.on('join', ...)` handler — only `task_subscribe`,
 *   `doctype_subscribe`, `doc_subscribe`. Sending `socket.emit('join', ...)`
 *   reaches nobody, and `publish_realtime(room=...)` on the backend then
 *   delivers to zero subscribers.
 *
 *   Instead the backend `publish_realtime` calls use `user=<doc.user>`
 *   (every tab for that user gets the event) and stamp `run = <run_name>`
 *   into every payload. The handlers below filter on `payload.run` to
 *   ignore frames from other concurrent runs.
 *
 *   Events received from backend:
 *     openclaw_progress {run, label, phase}
 *     openclaw_delta    {run, token}
 *     openclaw_tool     {run, name, status: "start"|"done", args?, result?}
 *     openclaw_done     {run, final}
 *     openclaw_error    {run, message}
 *     openclaw_stopped  {run}
 *     openclaw_steered  {run, instruction}
 *     openclaw_modified {run, instruction}
 */
export function useStreamingRun(): StreamingRunHandle {
  const thinkingLine = ref<string>("");
  const tokens = ref<string[]>([]);
  const toolCalls = ref<StreamToolCall[]>([]);
  const running = ref<boolean>(false);
  const elapsedSec = ref<number>(0);
  const error = ref<string>("");
  const finalText = ref<string>("");
  const lastEventAt = ref<number>(0);
  const phase = ref<string>("");

  const fullText = computed(() => (finalText.value ? finalText.value : tokens.value.join("")));

  // The run we are currently streaming for. Handlers filter on this so frames
  // from other concurrent runs (other tabs / earlier runs not yet GC'd by the
  // backend) are ignored.
  let currentRunName = "";
  let startedAt = 0;
  let timer: ReturnType<typeof setInterval> | undefined;

  // Return true iff the event payload targets the run we're currently
  // streaming. Foreign-run events are silently dropped.
  function isForCurrentRun(payload: any): boolean {
    if (!currentRunName) return false;
    if (!payload) return false;
    // Tolerate older payloads that didn't carry `run` — but the contract
    // (test_forward_gateway_stream_every_event_carries_run_field) guarantees
    // it's present from the backend.
    if (payload.run === undefined || payload.run === null) return true;
    return String(payload.run) === currentRunName;
  }

  function onProgress(payload: any) {
    if (!payload) return;
    if (!isForCurrentRun(payload)) return;
    thinkingLine.value = payload.label || thinkingLine.value;
    phase.value = payload.phase || phase.value;
    lastEventAt.value = Date.now();
  }

  function onDelta(payload: any) {
    if (!payload || typeof payload.token !== "string") return;
    if (!isForCurrentRun(payload)) return;
    tokens.value.push(payload.token);
    lastEventAt.value = Date.now();
  }

  function onTool(payload: any) {
    if (!payload || !payload.name) return;
    if (!isForCurrentRun(payload)) return;
    const id = `${payload.name}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
    if (payload.status === "start") {
      toolCalls.value.push({
        id,
        name: payload.name,
        status: "start",
        args: payload.args,
        startedAt: Date.now(),
      });
      thinkingLine.value = `Calling ${humanize(payload.name)}...`;
    } else if (payload.status === "done") {
      const idx = [...toolCalls.value]
        .reverse()
        .findIndex((tc) => tc.name === payload.name && tc.status === "start");
      if (idx !== -1) {
        const realIdx = toolCalls.value.length - 1 - idx;
        toolCalls.value[realIdx] = {
          ...toolCalls.value[realIdx],
          status: "done",
          result: payload.result,
          endedAt: Date.now(),
        };
        const ref = toolCalls.value[realIdx];
        // auto-remove the chip 3s after done
        window.setTimeout(() => {
          toolCalls.value = toolCalls.value.filter((tc) => tc.id !== ref.id);
        }, 3000);
      }
    }
    lastEventAt.value = Date.now();
  }

  function onDone(payload: any) {
    if (!isForCurrentRun(payload)) return;
    finalText.value = (payload && payload.final) || tokens.value.join("");
    running.value = false;
    thinkingLine.value = "Ready for review.";
    phase.value = "done";
    lastEventAt.value = Date.now();
    stopTimer();
  }

  function onError(payload: any) {
    if (!isForCurrentRun(payload)) return;
    error.value = (payload && payload.message) || "Streaming error";
    running.value = false;
    stopTimer();
  }

  function onStopped(payload: any) {
    if (!isForCurrentRun(payload)) return;
    running.value = false;
    thinkingLine.value = "Stopped.";
    phase.value = "stopped";
    stopTimer();
  }

  function bind() {
    socket.on("openclaw_progress", onProgress);
    socket.on("openclaw_delta", onDelta);
    socket.on("openclaw_tool", onTool);
    socket.on("openclaw_done", onDone);
    socket.on("openclaw_error", onError);
    socket.on("openclaw_stopped", onStopped);
  }

  function unbind() {
    socket.off("openclaw_progress", onProgress);
    socket.off("openclaw_delta", onDelta);
    socket.off("openclaw_tool", onTool);
    socket.off("openclaw_done", onDone);
    socket.off("openclaw_error", onError);
    socket.off("openclaw_stopped", onStopped);
  }

  function startTimer() {
    stopTimer();
    startedAt = Date.now();
    elapsedSec.value = 0;
    lastEventAt.value = Date.now();
    timer = setInterval(() => {
      if (!running.value) return;
      elapsedSec.value = Math.floor((Date.now() - startedAt) / 1000);
      const silenceSec = (Date.now() - lastEventAt.value) / 1000;
      if (elapsedSec.value > 5 && silenceSec > 3 && phase.value !== "done") {
        thinkingLine.value = `Still working - ${elapsedSec.value}s elapsed...`;
      }
    }, 1000);
  }

  function stopTimer() {
    if (timer) {
      clearInterval(timer);
      timer = undefined;
    }
  }

  function reset() {
    thinkingLine.value = "";
    tokens.value = [];
    toolCalls.value = [];
    running.value = false;
    elapsedSec.value = 0;
    error.value = "";
    finalText.value = "";
    lastEventAt.value = 0;
    phase.value = "";
  }

  function start(runName: string) {
    if (!runName) return;
    cleanup();
    reset();
    currentRunName = runName;
    bind();
    // NOTE: we intentionally do NOT call socket.emit('join', {room: ...}).
    // Frappe's realtime server has no generic `join` handler. Instead we
    // rely on per-user delivery from `frappe.publish_realtime(user=...)`
    // and filter by `payload.run` inside each handler above.
    running.value = true;
    thinkingLine.value = "Opening session...";
    phase.value = "session.opened";
    startTimer();
  }

  async function stop(runName: string) {
    try {
      await stopAIRun(runName);
    } catch (err) {
      /* surfaced via socket error */
    }
  }

  async function steer(runName: string, instruction: string) {
    try {
      await steerAIRun(runName, instruction);
    } catch (err: any) {
      error.value = err?.messages?.[0] || err?.message || "Could not steer the run.";
    }
  }

  async function modify(runName: string, instruction: string) {
    try {
      await modifyAIRun(runName, instruction);
    } catch (err: any) {
      error.value = err?.messages?.[0] || err?.message || "Could not modify the run.";
    }
  }

  function cleanup() {
    // No room to leave — see start() for why. Just drop the listeners and
    // forget the run name so any late-arriving foreign frames are ignored.
    currentRunName = "";
    unbind();
    stopTimer();
    running.value = false;
  }

  onBeforeUnmount(() => cleanup());

  return {
    state: {
      thinkingLine,
      tokens,
      fullText,
      toolCalls,
      running,
      elapsedSec,
      error,
      finalText,
      lastEventAt,
      phase,
    },
    start,
    stop,
    steer,
    modify,
    cleanup,
  };
}

function humanize(name: string): string {
  return String(name || "")
    .replace(/^oss_manager_/, "")
    .replace(/^openclaw_/, "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (l) => l.toUpperCase());
}
