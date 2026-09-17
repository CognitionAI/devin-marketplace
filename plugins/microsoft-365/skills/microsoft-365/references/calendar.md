# Microsoft 365 Calendar (MCP tools)

Connect to the calendar endpoint `/calendar/mcp`. It exposes only `calendar_*` tools — mail,
files, Teams, tasks and people lookups live behind separate endpoints.

## Choosing a tool

| You want to…                                | Call                    |
| ------------------------------------------- | ----------------------- |
| See what is on the calendar in a period     | `calendar_list_events`  |
| Read one event's details                    | `calendar_get_event`    |
| Book a meeting or block time                | `calendar_create_event` |
| Change time, subject, location or attendees | `calendar_update_event` |
| Cancel / remove an event                    | `calendar_delete_event` |

## Tool signatures

| Tool                                                                                                                                                                                       | Notes                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `calendar_list_events(start, end, limit?, cursor?)`                                                                                                                                        | ISO 8601 `start` (inclusive) / `end` (exclusive). Recurring series are expanded into occurrences; times come back in **UTC**. |
| `calendar_get_event(event_id)`                                                                                                                                                             | One event.                                                                                                                    |
| `calendar_create_event(subject, start, end, body?, body_html=false, location?, attendees?, is_all_day?, is_reminder_on?, reminder_minutes_before_start?, show_as?, confirm=false)`         | **With attendees this sends invitations.**                                                                                    |
| `calendar_update_event(event_id, subject?, start?, end?, body?, body_html?, location?, attendees?, is_all_day?, is_reminder_on?, reminder_minutes_before_start?, show_as?, confirm=false)` | Omitted properties are untouched; at least one change required.                                                               |
| `calendar_delete_event(event_id, confirm=false)`                                                                                                                                           | For a meeting this **cancels it for every attendee**.                                                                         |

## Times and time zones (get this right)

- Write times are `{"date_time": "2026-09-02T10:00:00", "time_zone": "Europe/Madrid"}`: a
  **naive local timestamp** plus an IANA or Windows zone. No `Z` and no offset inside
  `date_time`. Omitting `time_zone` means UTC. An ISO 8601 string with an explicit offset
  (`"2026-09-02T10:00:00Z"`) is accepted too and read as that UTC instant; a string without
  an offset is rejected rather than guessed.
- `list_events` `start`/`end` are plain ISO 8601 instants (`"2026-09-01T00:00:00Z"`), and
  returned event times are UTC — convert before showing them to the user.
- Always tell the user which time zone you used when you book something.
- All-day events: set `is_all_day: true` with midnight-to-midnight local times.

## Discovering ids

- Event id → `calendar_list_events` over the relevant range (or `calendar_get_event` if you
  already have one). Never guess an id.
- Attendee addresses → use what the user gave you. If you had to infer who a person is, confirm
  with the user first; you can optionally resolve them with the Directory MCP
  (`directory_search_users`) if that endpoint is also connected.

## Reading and paging

- Always pass a real range; do not sweep a whole calendar to find one meeting.
- Lists return `{ "items": [...], "next": <cursor|null> }`. For more, repeat the call with
  `cursor` set to `next` **verbatim**, changing nothing else. Never edit or build a cursor URL.
  Only `next: null` means the range is exhausted. `limit` defaults to 25, max 200.
- Results are narrow projections; use the fields returned.

## Writing: preview → approval → confirm

Every write takes `confirm` (default `false`).

1. Call it **without** `confirm`. Nothing reaches the calendar; you get `rejected` with a
   `confirmation_required` error. There is no rich preview body here — restate the change
   yourself: subject, start/end with time zone, attendees, location.
2. Get explicit approval. This matters more here than anywhere else: creating or updating an
   event with attendees **emails invitations**, and deleting a meeting **cancels it for all
   attendees**.
3. Re-run the **identical** call with `confirm: true`.

Read `status` on the result:

| `status`                   | Meaning                                              | Do                                                                                                                     |
| -------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `confirmed`                | It happened.                                         | Report success using `body` (contains the event id).                                                                   |
| `confirmed_but_unreadable` | **It happened**; only the response was unreadable.   | Treat as success. Do **not** retry. `calendar_list_events` to recover the event.                                       |
| `rejected`                 | Nothing happened (no `confirm`, or invalid request). | Fix the arguments and retry safely.                                                                                    |
| `indeterminate`            | It **may** have happened (timeout / server error).   | **Do not re-create the event** — you would duplicate invitations. List the range, then tell the user it is unverified. |

`calendar_delete_event` may be retried once after verifying state. `calendar_create_event` must
never be blindly retried.

## Best practices

- `attendees` is a list of
  `{"address": "ana@contoso.com", "name"?: "Ana", "kind": "required"|"optional"|"resource"}`;
  `kind` defaults to `required`.
- `update_event` **replaces** the attendee list you send — include everyone who should stay.
- A patch that changes `attendees` together with the reminder properties is sent as two
  sequential requests (everything else first, attendees second). If the first succeeds and
  the second does not, the result is `indeterminate` **with a `partial` object**:
  `partial.confirmed_fields` (already applied, e.g. `["subject", "is_reminder_on"]`),
  `partial.unconfirmed_fields` (always `["attendees"]`) and `partial.unconfirmed_status`
  (`rejected` = Graph refused the attendee change, safe to fix and resend **only the
  attendees**; `indeterminate` = unknown, re-read the event first). Nothing is rolled back:
  do not re-send the confirmed fields, and tell the user exactly which part is unverified.
- `show_as` ∈ `free`, `tentative`, `busy`, `oof`, `workingElsewhere`, `unknown`.
- `update_event` with nothing to change returns `rejected` / `invalid_request`; there is no way
  to clear a property.
- `body_html: true` sends the body as HTML; otherwise plain text.
- Never paste the bearer token, and never quote raw Graph error bodies to the user.

## Examples

```jsonc
// What does next week look like?
calendar_list_events { "start": "2026-09-01T00:00:00Z", "end": "2026-09-08T00:00:00Z" }

// Book a meeting: preview, ask, confirm
calendar_create_event {
  "subject": "Design sync",
  "start": { "date_time": "2026-09-02T10:00:00", "time_zone": "Europe/Madrid" },
  "end":   { "date_time": "2026-09-02T10:30:00", "time_zone": "Europe/Madrid" },
  "attendees": [{ "address": "ana@contoso.com", "kind": "required" }]
}
//  -> { "status": "rejected", ... confirmation_required }   nothing was created, no invites
calendar_create_event { /* identical arguments */ "confirm": true }
//  -> { "status": "confirmed", "body": { "id": "AAMk...", ... } }

// Move it 30 minutes later
calendar_update_event {
  "event_id": "AAMk...",
  "start": { "date_time": "2026-09-02T10:30:00", "time_zone": "Europe/Madrid" },
  "end":   { "date_time": "2026-09-02T11:00:00", "time_zone": "Europe/Madrid" },
  "confirm": true
}
```

## Not available — don't promise these

- Free/busy lookup or meeting-time suggestions.
- Responding to invitations (accept / decline / tentative).
- Creating or editing recurrence patterns — series are expanded on read, but writes are
  single-instance only.
- Other people's, shared or group calendars; only the signed-in user's default calendar.
- Attachments and Teams online-meeting links.

## When something fails

- **A tool is missing from `tools/list`** → the user's token lacks its scope. Reads need
  `Calendars.ReadBasic` (or `Calendars.Read`); every write needs `Calendars.ReadWrite`. Calling
  it anyway returns `insufficient_scope` with `required_scopes`; report it instead of looking
  for a workaround.
- **`401`** → the token is missing or expired; ask the caller for a fresh one.
- **429 / `retryable`** → wait `retry_after`, and retry reads only.
- **`invalid_graph_url`** → the cursor was altered; restart from the first page.
- **Validation errors** (bad range, empty patch) mean nothing was sent; fix the arguments.
- **Ambiguity** (which "Ana", which of two similar meetings) → ask the user before writing.

## Golden path

1. Check the tool is listed; if not, report the missing scope.
2. `calendar_list_events` over an explicit range to find the event id; page with `cursor`
   verbatim.
3. Write without `confirm`, restate subject / time + zone / attendees, get approval.
4. Repeat the identical call with `confirm: true`.
5. `confirmed` → done · `confirmed_but_unreadable` → done, no retry · `rejected` → nothing
   happened · `indeterminate` → verify by listing the range, never re-create.
6. Report the event id and the time zone you used.
