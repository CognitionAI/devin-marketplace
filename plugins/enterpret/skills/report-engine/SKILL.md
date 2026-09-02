---
name: report-engine
description: >
  Guides Claude through the 4-phase report workflow (Scope → Query → Draft → Final)
  and produces output in multiple formats (docx, pptx, html) with dynamic branding.
  Loads brand tokens from custom.json (if exists) or enterpret.json default.
  Auto-loads for any report-generating command.
version: 5.0.0
---

# Report Engine — 4-Phase Workflow with Multi-Format Output

## Overview

Every report follows a mandatory 4-phase workflow. The user always reviews a markdown draft before the final output is generated. This prevents wasted effort and ensures accuracy.

## Brand Loading

Before generating any output, load brand tokens:

1. **Check for `brand/custom.json`** — if it exists, load it as the primary brand
2. **Fall back to `brand/enterpret.json`** — the Enterpret default palette
3. **Shallow merge** — if `custom.json` exists, merge its fields over `enterpret.json` (custom overrides only the fields it specifies; unspecified fields use Enterpret defaults)
4. **Resolve template variables:**
   - `{ORG_NAME}` → `context/organization.json` → `name`
   - `{ORG_SLUG}` → `context/organization.json` → `slug`
   - Apply to all brand fields: `name`, `footer.dashboardUrl`, `citations.baseUrl`, etc.

The resolved brand object is referred to as `BRAND` throughout all format-specific reference files.

## The 4 Phases

### Phase 1: Scope

**Purpose:** Confirm what the report should cover before querying any data.

Ask the user (conversationally, not as a checklist):

| Parameter | Question | Default |
|-----------|----------|---------|
| **Audience** | "Who will read this?" | Mixed (leadership + ops) |
| **Time period** | "What date range?" | Last 7 days |
| **Region** | "Any region filter?" | All regions |
| **Goal** | "What question are you trying to answer?" | General overview |
| **Focus** | "Any specific topics or categories to focus on?" | None |

**Rules:**
- Ask 2-3 questions max. Don't interrogate.
- If the user provides context in their command (e.g., `/customer-digest US last week`), extract parameters from that and confirm.
- Always confirm the scope before proceeding: "I'll pull [time range] data for [region/topic], aimed at [audience]. Sound right?"

### Phase 2: Query

**Purpose:** Pull data from the Wisdom Knowledge Graph.

1. Load the `wisdom-kg` skill for query patterns and rules
2. Execute queries based on the report type (see `wisdom-kg` SKILL.md → Query Strategy)
3. Collect: theme volumes, sentiment, WoW changes, verbatim evidence with citation IDs
4. If a query fails, simplify and retry (never present failed query results)

**Rules:**
- Always run the pre-flight check first: call `get_organization_details` to verify auth
- If auth fails, tell the user to run `/start` to re-authenticate
- Run queries sequentially, not in parallel (to handle errors gracefully)
- Always collect `feedback_record_id` for citations

### Phase 3: Draft

**Purpose:** Present a structured markdown draft for user review.

Present the report draft directly in chat as markdown. Structure depends on the report type (see `references/report-templates.md`), but always includes:

1. **Executive Summary** — 3-5 bullet points of key findings
2. **Data sections** — Tables, ranked lists, themed groupings
3. **Evidence** — Verbatim quotes with citation links
4. **Recommendations** — Actionable next steps framed as product decisions

**Rules:**
- Always say: "Here's the draft. Want me to adjust anything before I generate the final report?"
- Wait for user approval or edits before proceeding to Phase 4
- If the user requests changes, update the draft and re-present

### Phase 4: Final (Multi-Format Output)

**Purpose:** Generate branded output from the approved draft.

#### Step 4a: Choose Format

Ask: "What format would you like?"
- **docx** — Word document (default, best for sharing and editing)
- **pptx** — Executive summary deck (5-8 slides, best for presentations)
- **html** — Self-contained HTML with interactive charts (best for web/email)
- **all** — Generate all three formats

Default: docx

#### Step 4b: Generate Charts

Before building the document, generate chart images for each report section that supports them. See `references/chart-patterns.md` for config recipes and `references/report-templates.md` for which sections get which chart type.

1. Build the Chart.js config object for each chart using `BRAND.chart.*` colors
2. Call `generateChart(config, width, height)` to fetch a PNG buffer from QuickChart API
3. If any chart fails (`null` return), skip it — charts never block report generation
4. Store buffers for use in Step 4c

#### Step 4c: Build Document

Route to the appropriate format-specific reference:

| Format | Reference File | Key Approach |
|--------|---------------|--------------|
| docx | `references/report-format-docx.md` | docx-js (npm `docx` package) |
| pptx | `references/report-format-pptx.md` | pptxgenjs |
| html | `references/report-format-html.md` | Self-contained HTML + Chart.js CDN |

**For each format:**
1. Apply `BRAND` tokens (colors, typography, footer text)
2. Embed charts where applicable
3. Include citation hyperlinks using `BRAND.citations.baseUrl`
4. Save with appropriate file extension

**File naming:** `{report_type}_{region}_{date}.{ext}`
- Example: `customer_digest_US_2026-03-05.docx`
- Example: `investigation_login_failures_2026-03-05.pptx`

**After generation:**
- Save the file(s) to the workspace folder
- Present a link: `[View your report](computer:///path/to/file.ext)`
- Briefly state: "Your {report_type} is ready. It covers {scope summary}."

**Integration nudge (optional):**
If the user has Notion or other MCP servers configured, offer: "Want me to also publish this to Notion / share via Slack?"

---

## DOCX Implementation Reference

### Setup

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, ExternalHyperlink, PageNumber, PageBreak, LevelFormat,
        ImageRun } = require('docx');
const fs = require('fs');
```

### Critical docx-js Rules

1. **Set page size explicitly** — US Letter: `width: 12240, height: 15840`
2. **Never use `\n`** — use separate Paragraph elements
3. **Never use unicode bullets** — use `LevelFormat.BULLET` numbering config
4. **Tables need dual widths** — `columnWidths` on table AND `width` on each cell
5. **Always use `WidthType.DXA`** — never PERCENTAGE
6. **Use `ShadingType.CLEAR`** — never SOLID for table backgrounds
7. **Never use tables as dividers** — use Paragraph border instead
8. **ImageRun requires `type`** — always specify png/jpg
9. **Charts are generated via QuickChart API** — see `references/chart-patterns.md`
10. **Charts supplement tables** — always place chart ABOVE its data table
11. **Chart failure is silent** — if `generateChart()` returns `null`, skip the chart

---

## Reference Files

- `references/report-templates.md` — Structural templates for each report type + archetypes
- `references/report-format-docx.md` — Full docx-js implementation patterns and styling
- `references/report-format-pptx.md` — pptxgenjs executive summary deck patterns
- `references/report-format-html.md` — Self-contained HTML + Chart.js template
- `references/chart-patterns.md` — QuickChart API chart generation and embedding patterns
