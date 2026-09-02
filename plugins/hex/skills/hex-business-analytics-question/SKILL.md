---
name: hex-business-analytics-question
description: Use when the user asks a business analytics question that may already be answered in Hex projects, dashboards, apps, or Hex Agent threads.
---

# Hex Business Analytics Question

Use this skill when the user asks a business analytics question and wants an answer from Hex context. The goal is to search existing Hex work first, answer from known project context when possible, and only start a Hex Agent thread when search cannot fully satisfy the question.

## Workflow

1. Restate the analytical question in concrete business terms if needed, including metric, dimension, timeframe, segment, and grain.
2. Search existing Hex projects before starting new analysis:
   - Use `search_projects` with the user's terms, likely synonyms, metric names, dashboard names, table names, or business domain terms.
   - Prefer existing projects, dashboards, and apps that appear maintained, relevant, and close to the user's question.
3. Evaluate search results:
   - If an existing project directly answers the question, summarize the answer and cite the relevant project context.
   - If a project is relevant but incomplete, explain what it covers and what remains unanswered.
   - If search results are weak or conflicting, say so plainly.
4. Start a Hex Agent thread only when search cannot fully answer the question:
   - Use `create_thread` with the business question, relevant project context, and any constraints discovered from search.
   - Tell the user the thread may take a few minutes.
   - Use `get_thread` to poll until the result is useful or complete.
5. Continue an existing thread only after it is idle and the user asks a follow-up. Use `continue_thread` with the follow-up and preserve prior context.
6. Return a concise answer with confidence, caveats, source projects or thread links when available, and recommended follow-up analysis when useful.

## Answering Rules

- Search before creating a new thread.
- Do not present a thread result as definitive if it depends on incomplete context, stale projects, missing permissions, or unresolved assumptions.
- Distinguish existing Hex project findings from new Hex Agent analysis.
- Prefer business-language answers over implementation details, but include metric definitions, filters, and timeframe when they affect interpretation.
- Do not fabricate data, project titles, owners, URLs, or thread status.
- If auth, workspace permissions, Magic enablement, or AI credits block a tool call, explain the blocker and what the user needs to configure.

## Expected Tools

The Hex app currently exposes tools such as `search_projects`, `create_thread`, `get_thread`, and `continue_thread`. Tool availability can vary by workspace permissions and server-side rollout state.

## Common Triggers

- "What drove the drop in conversion last week?"
- "Do we already have a Hex dashboard for ARR by segment?"
- "Answer this using Hex."
- "Search Hex before doing new analysis."
- "Ask Hex Agent if existing projects do not answer it."
