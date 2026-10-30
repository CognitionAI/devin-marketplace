---
name: write-google-doc
description: "Write a new Google Doc (design doc, spec, memo, RFC, meeting notes, report) or edit an existing one in place: create it from Markdown, then refine structure, formatting, tables, headers, links and comments with update_doc in read -> edit -> read-again loops, and check the rendered pages. Use whenever the deliverable is a Google Doc or the user asks for changes to one. Requires google-workspace-mcp."
---

# Writing and editing Google Docs

## New doc: draft in Markdown, convert once, then polish

1. **Agree the outline** in one message for anything longer than a page: title, sections, who it
   is for. For a design doc the default shape is Summary, Context / Problem, Goals and
   Non-goals, Proposal (with a diagram or table where it helps), Alternatives considered, Risks,
   Rollout / Migration, Open questions. For meeting notes: Attendees, Decisions, Action items
   (owner, due), Notes.
2. **Create from Markdown**: `create_file(name, content: <markdown>, type: "document",
   folderId?)`. Headings (`#`..`######`), bullets, numbered lists, bold/italic, links, code
   spans and pipe tables all convert. The reply's `id` / `webViewLink` is the document for the
   rest of the task; every later change is `update_doc` on it, never a second `create_file`.
3. **Read it back**: `read_doc` returns `[start-end] STYLE: text` per paragraph; confirm the
   heading levels and lists survived and note the indexes.
4. **Polish with `update_doc`** (request shapes are in the tool description): table column
   widths and header shading, `pinTableHeaderRows`, a header/footer (`createHeader` then
   `insertText` with `segmentId: headerId`), page setup (`updateDocumentStyle`), a title
   style, `createParagraphBullets` where the import left plain lines, a footnote or smart chips
   (`insertPerson`, `insertRichLink`, `insertDate`) where they add value. Keep one logical step
   per call.
5. **Check the pages**: `download_file(fileId, exportMimeType: "application/pdf")` from
   `scripted_tools`, written to disk; look at page count, orphaned headings, table overflow.
6. **Deliver** the link, and where the doc went. Offer a `share_file` only when the user named
   readers.

Templates: to fill a template doc, `copy_file` it under the final name and either
`replaceAllText` for `{{placeholders}}` or `replaceNamedRangeContent` when the template has
named ranges. Office input: `copy_file(fileId, type: "document")` converts a .docx already in
Drive.

## Editing an existing doc: loops of read -> edit -> read

- `read_doc` first, always, and re-read after each `update_doc` call: indexes are UTF-16
  offsets that shift with every insertion or deletion. Within one call, order edits from the
  highest index down.
- Replace a passage: `deleteContentRange` on `{startIndex, endIndex}` then `insertText` at
  `startIndex` (same call, delete first), or `replaceAllText` for an exact phrase that is unique.
  Keep the paragraph's trailing `\n` out of the deleted range or the paragraph merges with the next.
- Add a section: `insertText` with `endOfSegmentLocation: {}` (text starting with `\n`), or at
  the `startIndex` of the paragraph it should precede; then `updateParagraphStyle` with
  `namedStyleType: "HEADING_2"` on the heading's range and bullets with `createParagraphBullets`.
- Restyle without touching text: `updateTextStyle` / `updateParagraphStyle` with a `fields`
  mask naming only the properties being set, so the rest of the formatting survives.
- Tables: find the table's start index in `read_doc`; cells are addressed with
  `tableCellLocation: {tableStartLocation: {index}, rowIndex, columnIndex}`; insert text into a
  cell at the cell's paragraph index from `read_doc`. Add rows with `insertTableRow` before
  filling them.
- Tabs: `read_doc` names the tab (`tabId`); pass the same `tabId` in every range and location
  when the doc has more than one tab.
- Suggestions and comments: `read_doc` shows pending suggestions as `{+added+}` / `[-removed-]`;
  a review pass follows `review-google-files`. When a doc has open comments addressed to the
  user, read them (`list_comments`) before rewriting the passages they are on.
- On a doc Devin did not create, say before the first large rewrite that the change lands in
  the live file (undo via File -> Version history) and offer a `copy_file` backup.

## Style defaults

- Plain, literal language; one idea per paragraph; headings that say what the section decides,
  not just its topic. Tables for comparisons, numbered lists for sequences, bullets only for
  parallel items.
- Every number has a unit and a source; every open question has an owner where known.
- No placeholder text in a delivered doc ("TBD" only where the user said something is undecided).
- Match the existing doc's heading levels, fonts and terminology when editing; do not restyle a
  doc the user did not ask to restyle.

## Gotchas seen live

- Inserting at the document's final end index fails ("insertion index must be inside the bounds
  of an existing paragraph"): use `endOfSegmentLocation` or `endIndex - 1`.
- A heading created by inserting text takes the style of the paragraph it was inserted into;
  set `namedStyleType` explicitly.
- `replaceAllText` is document-wide and case-sensitive only with `matchCase: true`; check the
  phrase is unique in `read_doc` first.
- Images need a URL Google can fetch (`insertInlineImage: {uri}`); there is no upload path for
  a local PNG, so charts and diagrams are either rebuilt as tables/text, hosted somewhere
  fetchable, or handed to the user as files to insert.
