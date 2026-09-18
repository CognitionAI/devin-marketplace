---
name: microsoft-365-directory-mcp
description: "Use the Microsoft 365 Directory MCP tools (directory_*) to look people up in Entra ID: search users by display name, fetch a user by object ID or UPN, get a user's manager, and identify the signed-in user. Invoke whenever a task needs someone's identity, email address or Entra object ID (for example before DMing them in Teams or inviting them to a meeting): it gives exact tool signatures, what each returns, paging rules, and how to resolve ambiguous matches safely. Directory is read-only."
---

# Microsoft 365 Directory (MCP tools)

Connect to the directory endpoint `/directory/mcp`. It exposes only `directory_*` tools, all
**read-only** — mail, calendar, files, Teams and tasks live behind separate endpoints.

## Choosing a tool

| You want to…                              | Call                     |
| ----------------------------------------- | ------------------------ |
| Find a person by name                     | `directory_search_users` |
| Look someone up by object id or UPN/email | `directory_get_user`     |
| Find who someone reports to               | `directory_get_manager`  |
| Know who the signed-in user is            | `directory_me`           |

## Tool signatures

| Tool                                             | Notes                                                                                             |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `directory_search_users(query, limit?, cursor?)` | Matches **display name only**. `query` must be non-empty; quotes/backslashes are escaped for you. |
| `directory_get_user(user_id)`                    | `user_id` is an Entra object id **or** a UPN/email.                                               |
| `directory_get_manager(user_id)`                 | Returns the manager; `object_type` says whether it is a user or an org contact.                   |
| `directory_me()`                                 | The signed-in delegated user.                                                                     |

All of them return a narrow projection: `id`, `display_name`, `given_name`, `surname`, `mail`,
`user_principal_name`. Use `id` (the Entra **object id**, a GUID) whenever another tool asks for
a user id — for example the Collaboration MCP's `collaboration_send_dm` and `mentions` require
exactly that GUID and reject a UPN or email address.

## Using it well

- Searching by an email address or UPN will not work in `search_users` — pass it to
  `directory_get_user` instead.
- **Resolve ambiguity with the user, not by guessing.** If `search_users` returns several
  people, present the candidates (name + mail) and ask which one — never pick the first match
  before sending a message, an invitation or anything else user-visible.
- If a search returns nothing, try a shorter or differently spelled display name, or ask the
  user for the person's address and use `directory_get_user`.
- `directory_me` is the cheapest way to establish "the user" (their address, object id) before
  composing something on their behalf.
- Never paste the bearer token, and never quote raw Graph error bodies to the user.

## Paging

Lists return `{ "items": [...], "next": <cursor|null> }`. For more results, repeat the call with
`cursor` set to `next` **verbatim** and nothing else changed; never edit or build the URL. Only
`next: null` means the results are exhausted. `limit` defaults to 25, max 200. Prefer refining
`query` over paging deep into search results.

## Examples

```jsonc
directory_me { }
//  -> { "id": "0a1b...-guid", "display_name": "Sam Lee", "mail": "sam@contoso.com" }

directory_search_users { "query": "Ana Ruiz", "limit": 10 }
//  -> items: [{ "id": "6f1e...-guid", "display_name": "Ana Ruiz", "mail": "ana@contoso.com" }]
// two matches? -> ask the user which one before doing anything with the result

directory_get_user { "user_id": "ana@contoso.com" }
directory_get_manager { "user_id": "6f1e...-guid" }
//  -> { "id": "3c2d...-guid", "display_name": "Iris Cole", "object_type": "user" }

// Cross-workload handoff (only if the Collaboration endpoint is also connected):
// take items[].id from the search and pass it as collaboration_send_dm's user_id.
```

## Not available — don't promise these

- Any write: creating, updating or deleting users, groups or memberships. Directory is read-only.
- Group and Microsoft 365 Groups listing or management; direct reports, photos and org charts.
- Searching by mail/UPN/job title/department — display-name search plus `get_user` only.
- Guest/B2B or cross-tenant lookups beyond what the signed-in user's tenant returns.

## When something fails

- **A tool is missing from `tools/list`** → the user's token lacks its scope.
  `directory_search_users` / `directory_get_user` accept `User.ReadBasic.All`, `User.Read.All`,
  `User.ReadWrite.All`, `Directory.Read.All` or `Directory.ReadWrite.All`. **`directory_get_manager`
  needs a strictly higher scope** — `User.Read.All`, `User.ReadWrite.All`, `Directory.Read.All`,
  `Directory.ReadWrite.All`, `AgentIdUser.ReadWrite.All` or
  `AgentIdUser.ReadWrite.IdentityParentedBy` — so search working while `get_manager` is missing
  is expected, not a bug. `directory_me` also accepts plain `User.Read`. Calling an uncovered
  tool returns `insufficient_scope` with `required_scopes`; report which scope to add (admin
  consent may be needed) instead of improvising.
- **`401`** → the token is missing or expired; ask the caller for a fresh one.
- **429 / `retryable`** → wait `retry_after` before retrying.
- **`invalid_graph_url`** → the cursor was altered; restart from the first page.
- **Empty `query`** is rejected; supply a real name.
- **No manager** (top of the org, or an org contact) comes back as a not-found error (`Resource 'manager' does not exist`), not an empty result. It is a valid answer — report "no manager", don't treat it as a failure.

## Golden path

1. Check the tool is listed; if not, report the missing scope (remember `get_manager` needs
   more than search).
2. Search by display name, or `get_user` when you have an address/object id.
3. If more than one candidate matches, ask the user before using the result.
4. Carry the `id` (object id) forward to whatever needs a user id.
5. Report the person you resolved (name + mail) so the user can catch a wrong match early.
