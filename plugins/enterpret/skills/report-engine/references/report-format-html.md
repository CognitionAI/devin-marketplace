# HTML Report Format — Self-Contained Interactive Report (Chorus Design System)

This file provides the template and patterns for generating self-contained HTML reports aligned to the Enterpret Chorus design system. Reports are single-file, print-optimized, and work offline (except for CDN-loaded Chart.js and Geist font).

---

## HTML Template Scaffold

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{REPORT_TITLE}} — {{ORG_NAME}}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1/dist/fonts/geist-sans/style.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1/dist/fonts/geist-mono/style.css">
  <style>
    :root {
      /* Chorus brand tokens */
      --teal-600: {{BRAND.colors.primary}};
      --teal-700: {{BRAND.colors.primaryDark}};
      --teal-100: {{BRAND.colors.primaryLight}};
      --accent: {{BRAND.colors.accent}};

      /* Warm neutrals */
      --n100: {{BRAND.neutrals.n100}};
      --n200: {{BRAND.neutrals.n200}};
      --n300: {{BRAND.neutrals.n300}};
      --n400: {{BRAND.neutrals.n400}};
      --n500: {{BRAND.neutrals.n500}};
      --n600: {{BRAND.neutrals.n600}};
      --n700: {{BRAND.neutrals.n700}};
      --n800: {{BRAND.neutrals.n800}};
      --n900: {{BRAND.neutrals.n900}};

      /* Semantic */
      --color-primary: var(--teal-600);
      --color-text: var(--n900);
      --color-text-secondary: var(--n600);
      --color-text-tertiary: var(--n500);
      --color-border: var(--n300);
      --color-border-subtle: rgba(0,0,0,0.06);
      --color-bg-subtle: var(--n100);
      --color-positive: {{BRAND.colors.sentimentPositive}};
      --color-negative: {{BRAND.colors.sentimentNegative}};
      --color-neutral: {{BRAND.colors.sentimentNeutral}};

      /* Typography */
      --font-sans: 'Geist', {{BRAND.typography.fallbackFontFamily}}, system-ui, sans-serif;
      --font-mono: 'Geist Mono', 'SF Mono', monospace;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: var(--font-sans);
      font-weight: 300;
      color: var(--color-text);
      line-height: 1.6;
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem;
      background: #FFFFFF;
      font-size: 15px;
    }

    /* Header — Chorus style */
    .report-header {
      padding-bottom: 1.5rem;
      margin-bottom: 2rem;
      border-bottom: 1px solid var(--color-border);
    }
    .report-header h1 {
      font-size: clamp(28px, 4vw, 36px);
      font-weight: 900;
      color: var(--color-primary);
      letter-spacing: -0.025em;
      line-height: 1.1;
      margin-bottom: 0.5rem;
    }
    .report-header .subtitle {
      color: var(--color-text-secondary);
      font-size: 14px;
      font-weight: 300;
      line-height: 1.5;
    }
    .report-header .org-badge {
      display: inline-block;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 400;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--color-primary);
      background: var(--teal-100);
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      margin-bottom: 0.75rem;
    }

    /* Executive Summary — teal accent left border */
    .exec-summary {
      border-left: 3px solid var(--color-primary);
      padding: 1rem 1.5rem;
      margin: 1.5rem 0;
      background: var(--teal-100);
      border-radius: 0 8px 8px 0;
    }
    .exec-summary h2 {
      border: none;
      margin: 0 0 0.5rem;
      padding: 0;
      font-size: 15px;
      font-weight: 700;
      color: var(--color-primary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .exec-summary ul { list-style: none; padding: 0; }
    .exec-summary li {
      padding: 0.4rem 0;
      border-bottom: 1px solid rgba(0,0,0,0.04);
      font-weight: 400;
    }
    .exec-summary li:last-child { border-bottom: none; }

    /* Section headings */
    h2 {
      color: var(--color-primary);
      font-size: 20px;
      font-weight: 700;
      margin: 2.5rem 0 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--color-border);
    }
    h3 {
      color: var(--n800);
      font-size: 15px;
      font-weight: 700;
      margin: 1.5rem 0 0.5rem;
    }

    /* Labels — Chorus mono uppercase pattern */
    .label {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 400;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--color-text-secondary);
    }

    /* Tables — warm neutrals, no heavy headers */
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0;
      font-size: 14px;
    }
    thead th {
      background: var(--color-primary);
      color: #FFFFFF;
      padding: 0.6rem 0.8rem;
      text-align: left;
      font-weight: 500;
      font-size: 13px;
    }
    thead th:first-child { border-radius: 4px 0 0 0; }
    thead th:last-child { border-radius: 0 4px 0 0; }
    tbody td {
      padding: 0.5rem 0.8rem;
      border-bottom: 1px solid var(--n200);
    }
    tbody tr:nth-child(even) {
      background: var(--n100);
    }
    tbody tr:hover {
      background: var(--teal-100);
    }

    /* Charts */
    .chart-container {
      position: relative;
      margin: 1.5rem 0;
      padding: 1rem;
      background: var(--n100);
      border-radius: 8px;
      border: 1px solid var(--color-border-subtle);
    }
    .chart-container canvas {
      max-width: 100%;
    }
    .chart-caption {
      text-align: center;
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--color-text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-top: 0.75rem;
    }

    /* Sentiment badges — Chorus accent colors */
    .sentiment-badge {
      display: inline-block;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      font-family: var(--font-mono);
    }
    .sentiment-positive { background: var(--color-positive); color: #1C1A18; }
    .sentiment-negative { background: var(--color-negative); color: #1C1A18; }
    .sentiment-neutral { background: var(--color-neutral); color: #FFFFFF; }

    /* Verbatim quotes — warm border */
    .verbatim {
      border-left: 3px solid var(--n400);
      padding: 0.75rem 1rem;
      margin: 0.8rem 0;
      font-style: italic;
      font-weight: 300;
      color: var(--n800);
      background: var(--n100);
      border-radius: 0 8px 8px 0;
    }
    .verbatim-meta {
      font-style: normal;
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--color-text-tertiary);
      margin-top: 0.5rem;
    }
    .verbatim-meta a {
      color: var(--color-primary);
      text-decoration: none;
    }
    .verbatim-meta a:hover {
      text-decoration: underline;
    }

    /* Recommendations — card style with Chorus radius */
    .recommendation {
      display: flex;
      gap: 1rem;
      margin: 0.8rem 0;
      padding: 1rem;
      background: var(--n100);
      border-radius: 8px;
      border: 1px solid var(--color-border-subtle);
    }
    .recommendation .priority {
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      white-space: nowrap;
      height: fit-content;
    }
    .priority-high { background: var(--color-negative); color: #1C1A18; }
    .priority-medium { background: var(--color-primary); color: #FFFFFF; }
    .priority-low { background: var(--color-neutral); color: #FFFFFF; }

    /* Data scope / limitations */
    .data-scope {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--color-text-tertiary);
      padding: 0.75rem 1rem;
      background: var(--n100);
      border-radius: 8px;
      margin: 1.5rem 0;
    }

    /* Footer — minimal, Chorus style */
    .report-footer {
      margin-top: 3rem;
      padding-top: 1rem;
      border-top: 1px solid var(--n300);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--color-text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .report-footer a {
      color: var(--color-primary);
      text-decoration: none;
    }

    /* Print styles */
    @media print {
      body { max-width: 100%; padding: 1rem; }
      .chart-container { page-break-inside: avoid; }
      table { page-break-inside: avoid; }
      h2 { page-break-after: avoid; }
      .recommendation { page-break-inside: avoid; }
      a[href]:after { content: none; }
    }
  </style>
</head>
<body>

  <div class="report-header">
    <span class="org-badge">{{ORG_NAME}}</span>
    <h1>{{REPORT_TITLE}}</h1>
    <p class="subtitle">{{DATE_RANGE}} · {{REGION}} · {{SCOPE}}</p>
  </div>

  <div class="exec-summary">
    <h2>Executive Summary</h2>
    <ul>
      <!-- {{EXEC_SUMMARY_ITEMS}} -->
      <li>Key finding 1</li>
      <li>Key finding 2</li>
    </ul>
  </div>

  <!-- {{REPORT_SECTIONS}} -->
  <!-- Sections are generated dynamically based on report type -->

  <div class="report-footer">
    <span>Powered by <a href="https://enterpret.com">Enterpret</a> · via Claude Code</span>
    <span>Generated {{GENERATION_DATE}}</span>
  </div>

  <script>
    // Chart.js initialization
    const style = getComputedStyle(document.documentElement);
    const COLORS = {
      primary: style.getPropertyValue('--teal-600').trim(),
      accent: style.getPropertyValue('--accent').trim(),
      positive: style.getPropertyValue('--color-positive').trim(),
      negative: style.getPropertyValue('--color-negative').trim(),
      neutral: style.getPropertyValue('--color-neutral').trim(),
      // Chorus categorical palette for charts
      categorical: [
        '#0F6773', '#2A9EAD', '#86BDE1', '#A085B8', '#EB994D',
        '#67BB98', '#F99294', '#BCC064', '#FFD586', '#BAE1D0'
      ]
    };

    // {{CHART_SCRIPTS}}
  </script>

</body>
</html>
```

---

## Component Patterns

### Data Table

```html
<table>
  <thead>
    <tr>
      <th>Rank</th>
      <th>Theme</th>
      <th>Volume</th>
      <th>WoW</th>
      <th>Sentiment</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Theme Name</td>
      <td>12,345</td>
      <td>↑ 15%</td>
      <td><span class="sentiment-badge sentiment-negative">72% Negative</span></td>
    </tr>
  </tbody>
</table>
```

### Interactive Chart

```html
<div class="chart-container">
  <canvas id="chart-themes" width="720" height="400"></canvas>
  <p class="chart-caption">Top 10 Themes by Volume</p>
</div>

<script>
new Chart(document.getElementById('chart-themes'), {
  type: 'bar',
  data: {
    labels: ['Theme 1', 'Theme 2', ...],
    datasets: [{
      data: [1234, 5678, ...],
      backgroundColor: COLORS.primary,
      borderRadius: 4
    }]
  },
  options: {
    indexAxis: 'y',
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: 'rgba(0,0,0,0.06)' } },
      y: { grid: { display: false }, ticks: { font: { family: "'Geist', sans-serif", size: 12 } } }
    }
  }
});
</script>
```

### Verbatim Quote

```html
<div class="verbatim">
  "Customer feedback quote text here..."
  <div class="verbatim-meta">
    — 2026-03-01 &nbsp;
    <a href="{{CITATION_BASE_URL}}{{RECORD_ID}}">View in Enterpret</a>
  </div>
</div>
```

### Recommendation Card

```html
<div class="recommendation">
  <span class="priority priority-high">HIGH</span>
  <div>
    <strong>Action item headline</strong>
    <p>Detailed rationale and expected impact.</p>
  </div>
</div>
```

### Sentiment Donut Chart

```html
<div class="chart-container">
  <canvas id="chart-sentiment" width="400" height="400"></canvas>
  <p class="chart-caption">Sentiment Distribution</p>
</div>

<script>
new Chart(document.getElementById('chart-sentiment'), {
  type: 'doughnut',
  data: {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [{
      data: [45, 35, 20],
      backgroundColor: [COLORS.positive, COLORS.negative, COLORS.neutral],
      borderWidth: 2,
      borderColor: '#FFFFFF'
    }]
  },
  options: {
    cutout: '55%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: { font: { family: "'Geist', sans-serif", size: 12 }, padding: 16, usePointStyle: true }
      }
    }
  }
});
</script>
```

---

## Fallback: Base64 PNG Charts

If Chart.js CDN is unavailable or the report must work fully offline, embed charts as base64 PNG images instead:

```html
<div class="chart-container">
  <img src="data:image/png;base64,{{CHART_BASE64}}" alt="Top Themes by Volume" style="max-width:100%;">
  <p class="chart-caption">Top 10 Themes by Volume</p>
</div>
```

Generate the PNG using the same `generateChart()` function from `chart-patterns.md`, then base64-encode the buffer.

---

## Key Rules

1. **Self-contained** — Single HTML file, no external dependencies except Chart.js CDN and Geist font CDN
2. **Chorus design system** — Warm neutrals, teal primary, Geist typeface, 4px/8px border radius
3. **Responsive** — Works on desktop and mobile; `max-width: 900px` centered layout
4. **Print-optimized** — `@media print` rules prevent chart/table splitting across pages
5. **CSS variables** — All brand colors via `:root` variables from `brand/enterpret.json`
6. **Citation links** — All verbatim quotes link to `{citationBaseUrl}{record_id}`
7. **Fallback** — If Chart.js CDN fails, charts degrade to static base64 PNGs
8. **File naming** — `{report_type}_{region}_{date}.html`
9. **Mono labels** — Use Geist Mono + uppercase + letter-spacing for labels, captions, data scope
10. **Color proportion** — 60% neutrals, 30% teal, 10% accents (per Chorus guidelines)
