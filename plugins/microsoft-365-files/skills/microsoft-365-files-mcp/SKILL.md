---
name: microsoft-365-files-mcp
description: "Use the Microsoft 365 Files MCP tools (files_*) to browse OneDrive/SharePoint folders, stat items, read bounded file content, read a file the user shared as a SharePoint/OneDrive link, upload files, create folders and delete items. Invoke whenever a task involves the user's drive files or a sharing URL they pasted: it gives exact tool signatures, the drive-relative path rules, sharing-link rules, content and upload size limits, paging rules, the preview-then-confirm flow for writes, and how to interpret confirmed / confirmed_but_unreadable / rejected / indeterminate results."
---

# Microsoft 365 Files (MCP tools)

Connect to the files endpoint `/files/mcp`. It exposes only `files_*` tools — mail, calendar,
Teams, tasks and people lookups live behind separate endpoints.

## Choosing a tool

| You want to…                                                     | Call                       |
| ---------------------------------------------------------------- | -------------------------- |
| Check which account this endpoint is signed in as                | `files_me`                 |
| Find a SharePoint site                                           | `files_search_sites`       |
| List a site's document libraries                                 | `files_list_drives`        |
| See what is in a folder                                          | `files_list`               |
| Check whether something exists, its size or type                 | `files_stat`               |
| Read a file's content from a drive-relative path                 | `files_get_content`        |
| Read the file behind a SharePoint/OneDrive URL the user gave you | `files_get_shared_content` |
| Write / replace a file                                           | `files_upload`             |
| Create a folder                                                  | `files_mkdir`              |
| Remove a file or folder                                          | `files_delete`             |

## Tool signatures

| Tool                                                                                                                     | Notes                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `files_me()`                                                                                                             | Signed-in user (`id`, `display_name`, `mail`, `user_principal_name`) and `tenant_id` for this endpoint's token. Other M365 endpoints have their own tokens and may be signed in as someone else.                                              |
| `files_search_sites(query, max?, next?)`                                                                                 | Search SharePoint site names/keywords; `query` must be non-empty after trimming and at most 255 characters. `max` defaults to 25 and is capped at 200, like `files_list_drives`.                                                              |
| `files_list_drives(site_id, max?, next?)`                                                                                | List document libraries for the site; `max` defaults to 25 and is capped at 200. Repeat the same `site_id` when paging.                                                                                                                       |
| `files_list(path="", max?, next?, drive_id?)`                                                                            | Children of a folder; `""` or `"/"` is the drive root. Pass a SharePoint library's `drive_id` to use that library instead of the signed-in user's drive.                                                                                      |
| `files_stat(path, drive_id?)`                                                                                            | Metadata: name, size, folder/file, timestamps. `drive_id` selects a SharePoint library.                                                                                                                                                       |
| `files_get_content(path, max_bytes=65536, format?, width?, height?, drive_id?)`                                          | Bounded content; `1 <= max_bytes <= 10485760` (10 MiB). Optional Graph conversion: `format="pdf"` (Office/md/html/rtf…), `"html"` (Loop/Fluid/Whiteboard only), `"jpg"` (requires `width`+`height`, 1..10000). `drive_id` selects a library.  |
| `files_get_shared_content(share_url, max_bytes=65536)`                                                                   | Same bounds and response as `files_get_content`, plus `drive_id` and `item_id`.                                                                                                                                                               |
| `files_upload(path, content, content_encoding="utf-8"\|"base64", confirm=false, if_exists="replace"\|"fail", drive_id?)` | Simple upload. By default **overwrites** an existing file at that path; `if_exists="fail"` rejects with `graph_conflict` instead and leaves the file untouched. `drive_id` selects a SharePoint library.                                      |
| `files_mkdir(path, confirm=false, drive_id?)`                                                                            | Safe if the folder may exist: `confirmed` with `created: true` (new) or `created: false` (already there, untouched). A file at that path is `rejected` / `graph_conflict`. Creates missing intermediate folders (`a/b/c` from nothing works). |
| `files_delete(path, confirm=false, drive_id?)`                                                                           | Deletes a file or folder from the signed-in user's drive or the selected SharePoint library.                                                                                                                                                  |

## Paths (the most common source of errors)

Paths are **relative to the drive root** and validated before anything is sent:

- No leading `/` or `\`, forward slashes only.
- No empty, `.` or `..` segments — you cannot escape the drive root.
- No control characters.
- `""` and `"/"` both mean the drive root, and only `files_list` and `files_stat` accept it;
  no other absolute path is accepted.

Good: `Documents/2026/plan.md`. Rejected: `/Documents/plan.md`, `../other/plan.md`,
`Documents\\2026\\plan.md`.

## Discovering paths

Walk down with `files_list` from `""` or a folder you know, then `files_stat` the candidate
before acting on it. Do not guess a path from a file name the user mentioned in passing — there
is no file search tool, so confirm the location with the user if listing does not find it.

For a SharePoint library, call `files_search_sites` with a name or keyword, then
`files_list_drives` with the returned site's `id`. Use a returned drive's `id` as `drive_id` on
`files_list`, `files_stat`, `files_get_content`, `files_upload`, `files_mkdir` and `files_delete`.
Omit `drive_id` to keep using the signed-in user's drive. If the user pasted a SharePoint file URL,
use `files_get_shared_content` with that URL instead; it does not need site or library discovery.

## Reading content safely

- `files_get_content` returns `content` plus `truncated`, `returned_bytes` and `total_bytes`.
  Always check `truncated` before summarizing — do not present a truncated file as complete.
- Default 64 KiB, hard maximum 10 MiB. Use `files_stat` first when size matters; for a bigger
  file, tell the user it cannot be read whole rather than looping.
- Folder/package reads fail with structured `not_a_file`; items whose size Graph did not
  report fail with structured `file_size_unknown`.
- Binary content comes back base64-encoded; do not try to interpret it as text.
- Pass `format` when the bytes you want are a conversion, not the file itself:
  `format="pdf"` renders Office/markdown/rtf and similar documents as a PDF
  (useful for binary formats you cannot parse from raw bytes); `format="jpg"`
  renders a page image and requires `width` and `height`; `format="html"` only
  works on Loop/Fluid/Whiteboard items. Omit `format` for the original bytes.
  The result echoes which `format` was returned (`null` = original bytes).
- What Graph actually returns for a conversion can differ from the request:
  - `format="jpg"` has come back as **PNG** bytes (`\x89PNG`) while still echoing
    `format: "jpg"`; check the magic bytes before naming or decoding the file.
  - `width`/`height` are a **bounding box**, not the output size: a small image is
    not upscaled (an 8x8 PNG stayed 8x8 at 200x100) and the aspect ratio is kept.
  - `format="html"` also renders Markdown files (`<h1>`, `<strong>`…); on an
    `.html` file it returns the original bytes.
  - Formats Graph cannot convert (e.g. csv or png to `pdf`) fail with a generic
    `The preauthenticated file download endpoint rejected the request.` The same
    message is used for any failed converted download, including transient ones
    (throttling, 5xx), so it alone does not prove the format is unsupported: retry
    once, and if it fails again treat it as "conversion not supported" and fall
    back to the original bytes.
  - `width`/`height` are rejected unless `format="jpg"`.
- A converted result larger than `max_bytes` fails with structured `content_too_large`
  instead of truncating — a truncated PDF/JPG is unusable. Its size is unknown, so raise
  `max_bytes` up to 10 MiB or omit `format` to read the original bytes.

## Sharing links (a URL the user pasted)

When the user gives a SharePoint or OneDrive **URL** instead of a path, call
`files_get_shared_content` with that URL verbatim — do not try to turn it into a drive-relative
path, and never fetch or browse the URL yourself. The tool resolves it through Graph's `/shares`
mechanism and returns the same content fields plus `drive_id` and `item_id`; reuse those
identifiers if you need a follow-up call instead of passing the link again.

- Only worldwide-cloud sharing hosts are accepted: `*.sharepoint.com`, `1drv.ms`,
  `onedrive.live.com`. Anything else (http, another domain, a URL with `user@`) is rejected
  without any request.
- Pass the link exactly as received, query string included — the `?e=...` parameters are part of
  the link. Do not shorten, unshorten or rewrite it.
- Treat the URL as a credential: never echo it back in full and never put it in a file you write.
- The link only works if the signed-in user can access it: expired, revoked or anonymous-only
  links fail as not found. Ask the user to re-share rather than retrying.
- Shared Office/PDF files are usually over the 64 KiB default, so when the user's link is a
  document pass a bigger `max_bytes` up front (e.g. `10485760`) or retry with `total_bytes`.
- Folders/packages fail with `not_a_file`; oversized files fail with `content_too_large` before
  any download and include `total_bytes` plus the used `max_bytes`. Files above the 10 MiB hard
  maximum cannot be read through this tool; ask for a specific file or a smaller export.

## Paging

`files_list` returns `{ "items": [...], "next": <cursor|null> }`. For more, repeat the call with
`next` set to that value **verbatim** and the **same `path`** as the first call (a `next` without
its `path` is rejected as not matching the collection). When listing a SharePoint library, repeat
the same `drive_id` too. Site-search cursors are only valid for `files_search_sites`; drive-list
cursors are bound to the original `site_id`. Never edit or build the URL. Only `next: null` means
the collection is exhausted; `max` defaults to 25, max 200.

## Writing: preview → approval → confirm

Every write takes `confirm` (default `false`).

1. Call it **without** `confirm`. Nothing is written; you get a preview such as
   `{"operation": "upload", "bytes": 8, "max_bytes": 52428800}`.
2. Show the user the path and the effect — **especially that an upload replaces any existing
   file at that path** — and get explicit approval.
3. Re-run the **identical** call with `confirm: true`.

Read `status` on the result:

| `status`                   | Meaning                                                  | Do                                                                                                                                                            |
| -------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `confirmed`                | It happened.                                             | Report success using `body`.                                                                                                                                  |
| `confirmed_but_unreadable` | **It happened**; only the response was unreadable.       | Treat as success. Do **not** retry. `files_stat` if you need the metadata.                                                                                    |
| `rejected`                 | Nothing happened (no `confirm`, invalid path, or a 4xx). | `error.error == "confirmation_required"`: it was a preview — get approval, retry with `confirm: true`. Any other `error`: fix the arguments and retry safely. |
| `indeterminate`            | It **may** have happened (timeout / server error).       | **Do not re-upload.** `files_stat` the path and compare size/timestamp first, then tell the user it is unverified.                                            |

Uploading to a path that is an existing **folder** currently comes back as `indeterminate`
(`graph_unavailable`), although nothing was written. `files_stat` the target before uploading so
you never hit it.

`files_mkdir` needs no `files_stat` first and can be repeated: an existing folder comes back as
`confirmed` with `created: false`. `files_delete` at the same path may be retried once after
verifying state; an upload must not be blindly repeated.

## Best practices

- To create a file only if nothing is there, pass `if_exists: "fail"` to `files_upload`. Do not
  `files_stat` first and upload on "not found": another writer can create the file in between
  and it gets overwritten. A `rejected` outcome with `error.error == "graph_conflict"` means the
  path is taken and nothing was written — do not retry with `replace` unless the user wants to
  overwrite.
- When overwriting is intended, `files_stat` before `files_upload` and warn the user about what
  you are about to replace.
- Uploads are **simple uploads capped at 50 MiB**; larger content raises. Chunked upload
  sessions are not available, so do not attempt to split a large file.
- Binary payloads must be base64 with `content_encoding: "base64"`; text defaults to `"utf-8"`.
- `files_delete` on a folder removes its contents — always confirm the exact path with the user.
- Never paste the bearer token, and never quote raw Graph error bodies to the user.

## Examples

```jsonc
// Browse, then read
files_list { "path": "Documents/2026" }
files_list { "path": "Documents/2026", "next": "https://graph.microsoft.com/v1.0/me/drive/items/01ABC.../children?$skiptoken=..." }
files_stat { "path": "Documents/2026/plan.md" }
files_get_content { "path": "Documents/2026/plan.md", "max_bytes": 65536 }
//  -> { "content": "# Plan\n", "truncated": false, "returned_bytes": 7, "total_bytes": 7 }

// The user pasted a link instead of a path
files_get_shared_content { "share_url": "https://contoso.sharepoint.com/:w:/g/personal/alex/..." }
//  -> { "content": "# Plan\n", "drive_id": "b!...", "item_id": "01ABC...", "item": { "name": "plan.md" } }

// Write: preview, warn about overwrite, confirm
files_upload { "path": "Documents/2026/plan.md", "content": "# Plan\n" }
//  -> { "status": "rejected", "preview": { "operation": "upload", "bytes": 7, "max_bytes": 52428800 }, "error": { "error": "confirmation_required", ... } }
files_upload { "path": "Documents/2026/plan.md", "content": "# Plan\n", "confirm": true }

// Write only if the path is free (no files_stat needed): preview, get approval, confirm
files_upload { "path": "Documents/2026/notes.md", "content": "# Notes\n", "if_exists": "fail" }
//  -> { "status": "rejected", "preview": { "operation": "upload", "if_exists": "fail", ... }, "error": { "error": "confirmation_required", ... } }
files_upload { "path": "Documents/2026/notes.md", "content": "# Notes\n", "if_exists": "fail", "confirm": true }
//  -> created: { "status": "confirmed", ... }
//  -> already there: { "status": "rejected", "error": { "error": "graph_conflict", ... } }

files_mkdir { "path": "Documents/2026/archive", "confirm": true }
```

## Not available — don't promise these

- Large-file upload sessions (>50 MiB) and resumable/chunked uploads.
- Search across files, move, copy, rename and version history.
- Creating sharing links, and permissions / sharing management (reading a link the user already
  has is supported via `files_get_shared_content`).
- Selecting other users' drives.

## When something fails

- **A tool is missing from `tools/list`** → the user's token lacks its scope. Reads accept
  `Files.Read`, `Files.ReadWrite`, `Files.Read.All`, `Files.ReadWrite.All`, `Sites.Read.All` or
  `Sites.ReadWrite.All`; `files_search_sites` requires `Sites.Read.All` or `Sites.ReadWrite.All`.
  Writes accept `Files.ReadWrite`, `Files.ReadWrite.All` or `Sites.ReadWrite.All`, and
  `files_get_shared_content` accepts those same scopes (Graph documents `Files.ReadWrite` as the
  least privileged delegated permission for `/shares`, so a `Files.Read`-only token cannot use it).
  `Files.Read` and `Files.ReadWrite` cover only the user's own files; SharePoint libraries need
  `Files.Read.All` or `Sites.Read.All` (or a ReadWrite variant). If Graph returns 403, ask the user
  to reconnect the MCP with the needed scopes. Calling a hidden tool anyway returns
  `insufficient_scope` with `required_scopes`; report it rather than working around it.
- **`401`** → the token is missing or expired; ask the caller for a fresh one.
- **429 / `retryable`** → wait `retry_after`, and retry reads only.
- **`content_too_large`** → nothing was downloaded. If `total_bytes <= max_allowed_bytes`, retry
  once with `max_bytes = total_bytes`; for a conversion (no `total_bytes`) below the limit,
  follow the hint to retry once with a larger `max_bytes` or omit `format`. If it is bigger than
  10 MiB (or a conversion with no `total_bytes` is already at 10 MiB), tell the user it cannot be
  read through this tool and ask for a smaller file/export. Do not loop.
- **`not_a_file`** → the path/link is a folder or package (e.g. a OneNote notebook); `files_list`
  the folder or ask the user for a link to a specific file.
- **`file_size_unknown`** → Graph reported no size, so the file cannot be read with a bound; tell
  the user.
- **`invalid_graph_url`** → the `next` cursor was altered, or you passed it without the `path` it
  came from (or with a different one); restart from the first page.
- **Validation errors** (bad path, `max_bytes` out of range, oversized upload) mean nothing was
  sent; fix the arguments.
- **Not found** → re-`files_list` the parent folder; do not guess a neighbouring path.

## Golden path

1. Check the tool is listed; if not, report the missing scope.
2. `files_list` / `files_stat` to establish the exact drive-relative path — or, when the user gave
   a sharing URL, `files_get_shared_content` with that URL as-is.
3. Read with a bounded `max_bytes` and check `truncated`; page with `next` verbatim.
4. Write without `confirm`, show the path and the overwrite risk, get approval.
5. Repeat the identical call with `confirm: true`.
6. `confirmed` → done · `confirmed_but_unreadable` → done, no retry · `rejected` → nothing
   happened · `indeterminate` → `files_stat` to verify, never re-upload blindly.
7. Report the exact paths you touched.
