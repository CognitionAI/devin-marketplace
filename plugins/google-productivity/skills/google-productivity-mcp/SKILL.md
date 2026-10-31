---
name: google-productivity-mcp
description: "Use the Google MCP tools to search and read Gmail, draft/reply/forward and send email, manage labels and attachments, list and create/update/delete Google Calendar events, RSVP and find meeting times, and search Google Contacts. Invoke whenever a task involves the user's Gmail, Google Calendar or Google Contacts: it gives exact tool signatures, how to discover message/draft/event/label IDs, which OAuth permission each tool needs, and the draft-then-send flow required for every email."
---

# Google (Gmail, Calendar, Contacts MCP tools)

Connect to `https://google-mcp.devin.ai/mcp`. One endpoint serves Gmail, Google Calendar and
Google Contacts; each tool only appears when the user granted the matching permission when
they installed the plugin (see "Permissions" below). A tool you expect but cannot see means the
user did not grant that permission: tell them which one is missing instead of working around it.

## Choosing a tool

| You want to…                                        | Call                                                     |
| --------------------------------------------------- | -------------------------------------------------------- |
| Find mail                                           | `search_emails` (Gmail search syntax)                    |
| Read a message, its thread id and attachment ids    | `read_email`                                             |
| Download an attachment                              | `get_attachment`                                         |
| Write a new email                                   | `compose_draft`, then `send_draft`                       |
| Reply or forward                                    | `draft_reply` / `draft_forward`, then `send_draft`       |
| Change a pending draft                              | `update_draft`; inspect with `get_draft`, `list_drafts`  |
| Drop a draft                                        | `discard_draft`                                          |
| Clean up the inbox                                  | `archive_email` (default), `trash_email` (only on request) |
| Label / mark read / star                            | `label_email`; ids from `list_labels`, `create_label`    |
| Which "from" addresses the user may send as         | `get_aliases`                                            |
| See the user's calendars                            | `list_calendars`                                         |
| See what is on the calendar                         | `list_events`                                            |
| Find a slot that works for several people           | `suggest_time`                                           |
| Create / change / delete a meeting                  | `create_event`, `update_event`, `delete_event`           |
| Change one occurrence of a recurring event          | `update_occurrence`                                      |
| Accept / decline an invitation the user received    | `rsvp_event`                                             |
| Look up a person's email address                    | `search_contacts`                                        |

## Tool signatures

`?` marks optional arguments.

### Gmail

| Tool                                                                                                                      | Notes                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_emails(query, maxResults?, pageToken?)`                                                                           | Native Gmail search (`from:`, `subject:`, `is:unread`, `has:attachment`, `after:2024/01/01`, `in:sent`). Covers all time by default; add date operators only when the user asked for a time range. Returns previews with `messageId`s. |
| `read_email(messageId)`                                                                                                   | Headers, `threadId`, `labelIds`, body as Markdown (quoted history included) and attachments with the `attachmentId` that `get_attachment` needs.                                                   |
| `get_attachment(messageId, attachmentId, filename?, mimeType?)`                                                           | Base64 bytes. `attachmentId`s are short-lived: if Gmail rejects one, call `read_email` again for a fresh id.                                                                                        |
| `compose_draft(to, subject, body, cc?, bcc?, from?, attachments?, inReplyTo?, references?, threadId?)`                    | Creates a draft; nothing is sent until `send_draft`. Returns `draftId`. For replies and forwards use the dedicated tools below.                                                                      |
| `draft_reply(messageId, body, replyAll?, additionalRecipients?, cc?, bcc?, from?, attachments?)`                          | Threading headers and the quoted original are set automatically.                                                                                                                                    |
| `draft_forward(messageId, to, cc?, bcc?, body?, from?, includeAttachments?, attachments?)`                                | Quotes the original in the body.                                                                                                                                                                    |
| `update_draft(draftId, to?, subject?, body?, cc?, bcc?, from?, attachments?)`                                             | Pass ONLY the fields that change; unset fields keep their value (threading headers and attachments included).                                                                                      |
| `get_draft(draftId)` / `list_drafts(maxResults?)`                                                                         | Read-only. `found=false` from `get_draft` means Gmail already sent or discarded the draft; verify with `search_emails("in:sent ...")`, never with `send_draft`.                                      |
| `send_draft(draftId)`                                                                                                     | Irreversible: emails every recipient on the draft. Call `get_draft` first if you have not seen the final recipients, `from` and attachments.                                                         |
| `discard_draft(draftId)`                                                                                                  | Idempotent; discarding a missing draft reports `discarded=false`.                                                                                                                                   |
| `archive_email(messageId)`                                                                                                | Removes only the INBOX label; the mail stays in All Mail. `label_email(addLabelIds: ["INBOX"])` undoes it.                                                                                          |
| `trash_email(messageId)`                                                                                                  | Gmail deletes it permanently after 30 days. Reversible until then with `label_email(removeLabelIds: ["TRASH"], addLabelIds: ["INBOX"])`.                                                            |
| `label_email(messageId, addLabelIds?, removeLabelIds?)`                                                                   | Takes label **ids**, not names. System labels work too: `INBOX`, `UNREAD`, `STARRED`, `IMPORTANT` (`removeLabelIds: ["UNREAD"]` marks read). Use `trash_email` rather than adding `TRASH`.          |
| `list_labels()` / `create_label(name)`                                                                                    | `create_label` is idempotent and returns the existing label's id.                                                                                                                                   |
| `get_aliases()`                                                                                                           | Send-as addresses accepted by the `from` field of the draft tools.                                                                                                                                  |

### Google Calendar

| Tool                                                                                                                                                                          | Notes                                                                                                                                                                                                                 |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `list_calendars()`                                                                                                                                                            | Calendars with the `calendarId` the other tools accept (default `primary`).                                                                                                                                           |
| `list_events(timeMin, timeMax, calendarId?, maxResults?, pageToken?, timeZone?)`                                                                                              | Recurring events are expanded; returns `eventId`, `recurringEventId` and attendee `responseStatus`.                                                                                                                   |
| `suggest_time(windows, attendees?, durationMinutes?, eventId?)`                                                                                                               | Ranks slots inside `windows` by how many attendees are free and says who is blocked by what. Work out working hours first and pass only such windows. `eventId` moves an existing event.                             |
| `create_event(title, startDateTime, endDateTime, calendarId?, timeZone?, description?, location?, attendees?, addConference?, recurrence?)`                                   | Creates immediately; every address in `attendees` gets an invitation, so include only attendees the user named. `addConference: true` adds a Google Meet link.                                                         |
| `update_event(eventId, calendarId?, title?, startDateTime?, endDateTime?, timeZone?, description?, location?, attendees?, addConference?, recurrence?)`                       | Omitted fields are unchanged; `attendees` replaces the whole list (`[]` removes everyone). Attendees are emailed about the change.                                                                                     |
| `update_occurrence(eventId, originalStartTime, calendarId?, cancel?, title?, startDateTime?, endDateTime?, timeZone?, location?, description?)`                               | Changes or cancels ONE occurrence of a recurring event.                                                                                                                                                               |
| `delete_event(eventId, calendarId?)`                                                                                                                                          | Irreversible; attendees get a cancellation. An instance id (`<seriesId>_20260715T160000Z`) removes one occurrence, the bare series id removes the series.                                                              |
| `rsvp_event(eventId, response, calendarId?)`                                                                                                                                  | `accepted` / `declined` / `tentative` on an invitation the user received. Only the user's own status changes. `status=not_attendee` means the user is not on the guest list.                                           |

### Google Contacts

| Tool                                  | Notes                                                  |
| ------------------------------------- | ------------------------------------------------------ |
| `search_contacts(query, maxResults?)` | Searches the user's contacts by name or email address. |

## Permissions

The plugin asks the user to pick Google permissions when they install it; the tools above only
load for permissions that were granted. Identity (`openid`, `userinfo.email`) is always included.

| Permission (Google OAuth scope)         | Unlocks                                                                                                                                                                          |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gmail.readonly`                        | `search_emails`, `read_email`, `get_attachment`, `get_draft`, `list_drafts`, `list_labels`, `get_aliases`                                                                       |
| `gmail.modify`                          | `compose_draft`, `update_draft`, `draft_reply`, `draft_forward`, `send_draft`, `discard_draft`, `archive_email`, `trash_email`, `label_email`, `create_label`                     |
| `calendar.readonly`                     | `list_calendars`, `list_events`, `suggest_time`                                                                                                                                 |
| `calendar.events`                       | `create_event`, `update_event`, `update_occurrence`, `delete_event`, `rsvp_event`                                                                                               |
| `contacts.readonly` + `contacts.other.readonly` | `search_contacts`                                                                                                                                                       |

## Working rules

- **Draft, show, then send.** Every outgoing email goes through a draft tool first. Show the
  user the recipients, subject and body (or the `get_draft` output) and send with `send_draft`
  only once they confirm; never send to check whether a send already happened.
- **Calendar writes notify people.** `create_event`, `update_event`, `update_occurrence` and
  `delete_event` email every attendee. Confirm the attendee list before creating, and prefer
  `update_occurrence` for a single meeting in a series.
- **Ids come from the tools.** `messageId`/`threadId` from `search_emails`/`read_email`,
  `draftId` from the draft tools, `labelId` from `list_labels`, `eventId`/`calendarId` from
  `list_events`/`list_calendars`. Never invent or guess an id.
- **Search before narrowing.** Do not add date operators to a sender-, recipient- or
  subject-scoped Gmail search unless the user asked for a time range; it hides older mail.
- **Attachments** on the draft tools take either `contentBase64` bytes or an anonymously
  fetchable AWS SigV4 presigned S3 `url`; other URLs are rejected.
- **Cleaning up** means `archive_email`, not `trash_email`, unless the user asked for the mail to
  be deleted.
