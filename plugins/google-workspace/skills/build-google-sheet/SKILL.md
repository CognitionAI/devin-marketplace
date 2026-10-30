---
name: build-google-sheet
description: "Build or extend a Google Sheet that does real work: financial models, budgets, P&L and cash-flow statements, accounting ledgers and reconciliations, trackers, dashboards and data tables with formulas, number formats, validation, conditional formatting, named ranges, protection and charts, then verify it computes. Use whenever the deliverable is a spreadsheet or the user asks for changes to one. Requires google-workspace-mcp."
---

# Building spreadsheets that compute

A good sheet separates inputs from logic, uses formulas rather than pasted numbers, labels
every row, formats so numbers read at a glance, and proves itself with check rows. Devin
builds it in passes, reading back after each one. Tool signatures: `google-workspace-mcp`.

## Pass 0: agree the shape

For a model or statement, confirm in one message: periods (months/quarters/years and how
many), currency and units, the inputs the user controls, the outputs they care about, and
whether existing data should be imported. Default layout for a model:

- `Inputs` tab: one assumption per row (label, value, unit/notes); the only cells a user edits.
- One tab per statement or calculation (`P&L`, `Cash flow`, `Headcount`...): row labels in
  column A, periods across columns, every number a formula referencing `Inputs` or the row above.
- `Checks` rows (or tab): identities that must hold (balance sheet balances, totals match the
  source, no negative inventory), showing `ok` / `CHECK`.
- `Data` tabs for raw imports, untouched by formulas; summaries pull from them with
  `SUMIFS` / `QUERY` / `FILTER`.

For a ledger/reconciliation: a transactions table with a header row, consistent columns
(date, account, description, debit, credit, balance), the balance as a running formula, a
trial-balance or reconciliation tab with `SUMIFS` by account and a difference row.

## Pass 1: create the workbook and tabs

- New file: `create_file(name, type: "spreadsheet", folderId?)`, optionally with CSV `content`
  for a first data tab. Then `read_sheet(spreadsheetId)` for the default `sheetId`.
- Tabs: `update_spreadsheet` with `addSheet: {properties: {title, gridProperties: {rowCount,
  columnCount, frozenRowCount: 1}}}`; rename the default tab with `updateSheetProperties`
  (`fields: "title"`). The replies carry each new `sheetId`: keep them, every later grid
  request needs them.
- Existing workbook: `read_sheet` with no range (tabs, sizes, named ranges) and the ranges in
  play with `valueRender: "formula"` before changing anything. Never overwrite a tab you have
  not read.

## Pass 2: write values and formulas

`write_sheet(spreadsheetId, range: "'Inputs'!A1", values: [[...], ...])`: a 2-D array laid
down from the top-left cell. Strings that look like formulas, numbers, dates (`2027-01-01`)
or percents (`12%`) are parsed as such; `raw: true` keeps them literal (ids, zip codes).

- Write formulas as strings (`"=Inputs!$B$2*(1+Inputs!$B$3)^(B$1-1)"`), build the per-period
  row in code so each column's references are right, and keep absolute references (`$B$2`) on
  inputs. Cross-tab references use `'Tab name'!A1`.
- Prefer one formula pattern per row over hand-typed values; prefer `SUMIFS`, `XLOOKUP`/
  `INDEX-MATCH`, `IFERROR`, `ARRAYFORMULA`, `QUERY`, `SEQUENCE`/`EDATE` for period headers.
- Appending transactions: `write_sheet(range: "'Ledger'!A:F", values, append: true)`.
- Lay down labels and headers in the same write so the sheet is never half-labelled.

## Pass 3: make it readable and safe (`update_spreadsheet`)

| Need                                   | Request                                                                                                                                                                                   |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Currency / percent / date formats      | `repeatCell` with `cell.userEnteredFormat.numberFormat: {type: "CURRENCY", pattern: "$#,##0;($#,##0)"}` (or `PERCENT` `0.0%`, `DATE` `mmm yyyy`), `fields: "userEnteredFormat.numberFormat"` |
| Bold header, fill, borders, wrap       | `repeatCell` with `textFormat.bold`, `backgroundColor`, `horizontalAlignment`; `updateBorders`                                                                                            |
| Freeze headers / label column          | `updateSheetProperties` `gridProperties.frozenRowCount` / `frozenColumnCount`                                                                                                             |
| Column widths                          | `autoResizeDimensions` or `updateDimensionProperties` (`pixelSize`)                                                                                                                       |
| Input cells visibly editable           | light fill on `Inputs!B` cells; `setDataValidation` (`NUMBER_BETWEEN`, `ONE_OF_LIST` for dropdowns, `DATE_IS_VALID`) with `strict: true`                                                  |
| Protect formula tabs                   | `addProtectedRange` with `warningOnly: true` (users get a warning, not a lock-out) on each calculation tab                                                                                |
| Flag problems                          | `addConditionalFormatRule` (`NUMBER_LESS` 0 -> red text; `TEXT_EQ` "CHECK" -> red fill; `CUSTOM_FORMULA` for row-wise rules)                                                              |
| Names for key inputs                   | `addNamedRange` (`growth_rate` = `Inputs!B3`) so formulas read `=Revenue*(1+growth_rate)`                                                                                                 |
| Charts                                 | `addChart` with `spec.basicChart` (`COLUMN`, `LINE`, `BAR`) or `pieChart`; `domains`/`series` as `sourceRange`s; position with `anchorCell`; reply has `chartId`                           |
| Totals / grouping                      | `addDimensionGroup`; `autoFill`; `sortRange`; `setBasicFilter` on data tabs                                                                                                                |

Grid ranges: `{sheetId, startRowIndex, endRowIndex, startColumnIndex, endColumnIndex}`,
0-based, end-exclusive; omit an end to run to the sheet edge. Group related requests in one
call per tab; the whole call fails if one request is wrong, so a failure names
`requests[<n>]` to fix.

## Pass 4: verify it computes

- `read_sheet(range, valueRender: "unformatted")` on every output row: no `#REF!`, `#DIV/0!`,
  `#NAME?`, `#N/A`; totals equal the sum of their parts; check rows say `ok`.
- `read_sheet(range, valueRender: "formula")` on one column: references point where intended
  (off-by-one columns are the common bug).
- Recompute two or three headline numbers independently (from the inputs, in code) and compare.
- For a rendered check, `download_file(spreadsheetId, exportMimeType: "application/pdf")` (or
  xlsx) from `scripted_tools`.
- Fix with `write_sheet` / `update_spreadsheet` on the same file; do not create a new one.

## Deliver

Link, where it lives, which tab holds the inputs, and the one or two assumptions the user
should confirm. Mention anything imported that did not fit (unparsed dates, blank ids).

## Conventions and gotchas

- Displayed values are strings (`"$100,000"`): compare numbers with `valueRender: "unformatted"`.
- `write_sheet` cannot extend a tab beyond its `rowCount` / `columnCount`: grow it first with
  `appendDimension` or `updateSheetProperties`.
- Tab names with spaces or symbols need quotes in A1 ranges (`'P&L'!A1:G12`).
- `update_file content=...` replaces the whole workbook with a single CSV tab; for a workbook
  with several tabs use `write_sheet` / `update_spreadsheet`.
- Never hard-code a computed number into a cell the user will trust as a formula; if a value
  must be pasted (an external actual), mark the cell as an input.
- Dates: write ISO strings and format the column with a `DATE` number format. `read_sheet`
  returns dates as displayed strings even with `valueRender: "unformatted"`; `dateTimeRender:
  "serial"` gives the serial day numbers for arithmetic.
- Charts and conditional formats reference `sheetId`s; renaming a tab is safe, deleting and
  re-adding one is not.
