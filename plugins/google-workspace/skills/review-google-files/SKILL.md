---
name: review-google-files
description: "Review a Google Doc, Sheet or Slides deck the way a careful colleague would, leaving comments anchored to the exact passage, cell or shape, replying in existing threads and resolving them, and reporting back. Use whenever the user asks Devin to review, give feedback on, check, proofread, fact-check, sanity-check or 'leave comments on' a Doc, Sheet or deck, to work through the open comments on one, or to address reviewer comments on a file Devin wrote. Requires google-workspace-mcp."
---

# Reviewing Google Docs, Sheets and Slides

Devin reviews by commenting in the file, where the author works, not by sending a list in chat.
Pinned comments work on every surface: `add_comment` with `anchor` for one comment, or
`insertComment` requests through the surface's `update_*` tool for several at once; threads are
read with `list_comments` and resolved with `reply_to_comment` (`action: "resolve"`).
Signatures are in `google-workspace-mcp`.

## 1. Read the whole thing first

- Doc: `read_doc` (indexes per paragraph). Also `read_doc` with `suggestions: "accepted"` when
  the doc has pending suggestions, to review the text as it would read with them.
- Sheet: `read_sheet` with no range for the tabs, then each relevant tab; `valueRender:
  "formula"` for the formulas and `"unformatted"` for the numbers. A review of a model reads
  formulas, not just displayed values.
- Deck: `read_presentation` for text and geometry, then `download_file` as PDF (written to disk
  from `scripted_tools`) or `get_slide_thumbnail` for the slides whose layout matters.
- `list_comments` on the file: what has already been raised, what is resolved, and what is
  assigned where Google returns it. Do not repeat an open comment someone else made; reply in that thread instead.
- A re-review, or "what changed since I last looked": `list_revisions`, then diff the newest
  revision dated on or before that day against the current file (the version history rule in
  `google-workspace-mcp`) and review the changed parts, not the whole file again. If no
  revision that old is listed besides the first, or the file is a Slides deck, say the diff
  is not available and review the whole file.

Agree the brief in one line if the request is vague: what kind of review (structure, accuracy,
tone, numbers, consistency with another file) and how strict.

## 2. Decide what deserves a comment

A comment costs the author attention. Leave one where the author will act on it:
- a claim with no source or number ("40% faster" with no baseline)
- a contradiction inside the file or with a linked file
- a formula whose range stops short, hard-codes a value, or disagrees with its label
- a step, risk or decision that is missing from the section that should hold it
- wording that will be misread
Skip style nits unless asked. Group the same issue appearing many times into one comment that
names the pattern and the places. For a long file, aim for the 5-15 comments that matter and
put the rest in the summary.

Each comment: what is wrong or missing, why it matters, and the concrete fix or question, in
one to three sentences. Address the author in the second person; no "the AI noticed".

## 3. Pin each comment to the exact place

One comment: `add_comment(fileId, content, anchor)`. The tool detects the file type and runs
that surface's `insertComment`; the reply is the new thread with its `commentId`, `anchor` and
quoted text. Check the reply has an `anchor`: an empty `anchor: {}` creates an unpinned comment
with no error. A `comment_not_saved` error means Google returned success without confirming the
comment: run `list_comments` before retrying, so the author does not get it twice.

| Surface | `anchor` for `add_comment`                                              | Anchor source                                                                               |
| ------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Doc     | `{"range": {"startIndex", "endIndex", "tabId"?}}`                       | `read_doc` indexes; narrow the range to the sentence or phrase, not the whole paragraph     |
| Sheet   | `{"coordinate": {"sheetId", "rowIndex", "columnIndex"}}` (0-based)      | `sheetId` from `read_sheet` with no range; row/column from the A1 cell (B3 -> row 2, col 1) |
| Slides  | `{"objectId"}` of the shape, image, table or slide                      | element ids from `read_presentation`; speaker notes: the notes shape id. `add_comment` also takes `{shapeTextAnchor: {objectId, textRange: {type: "FIXED_RANGE", startIndex, endIndex}}}`, `{tableCellTextAnchor: {objectId, cellLocation: {rowIndex, columnIndex}, textRange}}` and `{tableAnchor: {objectId, tableRange?}}`; `textRange.type` is required |

Several comments on one file go as `insertComment` requests (one per comment,
`{...anchor, "content", "assigneeEmailAddress"?}`, with the same anchors as the table) through
`update_doc` / `update_spreadsheet` / `update_presentation`. Each reply carries
`commentThread.commentId`, `anchorId` and `plainTextQuote`: check the quote is the text you
meant. `plainTextQuote` is HTML-escaped (`it&#39;s`), so unescape it before comparing. `quote`
from `add_comment` and `list_comments` is meant to be plain text, but a server without the
latest fix still returns it escaped, so compare it in either form.

Comments are plain text; `+email@example.com` in `content` mentions and notifies that person,
`assigneeEmailAddress` assigns the thread (only when the user asked to assign or mention).
Confirm an assignment from `assigneeEmail` in the batch reply: `list_comments` does not show it,
and Google accepts addresses that do not exist.

Docs indexes do not shift when only comments are inserted, so they can go in any order. Never
edit the text and comment on it in the same call: a reviewer who was not asked to edit does not
edit.

## 4. Replying, resolving and addressing feedback

- Reply in an existing thread: `reply_to_comment(fileId, commentId, content)`, or
  `addCommentReply: {commentId, post: {content, commentAction: "RESOLVE"|"REOPEN"}}` inside the
  surface's `update_*` tool. `reply_to_comment` with `action: "resolve"` does the same from Drive.
  A reply with no `action` on a resolved thread reopens it. To keep it closed, pass
  `action: "resolve"` with the reply.
- Finding where a thread sits: `anchor` in `list_comments` is an id, not a position. A Doc's
  `kix.*` and a Sheet's `range` do not give you indexes or a cell, so find the spot from `quote`.
  Slides anchors name the page in `page` and the element in `targets`, and a target can be an
  element that has since been deleted.
- Addressing comments on a file Devin wrote: for each open thread from `list_comments`, make
  the change (`write-google-doc`, `build-google-sheet`, `build-google-slides` cover the edits),
  then reply with what changed and resolve. Threads that ask a question Devin cannot settle get
  a reply, not a resolution.
- Resolve only threads Devin addressed or the user asked to close.
- The Docs API cannot create suggestions (tracked changes). When a reviewer would normally
  suggest a rewording, put the proposed text in the comment ("Suggest: ..."); apply it directly
  only when the user asked Devin to make the edits. Existing suggestions by others can be
  accepted or rejected with `acceptSuggestion` / `rejectSuggestion: {suggestionId}` when the
  user asks.

## 5. Report

Finish with the file link and a short summary: how many comments, the two or three findings
that matter most, and anything the author should decide. Do not repeat every comment in chat.

## Worked example (Doc)

`read_doc` -> `[29-92] We add a token-bucket rate limiter in front of the public API.` ->
`add_comment(fileId, "Which bucket size and refill rate? Name the numbers here or link the
config.", anchor: {"range": {"startIndex": 29, "endIndex": 91}})` -> reply quotes the sentence ->
report "3 comments: parameters unspecified (Summary), per-org vs per-key is still open (Open
questions), no rollout plan".
