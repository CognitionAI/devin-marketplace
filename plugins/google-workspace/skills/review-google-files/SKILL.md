---
name: review-google-files
description: "Review a Google Doc, Sheet or Slides deck the way a careful colleague would, leaving comments anchored to the exact passage, cell or shape, replying in existing threads and resolving them, and reporting back. Use whenever the user asks Devin to review, give feedback on, check, proofread, fact-check, sanity-check or 'leave comments on' a Doc, Sheet or deck, to work through the open comments on one, or to address reviewer comments on a file Devin wrote. Requires google-workspace-mcp."
---

# Reviewing Google Docs, Sheets and Slides

Devin reviews by commenting in the file, where the author works, not by sending a list in chat.
Anchored comments are available on every surface through the `update_*` tool of that surface
(`insertComment`), threads are read with `list_comments`, and `addCommentReply` with
`commentAction: "RESOLVE"` closes them. Signatures are in `google-workspace-mcp`.

## 1. Read the whole thing first

- Doc: `read_doc` (indexes per paragraph). Also `read_doc` with `suggestions: "accepted"` when
  the doc has pending suggestions, to review the text as it would read with them.
- Sheet: `read_sheet` with no range for the tabs, then each relevant tab; `valueRender:
  "formula"` for the formulas and `"unformatted"` for the numbers. A review of a model reads
  formulas, not just displayed values.
- Deck: `read_presentation` for text and geometry, then `download_file` as PDF (written to disk
  from `scripted_tools`) or `get_slide_thumbnail` for the slides whose layout matters.
- `list_comments` on the file: what has already been raised, what is resolved, what is
  assigned. Do not repeat an open comment someone else made; reply in that thread instead.

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

## 3. Anchor each comment to the exact place

| Surface | Request (inside the surface's `update_*` tool)                                                                                                   | Anchor source                                        |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Doc     | `update_doc`: `{"insertComment": {"range": {"startIndex", "endIndex", "tabId"?}, "content", "assigneeEmailAddress"?}}`                             | `read_doc` indexes; narrow the range to the sentence or phrase, not the whole paragraph |
| Sheet   | `update_spreadsheet`: `{"insertComment": {"coordinate": {"sheetId", "rowIndex", "columnIndex"}, "content", "assigneeEmailAddress"?}}` (0-based)  | `sheetId` from `read_sheet` with no range; row/column from the A1 cell (B3 -> row 2, col 1) |
| Slides  | `update_presentation`: `{"insertComment": {"shapeTextAnchor": {"objectId", "textRange": {"type": "FIXED_RANGE", "startIndex", "endIndex"}}, "content"}}`; `tableCellTextAnchor: {objectId, cellLocation: {rowIndex, columnIndex}, textRange}`; `tableAnchor: {objectId, tableRange?}`; or `objectId` alone for a whole shape, image or slide | element ids and text from `read_presentation`; speaker notes: the notes shape id |

The reply carries the new `commentThread.commentId`, `anchorId` and `plainTextQuote`: check
the quote is the text you meant. Comments are plain text; `+email@example.com` in `content`
mentions and notifies that person, `assigneeEmailAddress` assigns the thread (only when the
user asked to assign or mention).

Several comments go in one `update_*` call per file (one request each). Docs indexes do not
shift when only comments are inserted, so they can go in any order. Never edit the text and
comment on it in the same call: a reviewer who was not asked to edit does not edit.

## 4. Replying, resolving and addressing feedback

- Reply in an existing thread: `reply_to_comment(fileId, commentId, content)`, or
  `addCommentReply: {commentId, post: {content, commentAction: "RESOLVE"|"REOPEN"}}` inside the
  surface's `update_*` tool. `reply_to_comment` with `action: "resolve"` does the same from Drive.
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
`update_doc` with `insertComment` on `{"startIndex": 29, "endIndex": 91}` ("Which bucket size
and refill rate? Name the numbers here or link the config.") -> reply quotes the sentence ->
report "3 comments: parameters unspecified (Summary), per-org vs per-key is still open (Open
questions), no rollout plan".
