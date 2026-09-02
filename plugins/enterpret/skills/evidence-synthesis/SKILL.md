---
name: evidence-synthesis
description: >
  How to synthesize customer evidence from KG data into actionable narrative.
  Auto-invoked when producing evidence sections, selecting quotes, sizing
  problems, assessing impact, or writing insight summaries. Core rule:
  synthesize, never dump. Value is narrative, not retrieval.
version: 5.0.0
---

# Customer Evidence Synthesis

This skill governs how you turn raw KG query results into evidence that PMs, executives, and engineers can act on. The output should feel like analysis from a skilled researcher, not a database export.

## Core Principle

**Synthesize, never dump.** The value you provide is narrative and interpretation, not raw retrieval. Anyone can pull numbers — what PMs need is someone to tell them what the numbers mean, why they matter now, and what to do about it.

## Quote Selection Rules

### CRITICAL: Use actual customer words, not AI summaries

Quotes MUST come from `nli.content` (the customer's verbatim words), NOT `fi.content` (the AI-generated summary). If a query returns `fi.content`, it is a summary — do not present it as a customer quote. Always query `nli.content AS verbatim` for customer-facing quotes.

### CRITICAL: Every quote must have a date

Every quote MUST include its `nli.record_timestamp` as a date. A quote without a date has no temporal context — the reader can't tell if it's from yesterday or 2 weeks ago. Never omit the date.

### How many: 3-5 maximum per section

More than 5 quotes becomes a data dump. Fewer than 3 feels cherry-picked. The sweet spot is 3-5 carefully chosen quotes that together tell a complete story. For top themes in reports, aim for 3+ quotes minimum.

### Diversity requirements:
- **Different subthemes** — don't pick 3 quotes about the same narrow issue
- **Different time periods** — show the problem exists across time, not just one spike
- **Different sentiment angles** — if possible, include one that shows the severity (frustrated) and one that shows the impact (workaround, churn mention)
- **Recency bias toward recent** — lead with the most recent quote, but include at least one older quote to show persistence

### Selection criteria (prefer quotes that):
1. **Illustrate with specific detail** — "The CSV import fails every time I have more than 500 rows" > "Import doesn't work"
2. **Show business impact** — "We had to manually re-enter 200 records" > "This is annoying"
3. **Represent the majority pattern** — don't lead with an outlier
4. **Include context** — quotes with timestamps, account info, or channel context are more credible

### What to avoid:
- Generic one-word complaints ("Bad", "Broken")
- Quotes that require extensive explanation
- Multiple quotes making the same point
- Quotes with PII or sensitive information — redact if present

### Citation format:
Every quote MUST include date AND a clickable "View in Enterpret" link. Use this exact format consistently:
```
> "{Quote text}"
> — {YYYY-MM-DD} · [View in Enterpret]({citationBaseUrl}{record_id})
```
Never use "View record" or just "View" — always "View in Enterpret".

## Problem Sizing (Required)

Every evidence section MUST include these six dimensions:

1. **Volume** — how many feedback items mention this? Absolute number + proportion of total feedback if available.

2. **Breadth** — how many distinct accounts/users? One account filing 50 tickets is different from 50 accounts filing one each. If account data isn't available, say so.

3. **Trend (WoW per theme)** — direction + percentage for EACH theme, not just overall. "↑ 45% week-over-week" not just "increasing." Include the comparison periods. Every theme table should have a WoW trend column.

4. **Recency** — when was the most recent mention? "Most recent: 2026-03-06" tells the reader whether this is active right now or tapering off. Include this for each top theme.

5. **Duration** — is this new (appeared this week) or chronic (6+ months)? New + rising = escalate. Old + stable = systemic.

6. **Channel mix + severity implication** — where is this feedback coming from? Tickets only vs. tickets + reviews + social carries different severity.

## Limitations Section (Required)

**Every output MUST include a "What this evidence does NOT tell us" section.** This is non-negotiable. Omitting limitations destroys trust with sophisticated PMs who know data has gaps.

Standard limitations to consider:

| Limitation | When to include |
|-----------|-----------------|
| Sample size | Always if < 50 items. "N=23 — treat as directional." |
| Channel bias | Always. "This reflects [channels]. Users who don't contact support are invisible." |
| Segment gaps | When account data is unavailable or incomplete |
| Correlation ≠ causation | When suggesting impact or root cause |
| Survivorship bias | When relevant — "This only captures users who stayed long enough to complain." |
| Taxonomy coverage | When search returned few matches — the problem may exist under different labels |
| Recency bias | When most evidence is from the last few days of the window |

Be specific. "Data has limitations" is useless. "All 23 data points come from support tickets filed in the last 14 days — no app review or survey signal" is useful.

## Output Calibration by Context

Different commands need different evidence density:

| Context | Evidence Depth | Quote Count | Limitations Depth |
|---------|---------------|-------------|-------------------|
| Quick lookup (`/find`) | Concise summary — volume, sentiment, top quotes | 2-3 | One-line scope |
| Deep analysis (`/analyze`) | Full block — this IS the deliverable | 3-5 | Full section |
| Root cause (`/analyze --rootcause`) | Minimal — action-oriented | 1-2 most severe | Blast radius caveat |
| Report — weekly/account (`/report`) | Their pain vs. market pattern or headlines | 2-3 | Completeness caveat |

## Narrative Structure

When writing evidence narrative (not tables), follow this arc:

1. **Lead with the finding** — what you discovered. Not how you discovered it.
2. **Size it** — volume, trend, breadth.
3. **Interpret it** — what does this mean for the product?
4. **Support it** — quotes that prove the interpretation.
5. **Bound it** — what we don't know.

Bad: "I queried the KG for themes matching 'checkout' and found 340 results with 78% negative sentiment across 3 subthemes..."

Good: "Checkout friction is the fastest-rising customer pain point this month — 340 reports, up 45% WoW, with 78% negative sentiment. It's concentrated in mobile web where users report the payment form resets on back-navigation..."

## JTBD Signal Extraction

When customer feedback contains signals about underlying jobs, extract them in this format:

**"When** [situation], **I want to** [action], **so I can** [outcome]"

### How to identify JTBD signals:
- **Workflow descriptions** — customers explaining what they're trying to accomplish
- **Workaround mentions** — reveals the job they're trying to get done despite the tool
- **Comparison language** — "In [other tool], I could..." reveals the job being hired for
- **Goal statements** — "I need to be able to..." or "We're trying to..."
- **Success criteria** — "It would be great if I could just..."

### JTBD extraction rules:
1. Extract no more than 2-3 JTBDs per evidence section — focus on the strongest signals
2. Ground each in a specific quote — don't fabricate JTBDs from thin evidence
3. Label inferred JTBDs as `HYPOTHESIS` — "Inferred JTBD (HYPOTHESIS): When [X]..."
4. Note how many customers expressed similar intent — a single customer's JTBD is an anecdote, 10 is a pattern

## Insight Types

The KG categorizes feedback insights by type. Use this to interpret the nature of the signal:

| Type | What It Means | How to Use |
|------|--------------|------------|
| COMPLAINT | Active frustration with current state | Strongest signal for prioritization |
| IMPROVEMENT | Suggestion for enhancement | Feature request signal |
| QUESTION | Confusion or lack of understanding | Documentation/UX clarity signal |
| PRAISE | Positive reinforcement | Protect/amplify what's working |

A theme that's 90% complaints is different from one that's 60% questions — the first needs a fix, the second needs better education.
