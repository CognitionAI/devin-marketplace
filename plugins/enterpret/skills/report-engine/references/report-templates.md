# Report Structure Templates

These templates define the section structure for each report type. The report engine uses these during Phase 3 (Draft) and Phase 4 (Final output). All placeholders use `{ORG_NAME}` and `{ORG_SLUG}` from `context/organization.json`.

---

## Customer Digest

**Purpose:** Weekly overview of what customers are saying. The "Monday morning briefing."

### Structure

```
TITLE: Customer Digest — {Region} | {Date Range}
SUBTITLE: Generated from {N} customer interactions

EXECUTIVE SUMMARY
- 3-5 bullet points: What changed this week? What's the #1 issue?
- Include: top theme, biggest mover (WoW), overall sentiment shift

SECTION 1: TOP THEMES
CHART: horizontalBarConfig — top 10 themes by volume, placed above table
- Table: Rank | Theme | Volume | WoW Change | Most Recent | Sentiment
- Top 10-15 themes by volume
- Every theme MUST show WoW trend (↑/↓/flat X%) and most recent date
- Highlight themes with >20% WoW increase in bold

SECTION 2: SENTIMENT OVERVIEW
CHART: donutConfig — sentiment split (Positive / Negative / Neutral), placed above breakdown
- Overall sentiment split (Positive / Negative / Neutral with %)
- Themes with highest negative sentiment concentration

SECTION 3: WEEK-OVER-WEEK CHANGES
CHART: groupedBarConfig — WoW side-by-side for top movers, placed above table
- Table: Theme | This Week | Last Week | Change | % Change
- Sort by absolute change (biggest movers first)
- Flag new themes that weren't in last week's top 20

SECTION 4: SUBTHEME BREAKDOWN (top 3 themes)
- For each of the top 3 themes, show subtheme decomposition
- Table: Subtheme | Volume | % of Theme Total | Most Recent
- Helps readers understand WHAT specifically within each theme

SECTION 5: NOTABLE FEEDBACK
- 3-5 representative verbatim quotes per top theme (minimum 3 for top 5 themes)
- Each quote MUST include: verbatim text, YYYY-MM-DD date, [View in Enterpret](link)
- Never use "View record" or "View" — always "View in Enterpret"
- Grouped by theme, ordered most recent first within each group

SECTION 6: LIMITATIONS
- REQUIRED — never omit this section
- Sample size caveat if N < 50
- Channel bias: which sources are represented, which are missing
- Account breadth: how many unique accounts/users (or note if unavailable)
- Taxonomy coverage: note if the topic may exist under different labels

SECTION 7: RECOMMENDATIONS
- 2-4 actionable items based on findings
- Frame as product decisions: "Consider...", "Investigate...", "Prioritize..."
- Each recommendation references specific data from above
```

---

## Issue Investigation

**Purpose:** Deep-dive into a specific topic, issue category, or anomaly. The "what happened and why" report.

### Structure

```
TITLE: Investigation — {Topic} | {Date Range}
SUBTITLE: Deep-dive analysis of {topic description}

EXECUTIVE SUMMARY
- What is the issue?
- How big is it? (volume, % of total, trend direction)
- What's the root cause hypothesis?
- What should be done?

SECTION 1: SCOPE & SCALE
CHART: lineConfig — volume trend over time for investigated topic, placed above summary
- Total volume for the investigated topic
- Trend over time (current period vs previous)
- Proportion of total feedback (what % does this represent?)

SECTION 2: THEME & SUBTHEME BREAKDOWN
CHART: stackedBarConfig — subthemes × sentiment breakdown, placed above table
- Table: Subtheme | Volume | Sentiment | % of Total
- Drill-down into L2 → L3 → Theme level
- Identify which specific subthemes drive the most volume

SECTION 3: CASCADE IMPACT
- Co-occurring themes (what other issues appear alongside this one?)
- Table: Co-occurring Theme | Shared Volume
- This reveals systemic connections

SECTION 4: ROOT CAUSE ANALYSIS
- Themed grouping of user complaints
- For each root cause:
  - Description of the pattern
  - Volume affected
  - 3+ verbatim examples with YYYY-MM-DD dates and [View in Enterpret](link)
  - Hypothesis for why this is happening

SECTION 5: CUSTOMER EVIDENCE
- 5-10 representative verbatim quotes (nli.content, NOT fi.content)
- Each MUST include: verbatim text, YYYY-MM-DD date, [View in Enterpret](link)
- Never use "View record" or "View" — always "View in Enterpret"
- Selected to illustrate the range of the problem across time and subthemes

SECTION 6: LIMITATIONS
- REQUIRED — never omit this section
- Sample size, channel bias, account breadth gaps, taxonomy coverage

SECTION 7: RECOMMENDATIONS
- Prioritized list of actions
- Each with: what to do, expected impact, urgency level
- Map recommendations to the root causes identified above
```

---

## Explore Taxonomy (Utility Output)

**Purpose:** Not a report — a quick reference output shown in chat (not a generated file).

### Structure

```
TAXONOMY: {Category Name}

L1: {Category}
├── L2: {Sub-category 1} (Volume: X)
│   ├── L3: {Issue 1} (Volume: Y, Sentiment: Z% negative)
│   │   ├── Theme: {Theme name 1}
│   │   └── Theme: {Theme name 2}
│   └── L3: {Issue 2} (Volume: Y)
│       └── Theme: {Theme name 3}
└── L2: {Sub-category 2} (Volume: X)
    └── ...
```

Present as a tree in markdown. No file generation for taxonomy exploration.

---

## Build-Report Archetypes

These archetypes are used by the `/build-report` command. Each defines a pre-built structure, scoping questions, and query strategy.

### Archetype 1: Theme Deep-Dive

**Purpose:** Comprehensive analysis of a specific L1 or L2 category — taxonomy breakdown, sentiment, trends, and evidence.

**Scoping Questions:**
1. Which category or topic to deep-dive into?
2. Date range? (Default: last 14 days)
3. Region filter? (Default: all)
4. Audience? (Default: product team)

**Structure (7 sections):**

```
TITLE: Theme Deep-Dive — {Category} | {Date Range}

1. EXECUTIVE SUMMARY
   - Category volume, trend, key subthemes

2. TAXONOMY BREAKDOWN
   CHART: horizontalBarConfig — L2 subcategories by volume
   - Table: L2 | Volume | WoW Trend | Most Recent | Top Themes | Sentiment

3. SENTIMENT ANALYSIS
   CHART: stackedBarConfig — sentiment per L2 subcategory
   - Overall sentiment split for the category
   - Comparison to org-wide average

4. TREND ANALYSIS
   CHART: lineConfig — category volume over past 4 weeks
   - WoW changes per theme, trajectory

5. TOP THEMES DETAIL
   - For each top 5 theme: volume, sentiment, WoW trend, most recent date
   - 3+ verbatim quotes per theme with YYYY-MM-DD dates and [View in Enterpret](link)
   - Subtheme decomposition for top 3 themes

6. CASCADE IMPACT
   - Co-occurring themes from other categories

7. LIMITATIONS
   - REQUIRED — sample size, channel bias, account breadth, taxonomy coverage

8. RECOMMENDATIONS
   - Prioritized actions specific to this category
```

### Archetype 2: Sentiment Trend

**Purpose:** Period-over-period sentiment comparison — what's getting better, what's getting worse, and why.

**Scoping Questions:**
1. Comparison periods? (Default: this week vs last week)
2. Region filter? (Default: all)
3. Focus on negative sentiment or full spectrum? (Default: full)
4. Audience? (Default: leadership)

**Structure (5 sections):**

```
TITLE: Sentiment Trend — {Period 1} vs {Period 2}

1. EXECUTIVE SUMMARY
   - Overall sentiment shift, biggest movers

2. SENTIMENT COMPARISON
   CHART: groupedBarConfig — sentiment per category, period 1 vs period 2
   - Table: Category | P1 Positive% | P2 Positive% | Change

3. THEMES DRIVING CHANGE
   CHART: horizontalBarConfig — themes with biggest sentiment shift
   - Themes that improved (top 5)
   - Themes that deteriorated (top 5)
   - New themes in period 2

4. EVIDENCE
   - 3+ verbatim quotes per top improving/deteriorating theme
   - Each with YYYY-MM-DD date and [View in Enterpret](link)

5. LIMITATIONS
   - REQUIRED — sample size, channel bias, period comparison caveats

6. RECOMMENDATIONS
   - What to continue (improving themes)
   - What to address (deteriorating themes)
```

### Archetype 3: Executive Summary

**Purpose:** High-level overview for leadership — concise, metric-heavy, action-oriented. Intentionally brief.

**Scoping Questions:**
1. Date range? (Default: last 7 days)
2. Region? (Default: all)
3. Any specific focus areas? (Default: none — full overview)

**Structure (4 sections):**

```
TITLE: Executive Summary — {ORG_NAME} | {Date Range}

1. KEY METRICS DASHBOARD
   - Total feedback volume (with WoW change)
   - Sentiment split (with WoW change)
   - Top 3 themes by volume
   - Biggest mover theme

2. TOP THEMES
   CHART: horizontalBarConfig — top 5 themes only
   - Table: Theme | Volume | WoW Trend | Most Recent | Action Needed
   - Every theme shows WoW direction and recency

3. HIGHLIGHTS & RISKS
   - 3-4 bullet points: What's improving? What's at risk?
   - Each backed by specific data
   - Include 1-2 representative quotes with dates for impact

4. DATA SCOPE & LIMITATIONS
   - Brief: N items, sources, date range, key gaps

5. RECOMMENDED ACTIONS
   - 2-3 high-priority items only
   - Framed for leadership decision-making
```

### Archetype 4: Custom

**Purpose:** User describes what they want, Claude proposes a structure, user confirms.

**Flow:**
1. Ask: "Describe what you want to analyze or present."
2. Claude proposes a report structure (title, sections, charts)
3. User confirms or adjusts
4. Claude executes with the confirmed structure

No predefined template — structure is generated dynamically based on user description and available data.
