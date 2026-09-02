# DOCX Report Format — Implementation Guide

This file provides the complete docx-js implementation patterns for generating branded reports. Read brand tokens dynamically: `brand/custom.json` (if exists) → `brand/enterpret.json` fallback.

---

## Full Document Scaffold

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, ExternalHyperlink, PageNumber, PageBreak, LevelFormat,
        TabStopType, TabStopPosition, ImageRun } = require('docx');
const fs = require('fs');

// Brand tokens — loaded dynamically from brand/*.json
// BRAND object is resolved by report-engine SKILL.md (custom.json → enterpret.json fallback)
// All {ORG_NAME} and {ORG_SLUG} vars are already resolved when this code runs

// Chorus design system tokens — loaded from brand/enterpret.json (or custom.json override)
const BRAND = {
  colors: {
    primary: "0F6773",       // Chorus Teal 600
    primaryDark: "0C5260",   // Chorus Teal 700
    primaryLight: "E6F3F5",  // Chorus Teal 100
    accent: "2A9EAD",        // Chorus accent teal
    text: "1C1A18",          // Warm neutral N900
    textSecondary: "7A756F", // Warm neutral N600
    border: "E2DFDB",        // Warm neutral N300
    tableHeader: "0F6773",   // Teal 600
    tableHeaderText: "FFFFFF",
    altRow: "F9F8F7",        // Warm neutral N100
    positive: "67BB98",      // Jade (Chorus botanical)
    negative: "F99294",      // Coral (Chorus warm)
    neutral: "9495A2"        // Slate (Chorus cool)
  },
  font: "Arial",             // Geist not available in docx; Arial as fallback
  orgName: "Acme Corp",           // from context/organization.json
  citationBaseUrl: "https://dashboard.enterpret.com/acme-corp/record/"
};

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: BRAND.font, size: 22 } } // 11pt
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: BRAND.font, color: BRAND.colors.primary },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: BRAND.font, color: BRAND.colors.primary },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 }
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: BRAND.font, color: BRAND.colors.text },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
      }
    ]
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 }, // US Letter
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BRAND.colors.primary, space: 4 } },
            spacing: { after: 200 },
            children: [
              new TextRun({ text: BRAND.orgName, bold: true, font: BRAND.font, size: 20, color: BRAND.colors.primary }),
              new TextRun({ text: "  |  Customer Intelligence Report", font: BRAND.font, size: 18, color: BRAND.colors.textSecondary })
            ]
          })
        ]
      })
    },
    footers: {
      default: new Footer({
        children: [
          // Separator line
          new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 2, color: BRAND.colors.border, space: 4 } },
            spacing: { after: 0 }
          }),
          // Two-cell borderless table for bottom-aligned logo + page number
          new Table({
            width: { size: 9360, type: WidthType.DXA },
            columnWidths: [6000, 3360],
            borders: {
              top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
              left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
              insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE }
            },
            rows: [new TableRow({
              children: [
                new TableCell({
                  verticalAlign: 'bottom',
                  width: { size: 6000, type: WidthType.DXA },
                  borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                             left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                  margins: { top: 0, bottom: 0, left: 0, right: 0 },
                  children: [new Paragraph({
                    spacing: { before: 0, after: 0 },
                    children: [
                      new ImageRun({
                        data: fs.readFileSync('brand/enterpret-wordmark.png'),
                        transformation: { width: 60, height: 12 },
                        type: 'png'
                      }),
                      new TextRun({ text: "  Powered by Enterpret | via Claude Code", font: BRAND.font, size: 16, color: BRAND.colors.textSecondary })
                    ]
                  })]
                }),
                new TableCell({
                  verticalAlign: 'bottom',
                  width: { size: 3360, type: WidthType.DXA },
                  borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                             left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                  margins: { top: 0, bottom: 0, left: 0, right: 0 },
                  children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    spacing: { before: 0, after: 0 },
                    children: [
                      new TextRun({ text: "Page ", font: BRAND.font, size: 16, color: BRAND.colors.textSecondary }),
                      new TextRun({ children: [PageNumber.CURRENT], font: BRAND.font, size: 16, color: BRAND.colors.textSecondary })
                    ]
                  })]
                })
              ]
            })]
          })
        ]
      })
    },
    children: [
      // TITLE
      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "REPORT TITLE HERE", bold: true, font: BRAND.font, size: 36, color: BRAND.colors.primary })]
      }),
      // SUBTITLE (date, region, scope)
      new Paragraph({
        spacing: { after: 360 },
        children: [new TextRun({ text: "Date Range | Region | Scope", font: BRAND.font, size: 22, color: BRAND.colors.textSecondary })]
      }),
      // ... report content sections ...
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/path/to/output.docx", buffer);
});
```

---

## Component Patterns

### Executive Summary Box

```javascript
function execSummaryItem(text) {
  return new Paragraph({
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: BRAND.colors.accent, space: 8 } },
    indent: { left: 200 },
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, font: BRAND.font, size: 22, color: BRAND.colors.text })]
  });
}
```

### Data Table

```javascript
function createTable(headers, rows, columnWidths) {
  const totalWidth = columnWidths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 1, color: BRAND.colors.border };
  const borders = { top: border, bottom: border, left: border, right: border };

  const headerRow = new TableRow({
    children: headers.map((h, i) =>
      new TableCell({
        borders,
        width: { size: columnWidths[i], type: WidthType.DXA },
        shading: { fill: BRAND.colors.tableHeader, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: h, bold: true, font: BRAND.font, size: 20, color: BRAND.colors.tableHeaderText })]
        })]
      })
    )
  });

  const dataRows = rows.map((row, rowIdx) =>
    new TableRow({
      children: row.map((cell, i) =>
        new TableCell({
          borders,
          width: { size: columnWidths[i], type: WidthType.DXA },
          shading: rowIdx % 2 === 1 ? { fill: BRAND.colors.altRow, type: ShadingType.CLEAR } : undefined,
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({
            children: [new TextRun({ text: String(cell), font: BRAND.font, size: 20, color: BRAND.colors.text })]
          })]
        })
      )
    })
  );

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths,
    rows: [headerRow, ...dataRows]
  });
}
```

### Citation Link

```javascript
function citationLink(recordId) {
  return new ExternalHyperlink({
    children: [new TextRun({
      text: "[View in Enterpret]",
      style: "Hyperlink",
      font: BRAND.font,
      size: 18,
      color: BRAND.colors.accent
    })],
    link: `${BRAND.citationBaseUrl}${recordId}`
  });
}
```

### Verbatim Quote Block

```javascript
function verbatimQuote(text, date, recordId) {
  return [
    new Paragraph({
      indent: { left: 400 },
      border: { left: { style: BorderStyle.SINGLE, size: 4, color: BRAND.colors.border, space: 8 } },
      spacing: { before: 80, after: 40 },
      children: [
        new TextRun({ text: `"${text}"`, italics: true, font: BRAND.font, size: 20, color: BRAND.colors.text })
      ]
    }),
    new Paragraph({
      indent: { left: 400 },
      spacing: { after: 120 },
      children: [
        new TextRun({ text: `— ${date}  `, font: BRAND.font, size: 18, color: BRAND.colors.textSecondary }),
        citationLink(recordId)
      ]
    })
  ];
}
```

### Sentiment Badge (inline text)

```javascript
function sentimentText(sentiment, volume) {
  const colorMap = { "Positive": BRAND.colors.positive, "Negative": BRAND.colors.negative, "Neutral": BRAND.colors.neutral };
  return new TextRun({
    text: `${sentiment}: ${volume}`,
    font: BRAND.font,
    size: 20,
    color: colorMap[sentiment] || BRAND.colors.text,
    bold: sentiment === "Negative"
  });
}
```

### Section Heading with Count

```javascript
function sectionHeading(title, count) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [
      new TextRun({ text: title, bold: true, font: BRAND.font, size: 28 }),
      count !== undefined ? new TextRun({ text: ` (${count})`, font: BRAND.font, size: 28, color: BRAND.colors.textSecondary }) : undefined
    ].filter(Boolean)
  });
}
```

### WoW Change Indicator

```javascript
function wowChange(current, previous) {
  if (previous === 0) return "New";
  const pct = Math.round(((current - previous) / previous) * 100);
  if (pct > 0) return `↑ ${pct}%`;
  if (pct < 0) return `↓ ${Math.abs(pct)}%`;
  return "—";
}
```

---

## File Naming Convention

```
{report_type}_{region}_{YYYY-MM-DD}.docx
```

Examples:
- `customer_digest_US_2026-03-05.docx`
- `investigation_login_failures_2026-03-05.docx`
- `theme_deep_dive_global_2026-03-05.docx`
