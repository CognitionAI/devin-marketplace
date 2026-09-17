---
name: microsoft-365
description: "Use the Microsoft 365 MCP tools whenever a task involves the user's Outlook mail or contacts, calendar, To Do tasks, OneDrive/SharePoint files, Teams chats/channels, or directory/people lookups. Six workload-scoped MCP servers (mail, calendar, todo, files, teams, directory) each expose only their own tools; this skill tells you which server to use and points at per-workload references with exact tool signatures, the preview-then-confirm write flow, paging rules, and the Graph scope to report when a call fails on permissions."
---

# Microsoft 365 (MCP tools)

Six Cognition-hosted MCP servers cover Microsoft 365 via the Microsoft Graph API. Each server
exposes **only its own workload's tools**, so pick the server that matches the task and read its
reference file before calling tools.

| Workload                        | MCP server               | Endpoint path        | Tool prefix      | Reference                          |
| ------------------------------- | ------------------------ | -------------------- | ---------------- | ---------------------------------- |
| Outlook mail & contacts         | `microsoft-365-mail`      | `/mail/mcp`          | `mail_`          | [references/mail.md](references/mail.md)           |
| Calendar & meetings             | `microsoft-365-calendar`  | `/calendar/mcp`      | `calendar_`      | [references/calendar.md](references/calendar.md)   |
| To Do tasks                     | `microsoft-365-todo`      | `/todo/mcp`          | `todo_`          | [references/todo.md](references/todo.md)           |
| OneDrive & SharePoint files     | `microsoft-365-files`     | `/files/mcp`         | `files_`         | [references/files.md](references/files.md)         |
| Teams, channels & chats         | `microsoft-365-teams`     | `/collaboration/mcp` | `collaboration_` | [references/teams.md](references/teams.md)         |
| Directory & people (read-only)  | `microsoft-365-directory` | `/directory/mcp`     | `directory_`     | [references/directory.md](references/directory.md) |

## Rules that apply to every workload

- **Writes are preview → approval → confirm.** Every side-effecting tool takes
  `confirm` (default `false`). Call it without `confirm` first — nothing is written — show the
  user what will happen, then re-run the *identical* call with `confirm: true`. Never pass
  `confirm: true` on a call the user has not seen and approved.
- **Read the write outcome, don't assume.** Results are `confirmed` (it happened),
  `confirmed_but_unreadable` (it happened; treat as success, do not retry — read back if you
  need details), `rejected` (nothing happened — no `confirm` or invalid request; fix args and
  retry safely), or `indeterminate` (it may have happened — **do not resend**; verify with a
  read and tell the user it is unverified).
- **Page with cursors.** List tools return `{ "items": [...], "next": <cursor|null> }`. To get
  more, call the same tool with `cursor` set to `next` verbatim and no other arguments changed.
  Never edit or build a cursor URL yourself; a short page does not mean the end — only
  `next: null` does.
- **Discover IDs before acting.** Folder, message, event, task, chat, channel and file IDs come
  from the workload's list/search tools — never invent them. For people, prefer directory
  lookups over guessing addresses.
- **Missing tools mean missing scopes.** `tools/list` hides tools the user's token can't call;
  calling one anyway returns `insufficient_scope` with `required_scopes`. Report the missing
  Microsoft Graph scope to the user (each reference lists them) instead of retrying or working
  around it.

## Setup and auth

Each server signs in with the member's **own Microsoft Entra app registration** — the client ID
and secret are entered in Devin's MCP settings when installing the server, and the app must have
the delegated Graph permissions listed in the workload's reference. If a tool fails with an
auth/permission error, tell the user which Graph scope is missing rather than retrying.
