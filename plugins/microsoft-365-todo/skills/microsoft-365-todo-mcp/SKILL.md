---
name: microsoft-365-todo-mcp
description: "Use the Microsoft 365 To Do MCP tools (todo_*) to browse task lists, read tasks, and create, update, complete or delete tasks. Invoke whenever a task involves the user's Microsoft To Do reminders or task lists: it gives exact tool signatures, the two IDs every task operation needs, the dateTimeTimeZone shape for due dates, paging rules, the confirm-before-write flow, and how to interpret confirmed / confirmed_but_unreadable / rejected / indeterminate results."
---

# Microsoft 365 To Do (MCP tools)

Connect to the To Do endpoint `/todo/mcp`. It exposes only `todo_*` tools — mail, calendar,
files, Teams and people lookups live behind separate endpoints.

## Choosing a tool

| You want to…                                       | Call                 |
| -------------------------------------------------- | -------------------- |
| Find which task lists exist (and their ids)        | `todo_lists`         |
| See the tasks in a list                            | `todo_list_tasks`    |
| Read one task in full                              | `todo_get_task`      |
| Add a reminder / task                              | `todo_create_task`   |
| Change title, body, due date, importance or status | `todo_update_task`   |
| Tick a task off                                    | `todo_complete_task` |
| Remove a task                                      | `todo_delete_task`   |

## Tool signatures

| Tool                                                                                                     | Notes                                                    |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `todo_lists(max_items=100, next_link?)`                                                                  | Lists with `id`, `display_name`, `wellknown_list_name`.  |
| `todo_list_tasks(list_id, max_items=100, next_link?)`                                                    | Tasks in one list.                                       |
| `todo_get_task(list_id, task_id)`                                                                        | One task.                                                |
| `todo_create_task(list_id, title, body?, due_date_time?, importance?, status?, confirm=false)`           | Creates only with `confirm=true`.                        |
| `todo_update_task(list_id, task_id, title?, body?, due_date_time?, importance?, status?, confirm=false)` | Patches only the fields you pass; at least one required. |
| `todo_complete_task(list_id, task_id, confirm=false)`                                                    | Sets status to `completed`.                              |
| `todo_delete_task(list_id, task_id, confirm=false)`                                                      | Deletes.                                                 |

Enumerations: `importance` ∈ `low`, `normal`, `high`. `status` ∈ `notStarted`, `inProgress`,
`completed`, `waitingOnOthers`, `deferred`.

Structured arguments:

- `due_date_time`: `{"date_time": "2026-09-03T17:00:00", "time_zone": "Europe/Madrid"}` — **both
  fields required**, `date_time` is a naive local timestamp (no `Z`, no offset).
- `body`: `{"content": "...", "content_type": "text"}` (or `"html"`) — both fields required.

## Discovering ids

**Every task operation needs two ids** and there is no "default list" shortcut:

1. `todo_lists` → pick the `list_id` (match on `display_name`; if several plausibly match, ask
   the user).
2. `todo_list_tasks(list_id)` → pick the `task_id`.

Never guess or reuse an id across lists.

## Reading and paging

- Lists return `{ "items": [...], "next": <cursor|null> }`. For more, repeat the call with
  `next_link` set to `next` **verbatim** and nothing else changed; never edit or build the URL.
  Only `next: null` means the collection is exhausted. `max_items` is 1–100 (default 100).
- Filter client-side on what the tools return; there is no server-side search over tasks.

## Writing: describe → approval → confirm

Every write takes `confirm` (default `false`).

1. Call it **without** `confirm`. Nothing is written; you get a bare `rejected` outcome with a
   `confirmation_required` error and **no preview body**.
2. Restate the change yourself — list name, title, due date with time zone, status — and get
   explicit user approval.
3. Re-run the **identical** call with `confirm: true`.

Read `status` on the result:

| `status`                   | Meaning                                              | Do                                                                                                                                |
| -------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `confirmed`                | It happened.                                         | Report success using `body` (contains the task id).                                                                               |
| `confirmed_but_unreadable` | **It happened**; only the response was unreadable.   | Treat as success. Do **not** retry. `todo_list_tasks` to recover the task.                                                        |
| `rejected`                 | Nothing happened (no `confirm`, or invalid request). | Fix the arguments and retry safely.                                                                                               |
| `indeterminate`            | It **may** have happened (timeout / server error).   | For `create_task`, **do not retry** — you would create a duplicate. `todo_list_tasks` first, then tell the user it is unverified. |

`todo_update_task`, `todo_complete_task` and `todo_delete_task` are idempotent enough to retry
once after you verify state; `todo_create_task` is not.

## Best practices

- Built-in lists (those whose `wellknown_list_name` is not `none`, e.g. `flaggedEmails`) have
  mutability limits. A write against them can fail with a hint to use a custom list — surface
  that hint to the user instead of retrying.
- Completing a task is `todo_complete_task`, not `todo_update_task` with a status string; use
  the dedicated tool.
- An empty patch (`update_task` with no field) returns `rejected` / `invalid_request`; there is
  no way to clear a field.
- State the time zone you used for a due date back to the user.
- Never paste the bearer token, and never quote raw Graph error bodies to the user.

## Examples

```jsonc
// Find the list, then the task
todo_lists { }
//  -> items: [{ "id": "AQMkAD...", "display_name": "Tasks", "wellknown_list_name": "defaultList" }]
todo_list_tasks { "list_id": "AQMkAD...", "max_items": 50 }
todo_list_tasks { "list_id": "AQMkAD...", "next_link": "https://graph.microsoft.com/v1.0/me/todo/lists/AQMkAD.../tasks?$skiptoken=..." }

// Add a task: describe, ask, confirm
todo_create_task {
  "list_id": "AQMkAD...", "title": "Send Q3 review",
  "due_date_time": { "date_time": "2026-09-03T17:00:00", "time_zone": "Europe/Madrid" },
  "importance": "high"
}
//  -> { "status": "rejected", ... confirmation_required }   nothing was created
todo_create_task { /* identical arguments */ "confirm": true }

// Tick it off later
todo_complete_task { "list_id": "AQMkAD...", "task_id": "AAMkAG...", "confirm": true }
```

## Not available — don't promise these

- Creating, renaming or deleting task **lists** (only tasks are writable).
- Recurrence, reminders, checklist steps, attachments, linked resources and categories.
- Searching or filtering tasks server-side; page and filter what you get.
- Shared or other users' task lists; only the signed-in user's To Do.

## When something fails

- **A tool is missing from `tools/list`** → the user's token lacks its scope. Reads need
  `Tasks.Read` (or `Tasks.ReadWrite`); every write needs `Tasks.ReadWrite`. Calling it anyway
  returns `insufficient_scope` with `required_scopes`; report it rather than working around it.
- **`401`** → the token is missing or expired; ask the caller for a fresh one.
- **429 / `retryable`** → wait `retry_after`, and retry reads only.
- **`invalid_graph_url`** → the `next_link` was altered; restart from the first page.
- **Validation errors** (missing `time_zone`, empty patch, bad enum value) mean nothing was
  written; fix the arguments.
- **Ambiguity** (two lists that could be "work") → ask the user before writing.

## Golden path

1. Check the tool is listed; if not, report the missing scope.
2. `todo_lists` → `list_id`; `todo_list_tasks` → `task_id`. Page with `next_link` verbatim.
3. Write without `confirm`, restate the change (list, title, due date + zone), get approval.
4. Repeat the identical call with `confirm: true`.
5. `confirmed` → done · `confirmed_but_unreadable` → done, no retry · `rejected` → nothing
   happened · `indeterminate` → list the tasks to verify, never blindly re-create.
6. Report the list, task id and due-date time zone you used.
