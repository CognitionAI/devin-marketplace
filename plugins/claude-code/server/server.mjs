#!/usr/bin/env node
// Stdio MCP server that runs the unmodified Claude Code CLI as a background job.
// Tool calls return within WAIT_LIMIT_SECONDS because Devin's MCP calls time out
// after 120 seconds; longer work is picked up by polling get_claude_code_job.
import { execFile, spawn, spawnSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { statSync } from "node:fs";
import { createInterface } from "node:readline";

const CLAUDE_CODE_PACKAGE = "@anthropic-ai/claude-code@2.1.315";
const PROTOCOL_VERSION = "2025-06-18";
const DEFAULT_WAIT_SECONDS = 60;
const WAIT_LIMIT_SECONDS = 100;
const MAX_RETAINED_JOBS = 50;
const MAX_RESULT_CHARS = 60_000;
const MAX_STDERR_CHARS = 4_000;
const CANCEL_KILL_DELAY_MS = 5_000;
const AUTH_STATUS_TIMEOUT_MS = 90_000;

const jobs = new Map();

function billing() {
  const mode = process.env.CLAUDE_CODE_BILLING || "auto";
  if (!["auto", "subscription", "api_key"].includes(mode)) {
    throw new Error("CLAUDE_CODE_BILLING must be auto, subscription, or api_key");
  }
  if (mode === "api_key" && !process.env.ANTHROPIC_API_KEY) {
    throw new Error("CLAUDE_CODE_BILLING is api_key but ANTHROPIC_API_KEY is empty");
  }
  return mode;
}

// Claude Code prefers ANTHROPIC_API_KEY over a subscription login, so a key left
// in the environment must be removed for "subscription" to mean subscription.
function childEnv() {
  const mode = billing();
  const env = { ...process.env };
  delete env.CLAUDE_CODE_BILLING;
  if (!env.ANTHROPIC_API_KEY || mode === "subscription") {
    delete env.ANTHROPIC_API_KEY;
  }
  return env;
}

function claudeCommand() {
  const found = spawnSync("claude", ["--version"], { stdio: "ignore" });
  if (!found.error) return { command: "claude", prefix: [] };
  return { command: "npx", prefix: ["-y", CLAUDE_CODE_PACKAGE] };
}

function clampWait(value) {
  const seconds = value ?? DEFAULT_WAIT_SECONDS;
  if (typeof seconds !== "number" || !Number.isFinite(seconds)) {
    throw new Error("wait_seconds must be a number");
  }
  return Math.min(Math.max(seconds, 0), WAIT_LIMIT_SECONDS);
}

function buildArgs(input) {
  const args = [
    "-p",
    "--output-format",
    "stream-json",
    "--verbose",
    "--permission-mode",
    input.permission_mode ?? "acceptEdits",
  ];
  if (input.model) args.push("--model", input.model);
  if (input.resume_session_id) args.push("--resume", input.resume_session_id);
  if (input.max_turns != null) args.push("--max-turns", String(input.max_turns));
  if (input.max_budget_usd != null) {
    args.push("--max-budget-usd", String(input.max_budget_usd));
  }
  if (input.allowed_tools?.length) {
    args.push("--allowedTools", input.allowed_tools.join(","));
  }
  if (input.disallowed_tools?.length) {
    args.push("--disallowedTools", input.disallowed_tools.join(","));
  }
  for (const dir of input.add_dirs ?? []) args.push("--add-dir", dir);
  return args;
}

function recordEvent(job, event) {
  if (event.type === "system" && event.subtype === "init") {
    job.sessionId = event.session_id;
    job.model = event.model;
    job.apiKeySource = event.apiKeySource;
  } else if (event.type === "assistant") {
    for (const block of event.message?.content ?? []) {
      if (block.type === "tool_use") {
        job.toolUses += 1;
        job.lastTool = block.name;
      } else if (block.type === "text" && block.text) {
        job.lastText = block.text;
      }
    }
  } else if (event.type === "result") {
    job.result = event;
    job.sessionId = event.session_id ?? job.sessionId;
  }
}

function startJob(input) {
  if (typeof input.prompt !== "string" || !input.prompt.trim()) {
    throw new Error("prompt is required");
  }
  if (typeof input.cwd !== "string" || !statSync(input.cwd, { throwIfNoEntry: false })?.isDirectory()) {
    throw new Error(`cwd is not a directory: ${input.cwd}`);
  }
  const env = childEnv();
  const { command, prefix } = claudeCommand();
  const child = spawn(command, [...prefix, ...buildArgs(input)], {
    cwd: input.cwd,
    env,
    // Its own process group, so killing the job also reaches the CLI under npx.
    detached: true,
    stdio: ["pipe", "pipe", "pipe"],
  });
  const job = {
    id: randomUUID(),
    child,
    status: "running",
    startedAt: Date.now(),
    toolUses: 0,
    stderr: "",
    done: null,
  };
  job.done = new Promise((resolve) => {
    const finish = (status, exitCode, error) => {
      if (job.status !== "running") return;
      job.status = job.cancelRequested ? "cancelled" : status;
      job.exitCode = exitCode;
      job.spawnError = error;
      job.finishedAt = Date.now();
      resolve();
    };
    child.on("error", (error) => finish("failed", null, error.message));
    child.on("close", (code) => {
      finish(code === 0 && job.result && !job.result.is_error ? "succeeded" : "failed", code);
    });
  });
  child.stdin.on("error", () => {});
  child.stdin.end(input.prompt);
  child.stderr.setEncoding("utf8");
  child.stderr.on("data", (chunk) => {
    job.stderr = (job.stderr + chunk).slice(-MAX_STDERR_CHARS);
  });
  createInterface({ input: child.stdout }).on("line", (line) => {
    try {
      recordEvent(job, JSON.parse(line));
    } catch {
      // Claude Code's stream is JSON lines; anything else is not job state.
    }
  });
  jobs.set(job.id, job);
  pruneJobs();
  return job;
}

function pruneJobs() {
  const finished = [...jobs.values()].filter((job) => job.status !== "running");
  for (const job of finished.slice(0, Math.max(0, jobs.size - MAX_RETAINED_JOBS))) {
    jobs.delete(job.id);
  }
}

function truncate(text) {
  if (typeof text !== "string" || text.length <= MAX_RESULT_CHARS) return text;
  return `${text.slice(0, MAX_RESULT_CHARS)}\n[truncated ${text.length - MAX_RESULT_CHARS} characters]`;
}

function describeJob(job) {
  const summary = {
    job_id: job.id,
    status: job.status,
    session_id: job.sessionId,
    model: job.model,
    // "none" with a working run means the subscription login was used.
    api_key_source: job.apiKeySource,
    elapsed_seconds: Math.round(((job.finishedAt ?? Date.now()) - job.startedAt) / 1000),
    tool_uses: job.toolUses,
  };
  if (job.status === "running") {
    summary.last_tool = job.lastTool;
    summary.last_text = job.lastText?.slice(-500);
    summary.next_step = "Call get_claude_code_job with this job_id to wait for the result.";
    return summary;
  }
  if (job.result) {
    summary.result = truncate(job.result.result);
    summary.result_subtype = job.result.subtype;
    summary.num_turns = job.result.num_turns;
    summary.estimated_cost_usd = job.result.total_cost_usd;
    summary.permission_denials = job.result.permission_denials?.map((denial) => denial.tool_name);
    if (job.result.errors?.length) summary.errors = job.result.errors;
  }
  if (job.status !== "succeeded") {
    summary.exit_code = job.exitCode;
    if (job.spawnError) summary.error = job.spawnError;
    if (job.stderr) summary.stderr = job.stderr;
    if (job.result?.is_error || !job.result) summary.auth_help = authHelp(job);
  }
  return summary;
}

function authHelp(job) {
  const text = `${job.result?.result ?? ""} ${job.stderr}`;
  if (!/log ?in|auth|api key|credential|401|403/i.test(text)) return undefined;
  return "Save ANTHROPIC_API_KEY in the plugin's connection, or run `claude auth login` on this machine, then retry. Call claude_code_auth_status to check.";
}

async function waitFor(job, seconds) {
  let timer;
  await Promise.race([
    job.done,
    new Promise((resolve) => {
      timer = setTimeout(resolve, seconds * 1000);
    }),
  ]);
  clearTimeout(timer);
}

function getJob(jobId) {
  const job = jobs.get(jobId);
  if (!job) {
    throw new Error(
      `Unknown job ${jobId}. Jobs live in the server process and end with it; resume the work with resume_session_id if you have the session_id.`,
    );
  }
  return job;
}

function signalJob(job, signal) {
  try {
    process.kill(-job.child.pid, signal);
  } catch {
    // The process group has already exited.
  }
}

function stopJob(job) {
  if (job.status !== "running") return;
  job.cancelRequested = true;
  signalJob(job, "SIGTERM");
  setTimeout(() => signalJob(job, "SIGKILL"), CANCEL_KILL_DELAY_MS).unref();
}

async function authStatus() {
  const { command, prefix } = claudeCommand();
  const output = await new Promise((resolve) => {
    execFile(
      command,
      [...prefix, "auth", "status"],
      { env: childEnv(), timeout: AUTH_STATUS_TIMEOUT_MS },
      (error, stdout, stderr) => resolve({ error, stdout, stderr }),
    );
  });
  let status;
  try {
    status = JSON.parse(output.stdout);
  } catch {
    status = { loggedIn: false, detail: (output.stderr || output.error?.message || "").slice(-500) };
  }
  return {
    billing_mode: billing(),
    logged_in: status.loggedIn,
    auth_method: status.authMethod,
    api_key_source: status.apiKeySource,
    detail: status.detail,
  };
}

const TOOLS = [
  {
    name: "run_claude_code",
    title: "Run Claude Code",
    description:
      "Run Claude Code as a subagent on a task, in its own context. Give it a self-contained prompt: it cannot see this conversation. Returns the result if it finishes within wait_seconds; otherwise returns a job_id to poll with get_claude_code_job while it keeps working. Each run costs the user money or subscription quota.",
    inputSchema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "The full task, including the context Claude Code needs." },
        cwd: { type: "string", description: "Absolute path of the directory to work in." },
        wait_seconds: {
          type: "number",
          description: `How long to wait for the result before returning a running job. Default ${DEFAULT_WAIT_SECONDS}, maximum ${WAIT_LIMIT_SECONDS}.`,
        },
        model: { type: "string", description: "Model alias such as sonnet or opus, or a full model name." },
        resume_session_id: { type: "string", description: "session_id of an earlier run to continue." },
        permission_mode: {
          type: "string",
          enum: ["default", "acceptEdits", "plan", "dontAsk"],
          description: "Default acceptEdits. Tools that would ask for permission are denied, because nobody can answer in a background run. Add them with allowed_tools.",
        },
        allowed_tools: {
          type: "array",
          items: { type: "string" },
          description: 'Tools to allow without asking, using Claude Code permission rules, for example "Bash(npm test:*)".',
        },
        disallowed_tools: { type: "array", items: { type: "string" }, description: "Tools to deny." },
        add_dirs: { type: "array", items: { type: "string" }, description: "Extra directories Claude Code may read and edit." },
        max_turns: { type: "integer", minimum: 1, description: "Stop after this many agent turns." },
        max_budget_usd: { type: "number", exclusiveMinimum: 0, description: "Stop once estimated API spend reaches this amount." },
      },
      required: ["prompt", "cwd"],
      additionalProperties: false,
    },
    annotations: { readOnlyHint: false, destructiveHint: true, openWorldHint: true },
    handler: async (input) => {
      const wait = clampWait(input.wait_seconds);
      const job = startJob(input);
      await waitFor(job, wait);
      return describeJob(job);
    },
  },
  {
    name: "get_claude_code_job",
    title: "Get Claude Code job",
    description: "Get a Claude Code job's progress or final result, waiting up to wait_seconds for it to finish.",
    inputSchema: {
      type: "object",
      properties: {
        job_id: { type: "string" },
        wait_seconds: { type: "number", description: `Default ${DEFAULT_WAIT_SECONDS}, maximum ${WAIT_LIMIT_SECONDS}. Use 0 to check without waiting.` },
      },
      required: ["job_id"],
      additionalProperties: false,
    },
    annotations: { readOnlyHint: true },
    handler: async ({ job_id, wait_seconds }) => {
      const wait = clampWait(wait_seconds);
      const job = getJob(job_id);
      await waitFor(job, wait);
      return describeJob(job);
    },
  },
  {
    name: "cancel_claude_code_job",
    title: "Cancel Claude Code job",
    description: "Stop a running Claude Code job.",
    inputSchema: {
      type: "object",
      properties: { job_id: { type: "string" } },
      required: ["job_id"],
      additionalProperties: false,
    },
    annotations: { destructiveHint: true },
    handler: async ({ job_id }) => {
      const job = getJob(job_id);
      stopJob(job);
      await waitFor(job, (CANCEL_KILL_DELAY_MS + 1000) / 1000);
      return describeJob(job);
    },
  },
  {
    name: "claude_code_auth_status",
    title: "Check Claude Code sign-in",
    description: "Check which Anthropic credential Claude Code will use on this machine: the API key or the subscription login. Returns no secrets.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    annotations: { readOnlyHint: true },
    handler: authStatus,
  },
];

async function handle(message) {
  const { method, params } = message;
  if (method === "initialize") {
    return {
      protocolVersion: params?.protocolVersion ?? PROTOCOL_VERSION,
      capabilities: { tools: {} },
      serverInfo: { name: "claude-code", version: "0.1.0" },
    };
  }
  if (method === "ping") return {};
  if (method === "tools/list") {
    return { tools: TOOLS.map(({ handler, ...tool }) => tool) };
  }
  if (method === "tools/call") {
    const tool = TOOLS.find(({ name }) => name === params?.name);
    if (!tool) throw Object.assign(new Error(`Unknown tool: ${params?.name}`), { code: -32602 });
    try {
      const result = await tool.handler(params.arguments ?? {});
      const failed = result.status === "failed";
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }], isError: failed };
    } catch (error) {
      return { content: [{ type: "text", text: error.message }], isError: true };
    }
  }
  throw Object.assign(new Error(`Method not found: ${method}`), { code: -32601 });
}

function send(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

function shutdown() {
  for (const job of jobs.values()) {
    if (job.status === "running") signalJob(job, "SIGTERM");
  }
  process.exit(0);
}

createInterface({ input: process.stdin })
  .on("line", (line) => {
    let message;
    try {
      message = JSON.parse(line);
    } catch {
      send({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } });
      return;
    }
    if (message.id === undefined) return;
    handle(message).then(
      (result) => send({ jsonrpc: "2.0", id: message.id, result }),
      (error) => send({ jsonrpc: "2.0", id: message.id, error: { code: error.code ?? -32603, message: error.message } }),
    );
  })
  .on("close", shutdown);
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
