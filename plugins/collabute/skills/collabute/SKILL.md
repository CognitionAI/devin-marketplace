---
name: collabute
description: Use Collabute's MCP tools to ground work in what the team already decided — meeting transcripts, team memory, Slack threads, and the issues, pull requests, deployments, and docs in the workspace's connected integrations — and to propose follow-up tasks or memory updates for a human to approve. Use when a task references a meeting, a decision, "what we agreed", a customer call, or team context that isn't in the repository.
---

# Collabute

Collabute is an AI teammate that remembers a team's meetings, decisions, and
conversations. Its MCP server exposes that memory and the workspace's connected
integrations. Every call runs in the signed-in user's active Collabute
workspace with the scopes they approved.

## Find context before acting

1. `memory.search` for decisions, history, and "why" questions. Start here when
   a task mentions something the team discussed.
2. `memory.get_bundle` to assemble a compact, cited context pack once you know
   what you need.
3. `meeting.list_recent`, then `meeting.get` / `meeting.get_transcript` when the
   user points at a specific meeting or call. Quote the transcript instead of
   paraphrasing when the exact wording matters.
4. Integration tools (`linear.*`, `jira.*`, `github.*`, `vercel.*`,
   `posthog.*`, `notion.*`, `gmail.*`, `slack.*`, `calendar.*`) only work for
   integrations the workspace has connected in Collabute. If one returns a
   not-connected error, tell the user to connect it in Collabute rather than
   retrying.

`system.ping` checks the connection and which workspace you are in.

## Changes are proposals

Tools named `*.propose_*` (`memory.propose_write`,
`meeting.propose_task_from_meeting`, `integration.propose_action`,
`coding.propose_implementation`, `github.propose_action`) do not change
anything directly. They create a pending proposal that a teammate approves or
rejects in Collabute. After calling one, tell the user a proposal is waiting
for approval in Collabute; do not describe the change as done.

Direct writes are limited to `calendar.create_event` / `calendar.update_event`,
`notion.create_page` / `notion.append_to_page` /
`notion.update_page_properties`, and `meeting.delete`. Confirm with the user
before calling them, and never call `meeting.delete` unless they asked for it.

## Good habits

- Cite where context came from (meeting title and date, Slack thread, issue
  key) so the user can check it.
- Prefer one targeted `memory.search` over many broad ones.
- For coding proposals, pass the repository as `owner/name`; never guess it.
