# PPTX Report Format — Executive Summary Deck

This file provides pptxgenjs implementation patterns for generating branded executive summary slide decks (5-8 slides). Designed for stakeholder presentations — concise, visual, high-impact.

---

## Setup

```javascript
const PptxGenJS = require('pptxgenjs');
const fs = require('fs');

// BRAND object is resolved by report-engine SKILL.md
// All template vars ({ORG_NAME}, {ORG_SLUG}) are already resolved

const pptx = new PptxGenJS();

// Master slide layout
pptx.defineLayout({ name: 'CUSTOM_16x9', width: 13.33, height: 7.5 });
pptx.layout = 'CUSTOM_16x9';
```

---

## Master Slide Definition

```javascript
pptx.defineSlideMaster({
  title: 'BRANDED_MASTER',
  background: { fill: 'FFFFFF' },
  objects: [
    // Top brand bar
    {
      rect: {
        x: 0, y: 0, w: 13.33, h: 0.5,
        fill: { color: BRAND.colors.primary }
      }
    },
    // Footer bar — Chorus warm neutral
    {
      rect: {
        x: 0, y: 7.0, w: 13.33, h: 0.5,
        fill: { color: 'F9F8F7' }
      }
    },
    // Footer text — left
    {
      text: {
        text: 'Powered by Enterpret | via Claude Code',
        options: {
          x: 0.5, y: 7.05, w: 6, h: 0.4,
          fontSize: 9, color: BRAND.colors.textSecondary,
          fontFace: BRAND.font
        }
      }
    },
    // Footer text — right (slide number)
    {
      text: {
        text: [{ text: 'Slide ', options: { fontSize: 9, color: BRAND.colors.textSecondary } }],
        options: {
          x: 11, y: 7.05, w: 2, h: 0.4,
          align: 'right', fontSize: 9, color: BRAND.colors.textSecondary,
          fontFace: BRAND.font
        }
      }
    }
  ],
  slideNumber: { x: 12.5, y: 7.05, fontSize: 9, color: BRAND.colors.textSecondary }
});
```

---

## Slide Templates (8 types)

### 1. Title Slide

```javascript
function addTitleSlide(title, subtitle, date) {
  const slide = pptx.addSlide({ masterName: 'BRANDED_MASTER' });

  // Full brand background for title
  slide.addShape('rect', { x: 0, y: 0, w: 13.33, h: 7.5, fill: { color: BRAND.colors.primary } });

  // Title
  slide.addText(title, {
    x: 1, y: 2, w: 11, h: 1.5,
    fontSize: 36, bold: true, color: 'FFFFFF',
    fontFace: BRAND.font, align: 'left'
  });

  // Subtitle
  slide.addText(subtitle, {
    x: 1, y: 3.5, w: 11, h: 0.8,
    fontSize: 18, color: BRAND.colors.accent,
    fontFace: BRAND.font, align: 'left'
  });

  // Date
  slide.addText(date, {
    x: 1, y: 4.5, w: 11, h: 0.5,
    fontSize: 14, color: 'CCCCCC',
    fontFace: BRAND.font, align: 'left'
  });

  // Enterpret wordmark
  slide.addImage({
    path: 'brand/enterpret-wordmark.png',
    x: 1, y: 6, w: 1.2, h: 0.24
  });

  return slide;
}
```

### 2. Key Metrics Dashboard

```javascript
function addMetricsSlide(title, metrics) {
  // metrics = [{ label, value, change, sentiment }]
  const slide = pptx.addSlide({ masterName: 'BRANDED_MASTER' });

  slide.addText(title, {
    x: 0.5, y: 0.7, w: 12, h: 0.6,
    fontSize: 24, bold: true, color: BRAND.colors.primary,
    fontFace: BRAND.font
  });

  const cols = Math.min(metrics.length, 4);
  const cardWidth = (12 / cols) - 0.3;

  metrics.slice(0, 4).forEach((m, i) => {
    const x = 0.5 + i * (cardWidth + 0.3);
    const changeColor = m.change?.startsWith('↑') ? BRAND.colors.negative
                      : m.change?.startsWith('↓') ? BRAND.colors.positive
                      : BRAND.colors.textSecondary;

    // Card background
    slide.addShape('rect', {
      x, y: 1.6, w: cardWidth, h: 2.5,
      fill: { color: 'F8F9FA' }, rectRadius: 0.1
    });

    // Metric value
    slide.addText(String(m.value), {
      x, y: 1.8, w: cardWidth, h: 1,
      fontSize: 36, bold: true, color: BRAND.colors.primary,
      fontFace: BRAND.font, align: 'center'
    });

    // Metric label
    slide.addText(m.label, {
      x, y: 2.8, w: cardWidth, h: 0.5,
      fontSize: 12, color: BRAND.colors.textSecondary,
      fontFace: BRAND.font, align: 'center'
    });

    // Change indicator
    if (m.change) {
      slide.addText(m.change, {
        x, y: 3.3, w: cardWidth, h: 0.5,
        fontSize: 14, bold: true, color: changeColor,
        fontFace: BRAND.font, align: 'center'
      });
    }
  });

  return slide;
}
```

### 3. Top Themes Chart + Table

```javascript
function addThemesSlide(title, chartBuffer, tableData) {
  // tableData = { headers: [...], rows: [[...], ...] }
  const slide = pptx.addSlide({ masterName: 'BRANDED_MASTER' });

  slide.addText(title, {
    x: 0.5, y: 0.7, w: 12, h: 0.6,
    fontSize: 24, bold: true, color: BRAND.colors.primary,
    fontFace: BRAND.font
  });

  if (chartBuffer) {
    // Chart on left half
    slide.addImage({
      data: `data:image/png;base64,${chartBuffer.toString('base64')}`,
      x: 0.3, y: 1.5, w: 6, h: 4.5
    });

    // Table on right half
    if (tableData) {
      const tableRows = [tableData.headers, ...tableData.rows.slice(0, 8)];
      slide.addTable(tableRows, {
        x: 6.5, y: 1.5, w: 6.5,
        fontSize: 10, fontFace: BRAND.font,
        border: { pt: 0.5, color: BRAND.colors.border },
        colW: tableData.colWidths || undefined,
        rowH: 0.4,
        autoPage: false
      });
    }
  } else if (tableData) {
    // Full-width table
    const tableRows = [tableData.headers, ...tableData.rows.slice(0, 12)];
    slide.addTable(tableRows, {
      x: 0.5, y: 1.5, w: 12,
      fontSize: 11, fontFace: BRAND.font,
      border: { pt: 0.5, color: BRAND.colors.border },
      rowH: 0.4,
      autoPage: false
    });
  }

  return slide;
}
```

### 4. Sentiment Overview

```javascript
function addSentimentSlide(title, chartBuffer, sentimentData) {
  // sentimentData = { positive: N, negative: N, neutral: N }
  const slide = pptx.addSlide({ masterName: 'BRANDED_MASTER' });

  slide.addText(title, {
    x: 0.5, y: 0.7, w: 12, h: 0.6,
    fontSize: 24, bold: true, color: BRAND.colors.primary,
    fontFace: BRAND.font
  });

  if (chartBuffer) {
    slide.addImage({
      data: `data:image/png;base64,${chartBuffer.toString('base64')}`,
      x: 1, y: 1.5, w: 5, h: 4
    });
  }

  // Sentiment cards on right
  const sentiments = [
    { label: 'Positive', value: sentimentData.positive, color: BRAND.colors.positive },
    { label: 'Negative', value: sentimentData.negative, color: BRAND.colors.negative },
    { label: 'Neutral', value: sentimentData.neutral, color: BRAND.colors.neutral }
  ];

  sentiments.forEach((s, i) => {
    const y = 1.8 + i * 1.5;
    slide.addShape('rect', { x: 7, y, w: 0.15, h: 1, fill: { color: s.color } });
    slide.addText(String(s.value), {
      x: 7.5, y, w: 4, h: 0.6,
      fontSize: 28, bold: true, color: BRAND.colors.text,
      fontFace: BRAND.font
    });
    slide.addText(s.label, {
      x: 7.5, y: y + 0.5, w: 4, h: 0.4,
      fontSize: 14, color: BRAND.colors.textSecondary,
      fontFace: BRAND.font
    });
  });

  return slide;
}
```

### 5–6. Findings Slides (reusable)

```javascript
function addFindingsSlide(title, findings) {
  // findings = [{ heading, body, citation }]
  const slide = pptx.addSlide({ masterName: 'BRANDED_MASTER' });

  slide.addText(title, {
    x: 0.5, y: 0.7, w: 12, h: 0.6,
    fontSize: 24, bold: true, color: BRAND.colors.primary,
    fontFace: BRAND.font
  });

  findings.slice(0, 4).forEach((f, i) => {
    const y = 1.5 + i * 1.3;

    // Accent dot
    slide.addShape('ellipse', {
      x: 0.5, y: y + 0.1, w: 0.2, h: 0.2,
      fill: { color: BRAND.colors.accent }
    });

    // Finding heading
    slide.addText(f.heading, {
      x: 0.9, y, w: 11, h: 0.4,
      fontSize: 16, bold: true, color: BRAND.colors.text,
      fontFace: BRAND.font
    });

    // Finding body
    slide.addText(f.body, {
      x: 0.9, y: y + 0.4, w: 11, h: 0.7,
      fontSize: 12, color: BRAND.colors.textSecondary,
      fontFace: BRAND.font, wrap: true
    });
  });

  return slide;
}
```

### 7. Recommendations Slide

```javascript
function addRecommendationsSlide(title, recommendations) {
  // recommendations = [{ action, rationale, priority }]
  const slide = pptx.addSlide({ masterName: 'BRANDED_MASTER' });

  slide.addText(title, {
    x: 0.5, y: 0.7, w: 12, h: 0.6,
    fontSize: 24, bold: true, color: BRAND.colors.primary,
    fontFace: BRAND.font
  });

  recommendations.slice(0, 4).forEach((r, i) => {
    const y = 1.5 + i * 1.3;
    const priorityColor = r.priority === 'high' ? BRAND.colors.negative
                        : r.priority === 'medium' ? BRAND.colors.accent
                        : BRAND.colors.textSecondary;

    // Priority badge
    slide.addShape('rect', {
      x: 0.5, y: y + 0.05, w: 0.8, h: 0.3,
      fill: { color: priorityColor }, rectRadius: 0.05
    });
    slide.addText(r.priority?.toUpperCase() || 'TBD', {
      x: 0.5, y: y + 0.05, w: 0.8, h: 0.3,
      fontSize: 8, bold: true, color: 'FFFFFF',
      fontFace: BRAND.font, align: 'center'
    });

    // Action
    slide.addText(r.action, {
      x: 1.5, y, w: 10.5, h: 0.4,
      fontSize: 14, bold: true, color: BRAND.colors.text,
      fontFace: BRAND.font
    });

    // Rationale
    slide.addText(r.rationale, {
      x: 1.5, y: y + 0.45, w: 10.5, h: 0.6,
      fontSize: 11, color: BRAND.colors.textSecondary,
      fontFace: BRAND.font, wrap: true
    });
  });

  return slide;
}
```

### 8. Closing Slide

```javascript
function addClosingSlide(orgName) {
  const slide = pptx.addSlide({ masterName: 'BRANDED_MASTER' });

  slide.addShape('rect', { x: 0, y: 0, w: 13.33, h: 7.5, fill: { color: BRAND.colors.primary } });

  slide.addText('Thank You', {
    x: 1, y: 2, w: 11, h: 1.5,
    fontSize: 40, bold: true, color: 'FFFFFF',
    fontFace: BRAND.font, align: 'center'
  });

  slide.addText(`${orgName} Customer Intelligence`, {
    x: 1, y: 3.5, w: 11, h: 0.8,
    fontSize: 18, color: BRAND.colors.accent,
    fontFace: BRAND.font, align: 'center'
  });

  slide.addText('Powered by Enterpret | Generated via Claude Code', {
    x: 1, y: 5, w: 11, h: 0.5,
    fontSize: 12, color: 'AAAAAA',
    fontFace: BRAND.font, align: 'center'
  });

  return slide;
}
```

---

## Standard Deck Structure

For a typical Customer Digest:

1. **Title Slide** — Report name, date range, org name
2. **Key Metrics** — Total volume, sentiment split, top theme, biggest mover
3. **Top Themes** — Chart + table of top 8-10 themes by volume
4. **Sentiment Overview** — Donut chart + sentiment cards
5. **Key Findings (1)** — Top 3-4 findings from the analysis
6. **Key Findings (2)** — Additional findings or deep-dive highlights (if needed)
7. **Recommendations** — 3-4 prioritized action items
8. **Closing** — Thank you + branding

For an Investigation report, replace slides 3-4 with:
- Scope & Scale (trend chart)
- Theme Breakdown (stacked bar + table)

---

## Output

```javascript
pptx.writeFile({ fileName: `customer_digest_US_2026-03-05.pptx` });
// or
const buffer = await pptx.write({ outputType: 'nodebuffer' });
fs.writeFileSync('/path/to/output.pptx', buffer);
```

---

## Key Rules

1. **5-8 slides max** — This is an exec summary, not a full report
2. **Charts are optional** — If chart buffers are `null`, show tables only
3. **Tables max 8-12 rows** — Truncate with "..." row if needed
4. **Brand colors throughout** — Use `BRAND.colors.*` for all elements
5. **16:9 aspect ratio** — 13.33" × 7.5"
6. **Font consistency** — Use `BRAND.font` everywhere
