---
name: microsoft-365-mail-mcp
description: "Use the Microsoft 365 Mail MCP tools (mail_*) to read Outlook mail, browse folders, send mail, create drafts, archive/move/mark messages, and manage personal contacts. Invoke whenever a task involves the user's mailbox or contacts: it gives exact tool signatures and arguments, how to discover folder/message/contact IDs, paging rules, the preview-then-confirm flow required for every write, and how to interpret confirmed / confirmed_but_unreadable / rejected / indeterminate results."
---

# Microsoft 365 Mail (MCP tools)

Connect to the mail endpoint `/mail/mcp`. It exposes only `mail_*` tools — calendar, files,
Teams, tasks and people lookups live behind separate endpoints.

## Choosing a tool

| You want to…                                    | Call                                          |
| ----------------------------------------------- | --------------------------------------------- |
| See recent or unread messages                   | `mail_list`                                   |
| Read a message body                             | `mail_get`                                    |
| Find a folder id                                | `mail_folders`                                |
| Send a message now                              | `mail_send_mail`                              |
| Leave a message for the user to send themselves | `mail_create_draft`                           |
| Tidy the inbox                                  | `mail_archive`, `mail_move`, `mail_mark_read` |
| Look up / edit the user's personal contacts     | `mail_contacts_*`                             |

## Tool signatures

| Tool                                                                                                                                       | Notes                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `mail_list(folder_id?, search?, unread_only=false, limit?, cursor?)`                                                                       | One page, newest first. `search` and `unread_only` cannot be combined. |
| `mail_get(message_id)`                                                                                                                     | Full message including body.                                           |
| `mail_folders(limit?, cursor?)`                                                                                                            | Folder ids, display names, unread counts.                              |
| `mail_send_mail(subject, body, to[], body_type="Text"\|"HTML", cc?, bcc?, save_to_sent_items=true, confirm=false)`                         | Sends only with `confirm=true`.                                        |
| `mail_create_draft(subject, body, to[], body_type?, cc?, bcc?, confirm=false)`                                                             | Creates a draft; it is never sent.                                     |
| `mail_archive(message_id, confirm=false)`                                                                                                  | Moves to the well-known archive folder.                                |
| `mail_move(message_id, destination_id, confirm=false)`                                                                                     | `destination_id` comes from `mail_folders`.                            |
| `mail_mark_read(message_id, confirm=false)`                                                                                                | Marks read.                                                            |
| `mail_contacts_list(email_address?, limit?, cursor?)`                                                                                      | Filter is an **exact** address match, not a name search.               |
| `mail_contacts_get(contact_id)`                                                                                                            | One contact.                                                           |
| `mail_contacts_create(given_name?, surname?, email_addresses?, business_phones?, mobile_phone?, job_title?, company_name?, confirm=false)` | At least one field required.                                           |
| `mail_contacts_update(contact_id, ...same fields, confirm=false)`                                                                          | Omitted fields stay unchanged; an empty patch is rejected.             |
| `mail_contacts_delete(contact_id, confirm=false)`                                                                                          | Deletes.                                                               |

## Discovering ids

- Folder id → `mail_folders`, then pass it as `folder_id` / `destination_id`. Never invent one;
  for archiving prefer `mail_archive` over `mail_move` with a guessed id.
- Message id → `mail_list` or `mail_get`. Ids are immutable, so they stay valid after a move.
- Contact id → `mail_contacts_list`.

## Reading and paging

- Always narrow the read: a `folder_id`, a `search` term, or `unread_only: true`. Do not page
  through a mailbox hunting for something.
- `search` + `unread_only` together raises an error; pick one. `search` also drops the
  newest-first ordering.
- Every list returns `{ "items": [...], "next": <cursor|null> }`. To get more, call the same
  tool with `cursor` set to `next` **verbatim** and no other arguments changed. Never edit or
  build a cursor URL yourself. A short page does not mean the end — only `next: null` does.
  `limit` defaults to 25, max 200.
- Results are narrow projections; use the fields returned rather than assuming Graph extras.

## Writing: preview → approval → confirm

Every write takes `confirm` (default `false`).

1. Call it **without** `confirm`. Nothing is sent; you get a non-PII preview (counts and
   lengths, e.g. `{"to_count": 1, "body_length": 15}`).
2. Show the user what will happen — recipients, subject, folder — and get explicit approval.
3. Re-run the **identical** call with `confirm: true`.

Read `status` on the result:

| `status`                   | Meaning                                              | Do                                                                                                       |
| -------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `confirmed`                | It happened.                                         | Report success using `body`.                                                                             |
| `confirmed_but_unreadable` | **It happened**; only the response was unreadable.   | Treat as success. Do **not** retry. Read back if you need details.                                       |
| `rejected`                 | Nothing happened (no `confirm`, or invalid request). | Fix the arguments and retry safely.                                                                      |
| `indeterminate`            | It **may** have happened (timeout / server error).   | **Do not resend.** Check Sent Items or the folder with `mail_list`, then tell the user it is unverified. |

`mail_mark_read`, `mail_archive` and `mail_move` may be retried once after you verify state.
`mail_send_mail` and `mail_create_draft` must never be blindly retried.

## Best practices

- **There is no `mail_send_draft`.** Sending and drafting are separate: if the user wants to
  review before sending, `mail_create_draft` and tell them to send it from Outlook. Never create
  a draft and then also `mail_send_mail` the same content — that leaves two artifacts.
- `mail_send_mail` returns `{recipient_count, saved_to_sent_items}`, not the message; use
  `mail_list` on Sent Items if you need the sent item itself.
- Confirm inferred addresses with the user before sending. `mail_contacts_list` matches an
  address exactly and cannot search by name.
- `body_type` is `"Text"` (default) or `"HTML"`. Markdown is not rendered.
- Never paste the bearer token, and never quote raw Graph error bodies to the user.

## Examples

```jsonc
// Read unread inbox mail, then page
mail_folders { }
mail_list { "folder_id": "AAMk...Inbox", "unread_only": true, "limit": 25 }
mail_list { "cursor": "https://graph.microsoft.com/v1.0/me/messages?$skiptoken=..." }

// Send: preview, ask, then confirm
mail_send_mail { "subject": "Q3 review", "body": "Notes attached.", "to": ["ana@contoso.com"] }
//  -> { "status": "rejected", "body": { "to_count": 1, "body_length": 15 } }   nothing sent
mail_send_mail { "subject": "Q3 review", "body": "Notes attached.", "to": ["ana@contoso.com"], "confirm": true }
//  -> { "status": "confirmed", "body": { "recipient_count": 1, "saved_to_sent_items": true } }

// Tidy up
mail_archive { "message_id": "AAMk...", "confirm": true }
```

## Not available — don't promise these

- Sending an existing draft (`mail_send_draft` does not exist).
- Reply / reply-all / forward tools — compose a new message instead.
- Attachments (adding, reading or downloading them).
- Rules, categories, and shared or delegated mailboxes; only the signed-in user's mailbox.

## When something fails

- **A tool is missing from `tools/list`** → the user's token lacks its scope. Tell them which to
  add: `Mail.Read` (read messages), `Mail.ReadBasic` (folders), `Mail.Send` (send),
  `Mail.ReadWrite` (draft/move/archive/mark read), `Contacts.Read` / `Contacts.ReadWrite`
  (contacts). Calling it anyway returns `insufficient_scope` with `required_scopes`; do not look
  for a workaround.
- **`401`** → the token is missing or expired; ask the caller for a fresh one.
- **429 / `retryable`** → wait `retry_after` before retrying, and retry reads only.
- **`invalid_graph_url`** → the cursor was altered; restart from the first page.
- **Validation errors** (`search` + `unread_only`, empty contact fields, empty patch) mean
  nothing was sent; fix the arguments.
- **Ambiguity** (several plausible recipients, unclear folder) → ask the user before writing.

## Golden path

1. Check the tool is listed; if not, report the missing scope.
2. Resolve ids (`mail_folders`, `mail_list`, `mail_contacts_list`) — never guess.
3. Read with explicit filters; page with `cursor` verbatim.
4. Write without `confirm`, show the preview, get approval.
5. Repeat the identical call with `confirm: true`.
6. `confirmed` → done · `confirmed_but_unreadable` → done, no retry · `rejected` → nothing
   happened · `indeterminate` → verify by reading back, never resend.
7. Report the recipients, folder and ids you actually used.
