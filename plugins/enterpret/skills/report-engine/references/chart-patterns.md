# Chart Patterns — QuickChart API for Reports

Reusable chart generation patterns using [QuickChart.io](https://quickchart.io) to produce PNG images for embedding in docx and pptx reports. For HTML reports, use Chart.js directly (see `report-format-html.md`). Zero npm dependencies — uses `fetch()` only.

---

## Core Functions

### `generateChart(config, width, height)` — Fetch PNG from QuickChart

```javascript
async function generateChart(config, width = 720, height = 400) {
  try {
    const response = await fetch('https://quickchart.io/chart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chart: config,
        width,
        height,
        devicePixelRatio: 2,
        backgroundColor: 'white',
        format: 'png'
      })
    });
    if (!response.ok) return null;
    const arrayBuffer = await response.arrayBuffer();
    return Buffer.from(arrayBuffer);
  } catch (e) {
    console.error('Chart generation failed:', e.message);
    return null;
  }
}
```

### `embedChart(buffer, width, height, caption)` — Wrap PNG into docx Paragraphs

```javascript
function embedChart(buffer, width = 480, height = 267, caption = '') {
  if (!buffer) return []; // Silent skip — chart failure never blocks report

  const elements = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, after: 80 },
      children: [
        new ImageRun({
          data: buffer,
          transformation: { width, height },
          type: 'png'
        })
      ]
    })
  ];

  if (caption) {
    elements.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [
          new TextRun({
            text: caption,
            italics: true,
            font: BRAND.font,
            size: 18,
            color: BRAND.colors.textSecondary
          })
        ]
      })
    );
  }

  return elements;
}
```

---

## Brand Palette

Colors are loaded dynamically from the resolved `BRAND` object (custom.json → enterpret.json fallback):

```javascript
const chartColors = {
  sentimentColors: {
    Positive: BRAND.chart.sentimentColors.Positive,
    Negative: BRAND.chart.sentimentColors.Negative,
    Neutral: BRAND.chart.sentimentColors.Neutral
  },
  categorical: BRAND.chart.categorical,
  wow: BRAND.chart.wow
};
```

**Chorus design system palette (from `brand/enterpret.json`):**
- Categorical (cross-group accents for max distinction): `["#0F6773", "#2A9EAD", "#86BDE1", "#A085B8", "#EB994D", "#67BB98", "#F99294", "#BCC064", "#FFD586", "#BAE1D0"]`
- Sentiment: Positive `#67BB98` (Jade), Negative `#F99294` (Coral), Neutral `#9495A2` (Slate)
- WoW: Current `#0F6773` (Teal 600), Previous `#C8C4BF` (Warm N400)

---

## Chart Config Recipes

Each function returns a Chart.js config object. Pass the result to `generateChart()`.

### 1. `horizontalBarConfig(labels, values)` — Top Themes by Volume

Use for: ranked theme lists, L1/L2 category breakdowns.

```javascript
function horizontalBarConfig(labels, values) {
  return {
    type: 'horizontalBar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: chartColors.categorical[0],
        borderRadius: 4,
        barThickness: 28
      }]
    },
    options: {
      scales: {
        xAxes: [{ gridLines: { color: 'rgba(0,0,0,0.06)' }, ticks: { callback: (v) => v.toLocaleString() } }],
        yAxes: [{ gridLines: { display: false }, ticks: { fontSize: 11 } }]
      },
      plugins: {
        legend: false,
        datalabels: {
          anchor: 'end',
          align: 'right',
          font: { weight: 'bold', size: 11 },
          formatter: (v) => v.toLocaleString()
        }
      }
    }
  };
}
```

Render: 720×320 → Embed: 480×213

### 2. `donutConfig(labels, values, colors)` — Sentiment Split

Use for: overall sentiment distribution, category-level sentiment.

```javascript
function donutConfig(labels, values, colors) {
  colors = colors || [chartColors.sentimentColors.Positive, chartColors.sentimentColors.Negative, chartColors.sentimentColors.Neutral];
  const total = values.reduce((a, b) => a + b, 0);
  return {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#FFFFFF'
      }]
    },
    options: {
      cutoutPercentage: 55,
      plugins: {
        legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true, fontSize: 12 } },
        datalabels: {
          formatter: (v) => ((v / total) * 100).toFixed(1) + '%',
          color: '#FFFFFF',
          font: { weight: 'bold', size: 12 }
        },
        doughnutlabel: {
          labels: [
            { text: total.toLocaleString(), font: { size: 28, weight: 'bold' }, color: '#000000' },
            { text: 'Total', font: { size: 12 }, color: '#666666' }
          ]
        }
      }
    }
  };
}
```

Render: 720×400 → Embed: 480×267

### 3. `groupedBarConfig(labels, currentValues, previousValues)` — WoW Comparison

Use for: week-over-week side-by-side, period comparisons.

```javascript
function groupedBarConfig(labels, currentValues, previousValues) {
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'This Week', data: currentValues, backgroundColor: chartColors.wow.current, borderRadius: 4 },
        { label: 'Last Week', data: previousValues, backgroundColor: chartColors.wow.previous, borderRadius: 4 }
      ]
    },
    options: {
      scales: {
        yAxes: [{ gridLines: { color: 'rgba(0,0,0,0.06)' }, ticks: { callback: (v) => v.toLocaleString() } }],
        xAxes: [{ gridLines: { display: false } }]
      },
      plugins: {
        legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16 } },
        datalabels: false
      }
    }
  };
}
```

Render: 720×400 → Embed: 480×267

### 4. `lineConfig(labels, datasets)` — Volume Trend Over Time

Use for: trend visualization, sentiment trajectory over time.

```javascript
function lineConfig(labels, datasets) {
  // datasets = [{ label, data, color }]
  return {
    type: 'line',
    data: {
      labels,
      datasets: datasets.map(ds => ({
        label: ds.label,
        data: ds.data,
        borderColor: ds.color,
        backgroundColor: ds.color + '1A', // 10% opacity fill
        fill: true,
        lineTension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: ds.color
      }))
    },
    options: {
      scales: {
        yAxes: [{ gridLines: { color: 'rgba(0,0,0,0.06)' } }],
        xAxes: [{ gridLines: { display: false } }]
      },
      plugins: {
        legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16 } },
        datalabels: false
      }
    }
  };
}
```

Render: 720×400 → Embed: 480×267

### 5. `stackedBarConfig(labels, datasets)` — Subthemes × Sentiment Breakdown

Use for: sentiment heatmap across themes, multi-category breakdowns.

```javascript
function stackedBarConfig(labels, datasets) {
  // datasets = [{ label, data, color }]
  return {
    type: 'horizontalBar',
    data: {
      labels,
      datasets: datasets.map(ds => ({
        label: ds.label,
        data: ds.data,
        backgroundColor: ds.color,
        borderRadius: 2
      }))
    },
    options: {
      scales: {
        xAxes: [{ stacked: true, gridLines: { color: 'rgba(0,0,0,0.06)' } }],
        yAxes: [{ stacked: true, gridLines: { display: false } }]
      },
      plugins: {
        legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16 } },
        datalabels: false
      }
    }
  };
}
```

Render: 720×320 → Embed: 480×213

### 6. `dualAxisConfig(labels, volumes, percentages)` — Volume Bars + Negative % Line

Use for: category overview with volume and negative sentiment rate side-by-side.

```javascript
function dualAxisConfig(labels, volumes, percentages) {
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Volume',
          data: volumes,
          backgroundColor: chartColors.categorical[0],
          borderRadius: 4,
          yAxisID: 'y-volume'
        },
        {
          label: 'Negative %',
          data: percentages,
          type: 'line',
          borderColor: chartColors.sentimentColors.Negative,
          backgroundColor: 'transparent',
          pointBackgroundColor: chartColors.sentimentColors.Negative,
          pointRadius: 5,
          lineTension: 0.3,
          yAxisID: 'y-pct'
        }
      ]
    },
    options: {
      scales: {
        yAxes: [
          {
            id: 'y-volume',
            position: 'left',
            gridLines: { color: 'rgba(0,0,0,0.06)' },
            ticks: { callback: (v) => v.toLocaleString() }
          },
          {
            id: 'y-pct',
            position: 'right',
            gridLines: { display: false },
            ticks: { callback: (v) => v + '%', max: 100 }
          }
        ],
        xAxes: [{ gridLines: { display: false } }]
      },
      plugins: {
        legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16 } },
        datalabels: false
      }
    }
  };
}
```

Render: 720×400 → Embed: 480×267

---

## Sizing Guide

| Chart Type | Render Size | Embed Size | Notes |
|---|---|---|---|
| Horizontal bar | 720×320 | 480×213 | Shorter height for bar charts |
| Donut | 720×400 | 480×267 | Standard |
| Grouped bar | 720×400 | 480×267 | Standard |
| Line | 720×400 | 480×267 | Standard |
| Stacked bar | 720×320 | 480×213 | Shorter height for bar charts |
| Dual axis | 720×400 | 480×267 | Standard |

The `devicePixelRatio: 2` in `generateChart()` produces 2× resolution PNGs for retina-quality output.

---

## Fallback Rules

1. **Charts never block report generation.** If `generateChart()` returns `null`, `embedChart()` returns `[]` — the report renders with tables only.
2. **Charts supplement tables** — always place the chart ABOVE its corresponding data table. The table remains the authoritative data source.
3. **If QuickChart is unreachable** (network error, rate limit), silently skip all charts. Do not retry.
4. **Log but don't alert** — `console.error` on failure for debugging, but never surface chart errors to the user.

---

## Usage Pattern (end-to-end)

```javascript
// 1. Prepare data
const themeLabels = ['Support', 'Billing', 'Onboarding', ...];
const themeVolumes = [22400, 19000, 13900, ...];

// 2. Generate chart config (using dynamic brand colors)
const config = horizontalBarConfig(themeLabels.slice(0, 10), themeVolumes.slice(0, 10));

// 3. Fetch PNG from QuickChart
const chartBuffer = await generateChart(config, 720, 320);

// 4. Embed in docx section (returns Paragraph[] or [])
const chartElements = embedChart(chartBuffer, 480, 213, 'Top 10 Themes by Volume');

// 5. Add to document section children
const sectionChildren = [
  sectionHeading('Top Themes'),
  ...chartElements,      // Chart above table (or empty if failed)
  createTable(headers, rows, widths)  // Table always present
];
```
