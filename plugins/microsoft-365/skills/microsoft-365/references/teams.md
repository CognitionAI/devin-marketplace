# Microsoft 365 Collaboration / Teams (MCP tools)

Connect to the collaboration endpoint `/collaboration/mcp`. It exposes only `collaboration_*`
tools — mail, calendar, files, tasks and people lookups live behind separate endpoints.

## Choosing a tool

| You want to…                            | Call                                 |
| --------------------------------------- | ------------------------------------ |
| Find the user's teams                   | `collaboration_list_teams`           |
| Find a channel in a team                | `collaboration_list_channels`        |
| Find an existing chat (ids/topics only) | `collaboration_list_chats`           |
| See who is in a chat                    | `collaboration_list_chat_members`    |
| Post in a team channel                  | `collaboration_send_channel_message` |
| Post in an existing chat (group or 1:1) | `collaboration_send_chat_message`    |
| Message one person directly             | `collaboration_send_dm`              |

## Tool signatures

| Tool                                                                                         | Notes                                                                              |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `collaboration_list_teams(cursor?)`                                                          | Teams the user has joined.                                                         |
| `collaboration_list_channels(team_id, cursor?)`                                              | Channels of a team.                                                                |
| `collaboration_list_chats(limit?, cursor?)`                                                  | Chat **metadata only** — id, topic, type, timestamps. No messages. `limit` max 50. |
| `collaboration_list_chat_members(chat_id, cursor?)`                                          | Members of a chat.                                                                 |
| `collaboration_send_channel_message(team_id, channel_id, content, mentions?, confirm=false)` | Posts only with `confirm=true`.                                                    |
| `collaboration_send_chat_message(chat_id, content, mentions?, confirm=false)`                | Posts only with `confirm=true`.                                                    |
| `collaboration_send_dm(user_id, content, mentions?, confirm=false)`                          | Finds or creates a verified 1:1 chat with `user_id`, then sends.                   |

## You cannot read messages

These tools expose chat **metadata**, not content. Never say you checked a conversation, and
never plan a "read the last message, then reply" sequence — ask the user for the context you
need. Reading history is deliberately out of scope; recommend `Chat.ReadBasic` for chat access
and do **not** ask the user to grant `Chat.Read`.

## Discovering ids

- Team id → `collaboration_list_teams`. Channel id → `collaboration_list_channels(team_id)`.
- Chat id → `collaboration_list_chats` (match on `topic` / members via
  `collaboration_list_chat_members`; if several plausibly match, ask the user).
- **DM recipient**: `collaboration_send_dm` needs the recipient's **Entra user object id (a
  GUID)**. A UPN or email address is rejected with `dm_recipient_unverified`. Get the GUID from
  the Directory MCP (`directory_search_users` → `items[].id`) if that endpoint is connected, or
  from the user. Mentions need the same GUID.

## Message content and mentions

- `content` is treated as **plain text and HTML-escaped** before sending, so any markup or
  markdown you write shows up literally. Write plain prose.
- To mention people, use `mentions`:
  `[{"user_id": "<entra-object-id>", "display_name": "Ana"}]`. An `<at>` tag per mention is
  appended to the message text automatically, in array order — do not write `<at>` yourself.

## Sending: describe → approval → confirm

Every send takes `confirm` (default `false`).

1. Call it **without** `confirm`. Nothing is posted; you get a `rejected` outcome with
   `confirmation_required`.
2. Show the user the exact destination (team + channel, or the chat / person) and the exact text
   you will post, and get explicit approval.
3. Re-run the **identical** call with `confirm: true`.

Read `status` on the result:

| `status`                   | Meaning                                                            | Do                                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `confirmed`                | The message was posted.                                            | Report success using `body`.                                                                                                              |
| `confirmed_but_unreadable` | **The message was posted**; only the response was unreadable.      | Treat as success. Do **not** resend.                                                                                                      |
| `rejected`                 | Nothing was posted (no `confirm`, unverified recipient, or a 4xx). | Fix the arguments (or the identity) and retry safely.                                                                                     |
| `indeterminate`            | It **may** have been posted (timeout / server error).              | **Never resend** — you would double-post. Tell the user it is unverified and ask them to check Teams; you cannot read the chat to verify. |

No send is idempotent: never blindly retry one.

## DM safety rules

`collaboration_send_dm` fails closed. It only sends after proving the target chat is a
`oneOnOne` chat whose members are exactly the signed-in user and the recipient, both are AAD
users in the caller's tenant, and neither is a guest. Ambiguous matches, guests, foreign tenants
and unexpected chat types abort before anything is sent.

If `send_dm` refuses: **do not** work around it by picking a chat id out of
`collaboration_list_chats` and calling `send_chat_message`. Re-resolve the person's object id
and ask the user to confirm the recipient.

## Examples

```jsonc
// Post in a channel
collaboration_list_teams { }
collaboration_list_channels { "team_id": "19:abc...@thread.tacv2" }
collaboration_send_channel_message {
  "team_id": "19:abc...@thread.tacv2", "channel_id": "19:def...@thread.tacv2",
  "content": "Deploy finished, notes in Documents/2026/plan.md"
}
//  -> { "status": "rejected", ... confirmation_required }   nothing posted
collaboration_send_channel_message { /* identical arguments */ "confirm": true }

// DM a person (object id from the Directory MCP, if connected)
directory_search_users { "query": "Ana Ruiz" }        // -> items[0].id = "6f1e...-guid"
collaboration_send_dm {
  "user_id": "6f1e...-guid",
  "content": "Notes are in Documents/2026/plan.md",
  "mentions": [{ "user_id": "6f1e...-guid", "display_name": "Ana" }],
  "confirm": true                                      // only after the user approved
}
```

## Not available — don't promise these

- Reading chat or channel message history (`Chat.Read` is intentionally not used).
- Sending or sharing a file inside a chat — upload it with the Files MCP and paste the location
  in the message text.
- Replying in a channel thread, editing, deleting or reacting to messages.
- Creating teams/channels/group chats, or managing membership.
- Microsoft 365 Groups management.

## When something fails

- **A tool is missing from `tools/list`** → the user's token lacks its scope. Typical minimums:
  `Team.ReadBasic.All` (list teams), `Channel.ReadBasic.All` (list channels), `Chat.ReadBasic`
  (list chats and members), `ChannelMessage.Send` (channel post), `ChatMessage.Send` (chat
  post), and for `send_dm` **all four** of `Chat.Create`, `ChatMessage.Send`, `User.Read` and
  `Chat.ReadBasic`. Calling an uncovered tool returns `insufficient_scope` with
  `required_scopes`; report it rather than working around it.
- **`dm_recipient_unverified`** → you passed a UPN/email, or the chat could not be proven to be
  a clean 1:1 with that person. Get the Entra object id and confirm the recipient with the user.
- **`401`** → the token is missing or expired; ask the caller for a fresh one.
- **429 / `retryable`** → wait `retry_after`, and retry reads only.
- **`invalid_graph_url`** → the cursor was altered; restart from the first page.
- Lists return `{ "items": [...], "next": <cursor|null> }`: repeat the call with `cursor` set to
  `next` **verbatim** for more; only `next: null` means the end.
- Never paste the bearer token, and never quote raw Graph error bodies to the user.

## Golden path

1. Check the tool is listed; if not, report the missing scope.
2. Resolve the destination: team + channel ids, a chat id, or an Entra object id for a DM.
   Never guess, and never assume you can read the conversation first.
3. Draft the plain-text message (plus `mentions` GUIDs if needed).
4. Send without `confirm`, show the user the destination and exact text, get approval.
5. Repeat the identical call with `confirm: true`.
6. `confirmed` → done · `confirmed_but_unreadable` → done, no resend · `rejected` → nothing
   posted · `indeterminate` → tell the user to check Teams, never resend.
7. Report where you posted and to whom.
