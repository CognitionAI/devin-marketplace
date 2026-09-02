---
name: cello-get-program-performance
description: Analyze Cello's referral program health, trends, industry benchmarks, prioritized recommendations, and top-performing referrers into one performance readout. Use this whenever someone asks how their referral program is doing, wants a performance summary, asks "how are we trending," "how do we compare to industry," "what should we improve," "who are our top referrers," or wants a recurring digest (weekly/monthly) of program health. Also trigger for questions like "why did signups drop" or "are we above/below benchmark" — this pulls metrics, recommendations, and top referrers together rather than answering from any single tool alone. Do not use this for integration/technical debugging (use cello-integration-health-check) or for a deep fraud/anomaly investigation into a specific referrer (this skill flags an obviously odd top-referrer ratio in passing, but a dedicated referrer-analysis skill should do the actual investigation).
compatibility: Requires the Cello MCP server (cello_get_program_metrics, cello_get_recommendations, and cello_get_top_referrers tools).
---

# Get Program Performance

Turns raw metrics and recommendation data into a readout that actually says something — not just a table of numbers. The core value-add is connecting the two: a metrics dip is more useful paired with the specific recommendation that addresses it, and a recommendation is more convincing paired with the number it would move.

## Workflow

1. **Call `cello_get_program_metrics`.** This returns lifetime totals, weekly/monthly history, and industry benchmarks in one call.

2. **Call `cello_get_top_referrers`.** This returns the top 10 referrers ranked by revenue, with signups, recurring purchases, ARR, days active, and days sharing per referrer.

3. **Call `cello_get_recommendations`.** This returns a prioritized (impact-weighted) list of improvement actions and their completion status.

4. **Connect them — this is the actual analysis, not just reporting each tool's output separately:**
   - Identify the most significant trend(s) in the metrics: compare last-30d vs. prior-30d across referrers enabled, active referrers, sharing activity, signups, and recurring purchases. Note when a headline number (e.g. ARR) is moving opposite to the underlying activity metrics — lagging revenue recognition can mask a cooling funnel, and that gap is often the most important thing to surface, not the ARR figure alone.
   - Check each metric against its industry benchmark where available. Being above benchmark doesn't mean "nothing to improve" — say so if the trend is declining even while still above benchmark, since trajectory matters as much as the snapshot.
   - Cross-reference declining metrics against the recommendation list: does an unfinished recommendation directly address the metric that's slipping? If so, lead with that pairing — it's the most actionable insight in the whole readout ("sharing is down 10% and 3 of 3 Sharing-category recommendations are still open").
   - Note top completed vs. incomplete recommendations by impact weight, so the highest-leverage open item is never buried.
   - From the top referrers list, note whether a small number of referrers account for a disproportionate share of revenue/signups (concentration risk for the program, independent of any individual fraud question) — this matters for performance framing even without flagging fraud specifically.
   - While reviewing top referrers, do a light plausibility check on the ratio of `daysActive` to `daysSharing` versus signup volume — a referrer with very few sharing days but outsized signups is worth one flagged line (not a full writeup) since it's the kind of thing worth a closer look. Keep this brief: name the referrer and the specific ratio, then suggest a dedicated referrer/fraud-analysis pass if one is available, rather than investigating further here — that's a different skill's job.

## Output format

Keep it to a short readout, not a dashboard dump — lead with what changed and what to do about it, not a wall of metrics:

```
## Program Performance: [headline — e.g. "cooling activity despite rising ARR"]

**Trend:** [most important month-over-month shift, with the benchmark comparison if relevant]
**Why it matters:** [connect to lagging indicators if headline metric is masking it]

### Top opportunity
[highest-impact-weight open recommendation, tied explicitly to the metric it would move]

### Other notable shifts
- [metric]: [change] (benchmark: [industry figure], you: [your figure])
- ...

### Recommendations status
[x/y done] — remaining gaps by category

### Top performing referrers
[top 2-3 by revenue, with signups/ARR]
[one-line concentration note if a small handful dominate]
[flag only if a ratio genuinely looks off — otherwise omit this line entirely]
```

Don't just list every metric returned by the tool — pick the ones that moved meaningfully or sit near/below benchmark. A flat, healthy number doesn't need a line.

## Edge cases

- **ARR/revenue rising while activity metrics fall:** always call this out explicitly rather than leading with the revenue figure — it's the single most common way a program looks healthier than it is, since revenue recognition lags the referrer activity that drives it.
- **All recommendations in one category are open (e.g. all of Sharing):** treat this as a pattern, not three separate line items — say the category is the gap, then name the top one or two by impact weight.
- **No benchmark data available for a given metric:** just report your own trend without forcing a comparison; don't imply a benchmark exists if the tool didn't return one.
- **Recurring/digest use** (e.g. "give me my weekly program update"): keep the same structure, but explicitly note what changed since the last readout if that context is available in conversation; otherwise treat it as a fresh snapshot rather than guessing at a prior baseline.
