---
name: hex-to-canvas
description: Use Hex Threads through the Hex MCP search_projects/create_thread/get_thread/continue_thread tools to get concrete, canvas-ready metric values from Hex projects or dashboards, then build a Cursor canvas that can combine those figures with local repo, git, or other MCP context. Use when querying Hex for KPIs, data analysis, metrics, trends, dashboard values, or when blending Hex data with local information into a Cursor canvas or structured dashboard.
---

# Hex Thread to Cursor Canvas

Use this skill to turn a Hex Threads analysis into a Cursor canvas. Hex replies often start as narrative summaries, such as "trending up" or "in a 35-50% band", with charts that live inside Hex. A canvas needs exact values embedded inline, so ask for concrete numbers up front, verify them, and only then build the canvas.

## Workflow

1. **Authenticate if needed.** If the Hex MCP server is not authenticated, use Cursor's MCP authentication flow for the Hex server before invoking Hex tools.
2. **Find the right project or dashboard when relevant.** If the user refers to an existing Hex dashboard, report, project, or metric that "lives in Hex", call `search_projects` to locate it. If more than one result is plausible, ask the user to confirm before proceeding.
3. **Gather local context when relevant.** If the canvas should combine Hex data with local information, collect that context before prompting Hex. Useful sources include repository files, `git log`, feature flags, tickets, docs, or other MCP servers.
4. **Create the Hex thread.** Call `create_thread` with a prompt adapted from the canvas-ready template below.
5. **Poll for completion.** Call `get_thread` until the thread is idle or complete. Hex Threads can take several minutes; share the thread URL with the user when useful.
6. **Verify the numbers.** Confirm the response contains exact values, periods, source names, and numerator/denominator counts for rates. If anything is missing or only qualitative, call `continue_thread` for the specific missing values. Do not infer or fabricate.
7. **Build the canvas.** Create one `.canvas.tsx` file using the Cursor canvas APIs. Embed the verified values inline, and cite sources in captions: Hex thread URL, Hex project/dashboard title, source table/model name, as-of date, and any local file paths or commit SHAs used.

## Canvas-ready prompt template

Adapt this prompt when creating or continuing a thread:

```text
Give me the top KPIs for <topic> as concrete numbers I can put on a dashboard.
For each metric, return:
- Exact current value
- Period covered
- Numerator and denominator for any rate
- Recent-period versus prior-period comparison and delta
- Source table, model, or Hex project used
- As-of date
- Data-coverage caveats, including empty or future periods, timezone, and small samples

Return the results as:
1. A concise list of metric name + value + period.
2. A markdown table with metric, current value, prior value, delta, period,
   numerator, denominator, source, and caveats.
```

Why each clause matters:

- **Exact current value** blocks vague trend language.
- **Period covered** gives every canvas number a defensible time range.
- **Numerator and denominator** make rates auditable, for example `46.2% = 36 / 78`.
- **Recent versus prior comparison** gives a real MoM, QoQ, or other period-over-period stat instead of an eyeballed trend.
- **Source table, model, or Hex project** belongs in the canvas caption.
- **Caveats** prevent incomplete or noisy data from being presented as settled fact.

## Pull from existing Hex dashboards

Hex Threads can read the data behind projects and dashboards that already exist in the workspace. Use this when the user wants the latest values from an existing Hex artifact instead of a new analysis.

1. Call `search_projects` with the dashboard, project, metric, or topic name.
2. Review candidate results using their `title`, `description`, `generated_summary`, `url`, or `appUrl`.
3. Ask the user to choose if multiple candidates are plausible.
4. Name the selected project explicitly in the `create_thread` prompt:

```text
Using the data behind the Hex project "<project title>", give me the latest
values for <metrics>. Return exact current values, the period each covers,
the numerator and denominator behind any rate, the source table/model, caveats,
and the as-of date.
```

5. Treat returned figures as point-in-time. Include the as-of date and Hex project link in the canvas caption.

## Combine with local information

When the canvas should blend Hex data with local repo or external context:

- Collect local context before creating the thread so the Hex prompt can ask for values that line up with the canvas story.
- Keep Hex-sourced values separate from locally derived values in your notes until final assembly.
- Cite local sources with file paths, line references when available, branch names, commit SHAs, or MCP result links.
- If local context changes the interpretation of a Hex metric, explain that in a `Callout` or short narrative card rather than modifying the Hex number.

## Data-coverage caveats to preserve

Carry caveats from Hex into the canvas honestly:

- **Empty or future periods.** Use the latest complete period with data and label it clearly.
- **Timezone.** Note the project timezone, especially for daily, weekly, or monthly windows.
- **Small-sample noise.** Flag low-count periods instead of presenting swings as durable trends.
- **Lower-volume upticks.** A favorable delta on much lower volume should be labeled preliminary.
- **Definition changes.** If the metric definition, table, filter, or cohort changed, include that in the caption or notes.

## Mapping Hex output to canvas components

- Headline metrics -> `Stat` components in a `Grid`.
- Good or bad movement -> `tone="success"` or `tone="danger"` when the direction is unambiguous.
- Two-part splits, such as wins/losses or pass/fail -> donut-style `PieChart`.
- Period-over-period or category comparisons -> `BarChart` with `valueSuffix` and visible values.
- Full metric list with periods and sources -> `Table` with numeric columns right-aligned.
- Narrative recommendations -> short `Card` components and a `Callout tone="info"` takeaway.
- Source and caveat details -> captions or a compact methodology card.

## Rules

- **Never invent numbers.** If a value is not in the Hex thread response, ask for it with `continue_thread` or omit that canvas element.
- **Do not build from qualitative summaries alone.** Terms like "up", "down", "strong", "weak", "roughly", or "about" are not canvas-ready unless paired with exact values and periods.
- **Keep caveats visible.** Do not present preliminary, sparse, future-period, or timezone-sensitive data as settled.
- **Use one canvas file.** Build a single `.canvas.tsx` file and import only from `cursor/canvas`.
- **Keep data lineage clear.** Each chart, stat, or table must have enough caption/source context for a reviewer to trace the number back to Hex or local context.

## Expected Tools

The Hex app currently exposes tools such as `search_projects`, `create_thread`, `get_thread`, and `continue_thread`. Canvas construction should use Cursor canvas APIs and follow any available canvas-specific skill or project guidance. Tool availability can vary by workspace permissions and server-side rollout state.

## Common Triggers

- "Build a canvas from this Hex dashboard."
- "Use Hex Agent to get exact KPI values for a Cursor canvas."
- "Pull the latest metrics from Hex and combine them with this branch."
- "Turn this Hex Thread into a dashboard."
- "Make a canvas with Hex numbers, sources, and caveats."
