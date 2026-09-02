---
name: investigate-bug
description: Structured workflow for analyzing a Jam bug report end-to-end — pulls diagnostics from the Jam MCP server (console, network, user events, screenshots, video frames, transcript) and produces a root-cause hypothesis. Invoke with `/investigate-bug <jam-url-or-id>`.
---

# Investigate Bug

A structured workflow for investigating Jam bug reports. Invoke with `/investigate-bug <jam-url-or-id>`.

## Workflow

### Step 1: Get the Bug Report

Call `getDetails` with the provided Jam URL or ID. A full `https://jam.dev/c/...` URL or a UUID both work.

From the response, extract:
- **Description** — what the reporter said
- **Type** — `video`, `screenshot`, or `replay`
- **Device info** — browser, OS, screen size
- **Investigation Guide** — server-recommended next steps, returned as the second text block
- **Postprocessing status** — for fresh Jams, some event-backed tools may report "not ready yet"

### Step 2: Follow the Investigation Guide

The `getDetails` response includes an Investigation Guide built from real signals in the Jam (console error counts, 4xx/5xx ranges per host, mic enabled, etc.). **Treat it as authoritative** — the steps below are fallbacks for when the guide is light or you want to drill deeper.

- Each path specifies a **tool** to call, suggested **arguments**, and **what to look for**.
- Investigate `high` priority paths first; defer `medium` until they're exhausted.
- For video Jams where the reporter had the mic on, `getVideoTranscript` is now prioritized **above** `analyzeVideo` — voiceover is the cheapest, most direct signal.

### Step 3: Analyze Network Activity

Call `getNetworkRequests` with filters to focus on problems:
- `statusCode: "5xx"` for server failures, `"4xx"` for client errors
- `host: "api.example.com"` to scope to a specific backend
- `method: "POST"` for mutation failures
- `limit` to cap output when a Jam is noisy

Note CORS errors, timeouts, and unexpected response shapes.

### Step 4: Check Console Errors

Call `getConsoleLogs` with `logLevel: "error"` to find runtime errors.
- Look for unhandled exceptions, failed assertions, and stack traces.
- Cross-reference timestamps with network errors and user events.
- **Silent failure check:** if network shows 4xx/5xx but console is clean, the app may be swallowing errors — re-run with no `logLevel` filter.

### Step 5: Review User Events

Call `getUserEvents` to understand the sequence of interactions.
- Identify the exact action that triggered the bug.
- Note any unexpected navigation or repeated actions (signs of user confusion).

### Step 6: Analyze Visual Evidence

Based on the Jam type from `getDetails`:
- **Screenshot Jams** — call `getScreenshots` to examine visual state.
- **Video Jams** — call `getFrames` with `overview: true` first: it returns a single timestamp-labeled grid of frames spanning the whole recording, the fastest way to see what happened on screen. Then sample around the failure with `at: [<ms>, ...]` or a `fromMs`/`toMs` window (max 30 frames per call; `size` controls resolution).
- **Video Jams with mic** — also call `getVideoTranscript` (cheap, fast — the reporter's narration captures intent directly). If you need richer context, call `analyzeVideo` for extracted intents.
- **Video Jams without mic** — use `getFrames` plus `analyzeVideo`.
- `analyzeVideo` and `getFrames` short-circuit on non-video Jams, so always check the type first.

### Step 7: Check Custom Metadata

Call `getMetadata` to retrieve any app-specific context (user IDs, feature flags, app version) that the application set via the `jam.metadata()` SDK.

### Step 8: Produce Diagnosis

Compile findings into a structured report:

```
## Bug Report Analysis

### Summary
[One-sentence description of the issue]

### What Happened
[Sequence of events from user's perspective]

### Root Cause Hypothesis
[Most likely technical cause based on evidence]

### Supporting Evidence
- [Network error / console error / user event that supports the hypothesis]
- [Additional data points]

### Recommended Next Steps
1. [Specific action to fix or further investigate]
2. [Additional actions]
```

## Tips

- Not all steps are needed for every bug. If the Investigation Guide from Step 2 gives you enough signal, skip straight to the diagnosis.
- Use `listJams` to search for similar reports if the bug might be a recurring issue. Filter by `url`, `author`, or `createdAt` (supports ISO 8601 durations like `-P7D` for "last 7 days").
- Add your findings back to the Jam with `createComment` (Markdown supported) so the team sees them. Pass `playbackRelativeTimestamp` to pin a comment to a specific moment in a video or replay.
- If a fresh Jam's event tools return "not ready yet," the Jam is still being processed — wait a few seconds and retry, or fall back to data that's already available.
