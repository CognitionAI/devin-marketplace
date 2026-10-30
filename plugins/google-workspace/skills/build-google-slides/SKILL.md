---
name: build-google-slides
description: "Create or edit a native Google Slides deck through the Slides MCP tools: plan the storyline, build slides from layouts and placeholders, add text, tables, images and linked Sheets charts, write speaker notes, then check every slide visually and fix it in place. Use whenever the deliverable is a Google Slides presentation or the user asks to change one, unless a brand-specific deck skill (for example cognition-slides' google-slides for Cognition-branded decks) applies, in which case that skill owns the design and this one is the tool reference. Requires google-workspace-mcp."
---

# Building Google Slides decks

Decks are judged by the eye, so the loop is: build a slide -> look at it (`get_slide_thumbnail`
or a PDF export) -> fix it -> next slide. Tool signatures: `google-workspace-mcp`. For
Cognition-branded decks the `cognition-slides` plugin's `google-slides` skill owns the design
system (fonts, colours, layouts) and calls these same tools; follow it when it is installed and
the deck is for Cognition.

## 1. Plan before touching the deck

- One sentence per slide ("what this slide proves") in a short outline the user can approve;
  5-12 slides is the default for a readout, 15-25 for a workshop. Title, agenda/summary,
  body, close/next steps.
- Audience and source material: ask for the Doc/Sheet to draw from, or search Drive for it.
- Template: if the user has a template deck, `copy_file` it under the deck's name and build on
  its layouts (`read_presentation` lists them with ids); otherwise `create_file(name, type:
  "presentation")` gives a blank 16:9 deck with one empty slide whose id is `p` (delete it at
  the end with `deleteObject`).

## 2. Build slides with layouts and placeholders

`update_presentation(presentationId, requests)`, one call per slide or per small group.

- `createSlide: {objectId: "s2", slideLayoutReference: {predefinedLayout: "TITLE_AND_BODY"},
  placeholderIdMappings: [{layoutPlaceholder: {type: "TITLE"}, objectId: "s2-title"},
  {layoutPlaceholder: {type: "BODY"}, objectId: "s2-body"}]}` then `insertText: {objectId:
  "s2-title", text}`. Predefined layouts and their placeholder types: `TITLE` (CENTERED_TITLE,
  SUBTITLE), `TITLE_AND_BODY` (TITLE, BODY), `TITLE_ONLY`, `SECTION_HEADER` (TITLE, BODY),
  `TITLE_AND_TWO_COLUMNS` (TITLE, BODY, BODY with `index` 0/1), `BLANK`. In a template deck use
  `layoutId` from `read_presentation` instead.
- Bullets: insert lines joined by `\n`, then `createParagraphBullets: {objectId, textRange:
  {type: "ALL"}, bulletPreset: "BULLET_DISC_CIRCLE_SQUARE"}`.
- Text style: `updateTextStyle` (`fontSize: {magnitude, unit: "PT"}`, `bold`,
  `foregroundColor`) with a `fields` mask; paragraph: `updateParagraphStyle`.
- Free-form elements: `createShape` / `createImage` / `createTable` / `createLine` with
  `elementProperties: {pageObjectId, size: {width, height}, transform: {scaleX: 1, scaleY: 1,
  translateX, translateY, unit: "PT"}}`. A 16:9 slide is 720 x 405 PT; keep 30-40 PT margins
  and align left edges across slides.
- Images need a fetchable URL (public, or a Drive file the user can read). Local renders
  cannot be uploaded through the MCP; use a table, native shapes or a linked chart instead.
- Charts from a Sheet: `createSheetsChart: {spreadsheetId, chartId, linkingMode: "LINKED",
  elementProperties}`; the `chartId` comes from the `addChart` reply or `read_sheet` details,
  and `LINKED` keeps it refreshable from the deck. Tables: `createTable {rows, columns}` then
  `insertText` with `cellLocation`.
- Speaker notes: `read_presentation` gives each slide's notes shape id; `insertText` into it.
- Order: `updateSlidesPosition`; duplicate a good slide with `duplicateObject` and edit the copy.

## 3. Look at every slide

After each slide or batch: `get_slide_thumbnail(presentationId, slideId, size: "medium")` and
check for text overflowing its box, overlapping elements, empty placeholders (they render as
"Click to add text"), inconsistent title positions, unreadable sizes (< 12 PT body text). For
the finished deck, `download_file(presentationId, exportMimeType: "application/pdf")` from
`scripted_tools` and page through it. Fix in place: `deleteText` + `insertText`, resize with
`updatePageElementTransform`, shorten copy. A text box that overflows means less text, not a
smaller font below 12 PT.

## 4. Editing an existing deck

- `read_presentation` first: slide ids, element ids, current text and positions. Re-read after
  structural changes (new slides, deletions).
- Replace text while keeping styling: `deleteText {textRange: {type: "ALL"}}` then `insertText`
  at index 0 in the same request list; or `replaceAllText` across the deck for a renamed term.
- Swap an image: `replaceImage {imageObjectId, url}`; refresh linked charts:
  `refreshSheetsChart`.
- Match the deck's existing layouts (`slideLayoutReference: {layoutId}` of a sibling slide) so
  new slides look like the old ones; thumbnail the new slide next to an existing one.
- Reviewer mode (comments instead of edits): `review-google-files`.

## 5. Deliver

Link, slide count, where it lives, and anything that still needs a human asset (a logo, a
photo, a number to confirm). Offer `share_file` only for named recipients.

## Gotchas

- `objectId`s are yours to choose (5-50 chars, letters/digits/`_`/`-`), unique per deck; a
  reused id fails the whole call.
- Inserting into a placeholder that has no text yet uses `insertionIndex: 0` (default);
  `insertText` into a non-text element (image, line) fails.
- Slides' default slide `p` in a new blank deck is a `TITLE` layout slide with empty
  placeholders; fill it or delete it, never ship it empty.
- Page size cannot be changed via the API; start from a template with the right size.
- Thumbnails show the slide as rendered, including template backgrounds: trust them over
  the element list when they disagree.
