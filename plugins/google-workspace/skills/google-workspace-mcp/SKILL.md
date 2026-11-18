---
name: google-workspace-mcp
description: "Use the Google Drive, Docs, Sheets, Slides and Forms MCP tools: find and download files, read and edit Docs/Sheets/Slides/Forms, leave and resolve comments, see who has access. Invoke whenever a task touches the user's Google Drive or a Google Doc, Sheet, Slides deck or Form: it gives the tool signatures, which permission unlocks each tool, the id and index conventions, the batchUpdate rules shared by every update_* tool, and the read -> edit -> read-again loop every write follows."
---

# Google Drive, Docs, Sheets, Slides & Forms (MCP tools)

Connect to `https://google-mcp.devin.ai/drive/mcp`. One endpoint serves Drive, Docs, Sheets,
Slides and Forms; a tool is listed only when the user granted the permission it needs (see
"Permissions"). A tool you expect but cannot see means the user did not grant that permission:
say which one is missing instead of working around it. Every call runs as the user's own Google
account, so Devin sees exactly the files they can see and every edit or comment is attributed to
them.

Workflow skills in this plugin build on this reference: `write-google-doc` (author or edit a
Doc), `build-google-sheet` (models, trackers, accounting workbooks), `build-google-slides`
(native decks), `review-google-files` (Devin as reviewer: anchored comments on any surface),
`google-forms-surveys` (forms, quizzes and their responses).

## Choosing a tool

| You want to…                                              | Call                                                                 |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| Find a file, list a folder, browse a shared drive         | `search_files` (Drive query syntax); `list_shared_drives`            |
| Metadata: type, size, parents, owners, link               | `get_file`                                                           |
| The bytes of any file, or a Doc/Sheet/deck rendered        | `download_file` (PDF/xlsx/pptx/docx/csv/png exports)                 |
| Who edited a file and when, an old version, what changed  | `list_revisions`, then `download_file` with `revisionId`             |
| Read the structure of a Doc / Sheet / deck / Form         | `read_doc` / `read_sheet` / `read_presentation` / `read_form`        |
| See one slide as an image                                 | `get_slide_thumbnail`                                                |
| Create a Doc or Sheet from text, a blank deck, a folder   | `create_file`                                                        |
| Start from a template or an Office file                   | `copy_file` (`type` converts .docx/.xlsx/.pptx/.csv to a Google type) |
| Rename, move, bin/unbin, star, replace whole content      | `update_file`                                                        |
| Edit part of a Doc / Sheet / deck / Form                   | `update_doc` / `update_spreadsheet` / `update_presentation` / `update_form` |
| Write or append cell values                               | `write_sheet`                                                        |
| Leave a comment pinned to text, a cell or an element      | `add_comment` with `anchor`; several at once: `insertComment` requests in `update_doc` / `update_spreadsheet` / `update_presentation` |
| Read, reply to, resolve, edit or delete comment threads   | `list_comments`, `reply_to_comment`, `update_comment`, `delete_comment`; `add_comment` without `anchor` for a file-level (unpinned) note |
| Who has access to a file                                  | `list_permissions` (sharing is done by the user in Drive; the MCP cannot grant access) |
| Form responses; a form's publish state                    | `list_form_responses`; `read_form`                                   |
| Remove a file for good                                    | `delete_file` (only when asked; otherwise `update_file trash=true`)  |

## Tool signatures

`?` marks optional arguments. Every `fileId` / `documentId` / `spreadsheetId` / `presentationId`
/ `formId` also accepts the file's Drive, Docs, Sheets, Slides or Forms URL, so a link the user
pasted can be passed straight through.

### Drive

| Tool                                                                                                   | Notes                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_files(query?, pageSize?, pageToken?, orderBy?)`                                                | `files.list` `q` syntax: `name contains 'roadmap'`, `fullText contains 'pricing'`, `'<folderId>' in parents` (`root` = My Drive), `mimeType = 'application/vnd.google-apps.spreadsheet'`, `'me' in owners`, `modifiedTime > '2026-01-01T00:00:00'`. Binned files are left out unless the query mentions `trashed`. `orderBy` is not allowed with `fullText`. |
| `get_file(fileId)`                                                                                     | Type, size, parents, owners, sharing summary, `webViewLink`.                                                                                                                                                                         |
| `download_file(fileId, exportMimeType?, revisionId?)`                                                  | `fileId` is also a Doc/Sheet/Slides/Form id. Base64 bytes, up to 10 MB. Google files are exported: Doc -> PDF, Sheet -> xlsx, Slides -> PDF, Drawing -> PNG by default; `exportMimeType` picks docx/xlsx/pptx/csv/txt/png/html instead. **Always call it from `scripted_tools` and write the bytes to disk**; the base64 must never land in chat context. `revisionId` (from `list_revisions`) returns that old version instead of the current one, in the same formats. |
| `list_revisions(fileId, limit?)`                                                                       | The file's version history, newest first: each revision's `id`, `modifiedTime` and `lastModifyingUser`, plus `total` (`limit` defaults to 50). Any file type except folders. Google merges the edits to a Doc, Sheet or deck into coarser revisions than File -> Version history shows, so one revision can hold many edits. Seeing the history usually takes edit access to the file; a view-only file answers with a permission error. |
| `create_file(name, content?, contentType?, type?, folderId?, shortcutTo?, description?)`               | `type: "document"` converts Markdown (default) or HTML content into a Doc; `type: "spreadsheet"` converts CSV into a Sheet whose tab is named after the file; `type: "presentation"` / `"form"` start blank (fill with `update_*`); `type: "folder"`. Without `type` the text is stored as a plain file. Default location is My Drive root. |
| `copy_file(fileId, name?, folderId?, type?, copyComments?)`                                            | Copies land next to the original unless `folderId` is set (a copy of a file in a read-only folder then fails: pass `folderId`). `type` converts an Office/CSV file into a Google type during the copy. `copyComments` re-posts threads as the caller and without pins; re-pin with `add_comment` if the position matters. Folders cannot be copied.      |
| `update_file(fileId, name?, folderId?, trash?, untrash?, starred?, description?, content?, contentType?, replaceAllTabs?)` | `content` replaces everything (a Sheet is rebuilt as one tab: refused on a multi-tab Sheet unless `replaceAllTabs`). For partial edits use the `update_*` tools.                                                                       |
| `delete_file(fileId)`                                                                                  | Permanent, skips the bin, deletes a folder's contents too. Prefer `update_file trash=true`.                                                                                                                                           |
| `list_shared_drives(query?, pageToken?)`                                                               | Ids usable as `folderId` or in `'<driveId>' in parents`.                                                                                                                                                                             |

### Comments and access (Drive)

| Tool                                                                                                       | Notes                                                                                                                                                                                    |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `list_comments(fileId, includeDeleted?, modifiedAfter?, pageToken?)`                                       | Every thread with `commentId`, quoted text, `anchor` (present only on a thread pinned to a position), resolved state, author, assignee, mentions and replies (with `replyId`); assignee is not returned by Google for batch-created comments. Works on Docs, Sheets, Slides and PDFs/images stored in Drive. |
| `add_comment(fileId, content, quote?, anchor?)`                                                            | `anchor` pins the thread: Doc `{"range": {"startIndex", "endIndex", "tabId"?}}` (from `read_doc`), Sheet `{"coordinate": {"sheetId", "rowIndex", "columnIndex"}}` (0-based), Slides `{"objectId"}` of an element, or `shapeTextAnchor` / `tableCellTextAnchor` / `tableAnchor` for a finer position (shapes in `review-google-files`). The tool picks the surface from the file type and runs its `insertComment`; a `comment_not_saved` error means Google did not confirm the save: check `list_comments` before retrying. `quote` only records the passage (the thread stays unpinned) and cannot be combined with `anchor`. |
| `reply_to_comment(fileId, commentId, content?, action?)`                                                   | `action: "resolve"` / `"reopen"`; resolving with no content posts a bare resolution. A reply with no `action` reopens a resolved thread.                                                  |
| `update_comment(fileId, commentId, content, replyId?)` / `delete_comment(fileId, commentId, replyId?)`     | Only the user's own comments.                                                                                                                                                            |
| `list_permissions(fileId, pageToken?)`                                                                     | Grantee, role, expiry, inherited-from-folder flag, `permissionId`.                                                                                                                       |

### Docs

| Tool                                                      | Notes                                                                                                                                                                                                                                                                                                 |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_doc(documentId, tabId?, startIndex?, suggestions?, format?)` | Each paragraph/table as `[start-end] STYLE: text`, the indexes `update_doc` needs. Lists, links, images, footnotes, headers/footers are marked; suggested edits show as `{+added+}` / `[-removed-]` (`suggestions: "accepted"` / `"rejected"` previews the doc with them applied / dropped, indexes then not editable); `format: "json"` returns the raw Docs API document. To see the rendered pages, `download_file` as PDF. |
| `update_doc(documentId, requests)`                        | Docs `batchUpdate`. The tool description lists the request shapes (text, style, tables, headers/footers, tabs, named ranges, comments, suggestions). Rules below.                                                                                                                                     |

### Sheets

| Tool                                                                                                                       | Notes                                                                                                                                                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_sheet(spreadsheetId, range?, ranges?, valueRender?, dateTimeRender?, majorDimension?, details?)`                      | No range: tabs with numeric `sheetId`, sizes, frozen rows, named and protected ranges. With a range: values **as displayed** (`"$100,000"`) by default; `valueRender: "unformatted"` for numbers, `"formula"` to audit formulas; `details: true` for per-cell notes, links, validation and formats. |
| `write_sheet(spreadsheetId, range, values?, append?, clear?, raw?, majorDimension?, appendMode?, returnValues?)`           | Overwrites from the range's top-left cell. Strings are parsed as typed: `=SUM(A1:A3)` becomes a formula, `2027-01-01` a date, `12%` a percent; `raw: true` stores them literally. `append: true` adds rows under the table found in `range`. `clear: true` empties the range. |
| `update_spreadsheet(spreadsheetId, requests)`                                                                              | Sheets `batchUpdate` for everything that is not a plain value: tabs, formats, validation, conditional formats, named/protected ranges, charts, comments. Ranges use the numeric `sheetId` and 0-based, end-exclusive indexes.                                            |

### Slides

| Tool                                                      | Notes                                                                                                                                                                                                                                             |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_presentation(presentationId)`                       | Page size, layouts (with their ids), then every slide's `slideId`, layout, speaker notes (with the notes shape id), and every element's kind, position/size in PT, text, placeholder type, image/video/chart source.                               |
| `get_slide_thumbnail(presentationId, slideId, size?)`     | PNG of one slide (`small` 200px, `medium` 800px, `large` 1600px). The way to check a layout visually; whole deck: `download_file` as PDF.                                                                                                         |
| `update_presentation(presentationId, requests)`           | Slides `batchUpdate`: slides, text, shapes, images, tables, charts, comments. New objects take your own `objectId` (5-50 chars `[A-Za-z0-9_-]`) so later requests in the same call can refer to them.                                              |

### Forms

| Tool                                                                      | Notes                                                                                                                        |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `read_form(formId)`                                                       | Title, responder link, publish state (publishing and opening/closing for responses happen in the Forms UI), settings, linked Sheet, every item with `itemId`/`questionId`, type, options, grading. |
| `update_form(formId, requests)`                                           | Forms `batchUpdate` (items are addressed by 0-based position).                                                               |
| `list_form_responses(formId, pageSize?, pageToken?, submittedAfter?)`     | Answers keyed by `questionId`; needs the `forms:responses` permission.                                                       |

## Permissions

| Permission (Google OAuth scope)                | Unlocks                                                                                                                                                               |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read (`drive.readonly`)                        | `search_files`, `get_file`, `download_file`, `list_revisions`, `list_shared_drives`, `list_comments`, `list_permissions`, `read_doc`, `read_sheet`, `read_presentation`, `get_slide_thumbnail`, `read_form` |
| Edit (`drive`)                                 | `create_file`, `copy_file`, `update_file`, `delete_file`, `write_sheet`, every `update_*`, `add_comment`, `reply_to_comment`, `update_comment`, `delete_comment` |
| Form responses (`forms.responses.readonly`)    | `list_form_responses`                                                                                                                                                 |

## Working rules

- **Ids come from the tools.** File ids from `search_files` or the user's URL; Doc indexes from
  `read_doc`; `sheetId` from `read_sheet` with no range; slide and element object ids from
  `read_presentation`; `commentId` / `replyId` from `list_comments` or an `insertComment`
  reply; `permissionId` from `list_permissions`. Never guess an id or an index.
- **Read, edit, read again.** Every edit to an existing file starts with the matching read
  tool and ends with it (or a `download_file` PDF / `get_slide_thumbnail` when layout
  matters), so the result is checked against what the user asked, not assumed.
- **batchUpdate semantics are shared by all four `update_*` tools.** Requests apply in order;
  one invalid request fails the whole call and nothing is applied; the error names the failing
  request by index (`requests[3]`). Replies come back one per request (`{}` when there is
  nothing to return) and carry created ids: `sheetId`, `chartId`, `namedRangeId`,
  `commentThread.commentId`, `objectId`, `headerId`, `itemId`. Keep a call to one logical
  step (one section, one tab, one slide) so a failure is easy to locate; up to about 100
  requests per call is fine.
- **Docs indexes shift.** Within one `update_doc` call order edits from the highest index down
  so earlier indexes stay valid, or re-read between calls. The end index of the last paragraph
  is not insertable: append with `endOfSegmentLocation: {}` (start the text with `\n` to
  begin a new paragraph) or insert at `endIndex - 1`.
- **Sheets ranges.** A1 ranges in `read_sheet` / `write_sheet` must include the tab name
  (`'P&L'!A1:G5`, quotes when the name has spaces or symbols); grid ranges in
  `update_spreadsheet` use the numeric `sheetId` and 0-based, end-exclusive row/column indexes.
- **Comments are first-class on every surface.** `add_comment` with `anchor` pins one
  comment to a Doc range, a Sheet cell or a Slides element, and takes the finer Slides anchors
  (`shapeTextAnchor` text range, `tableCellTextAnchor`) directly. For several comments in one
  call, send `insertComment` requests through `update_doc` / `update_spreadsheet` /
  `update_presentation`; `addCommentReply: {commentId, post: {content, commentAction?}}`
  (`content` goes inside `post`) with `commentAction: "RESOLVE"` / `"REOPEN"`, or
  `reply_to_comment` with `action`, closes or reopens a thread. `add_comment` without
  `anchor` is only for a file-level note; `quote` does not pin. The API cannot create Docs *suggestions*
  (tracked changes): a proposed wording goes in a comment, or is applied directly when the
  user asked for the edit. See `review-google-files`.
- **Files are the user's.** Create files where the user said, else their My Drive root, and
  tell them where. Edits land in the real file at once (undo is File -> Version history), so on
  a file Devin did not create, offer a `copy_file` backup before the first large rewrite.
  Never create scratch or test files; the file created for the request is the one file that
  request creates, and later fixes are `update_*` calls on it. Use `update_file trash=true`,
  not `delete_file`, unless the user asked for permanent deletion.
- **Version history answers questions about the past.** Use it when the user asks who changed
  a file or when, what changed since a date or a review, or what it said before an edit.
  `list_revisions` gives the ids; from `scripted_tools`, `download_file` the revision before
  the change and the current file in a text format (a Doc as `text/markdown`, a Sheet as xlsx,
  or `text/csv` for its first tab, a deck as `text/plain`), write both to disk and diff them
  there. Report what changed, not the two versions. Rolling a file back is the user's step
  (File -> Version history -> Restore this version); the MCP reads old versions only.
- **Sharing is the user's job.** The MCP cannot share a file or change permissions; `list_permissions` says who has access. When a deliverable needs readers, say so and let the user share it in Drive.
- **Big payloads stay out of chat.** `download_file` (base64) and large `read_*` results on
  big files belong in `scripted_tools`, written to disk and processed there.
- **Not possible through the MCP** (say so instead of improvising): sharing a file or changing permissions; publishing a Form or opening/closing it for responses; Docs suggestion mode; restoring, naming or deleting a file version;
  file-upload questions in Forms; changing a deck's page size; uploading binary files
  (`create_file` takes text; convert an Office file already in Drive with `copy_file type`);
  images in Slides/Docs need a URL Google can fetch (a public URL or a Drive file the user can
  read).
