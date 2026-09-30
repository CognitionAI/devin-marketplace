---
name: engineering-brief
description: >
  Write a weekly or monthly engineering brief from Antenna: what changed in delivery, flow, quality, and AI usage versus the prior period, and the biggest opportunities for improvement. Use when the user asks for a weekly or monthly summary, "what are the biggest opportunities for improvement on my team?", a leadership update, or a period-over-period review.
---

# Engineering brief

## Steps

1. **Pick the cadence.** For a weekly brief, use `week` over the last 5 complete weeks. For a monthly brief, use `month` over the last 6 complete months. Treat the current partial period as partial, or leave it out.
2. **Enterprise trend.** Call `group_metrics_trends` with no group IDs to get the enterprise aggregate. For a team brief, pass that team's `external_id` from `enterprise_identity_groups`.
3. **Team spread.** Call `group_metrics_list` for the latest complete period to see which groups drive the changes.
4. **Compute deltas.** For each metric below, compare the latest period with the average of the prior periods. Flag moves larger than about 10% and streaks of 3 or more periods in the same direction.
   - **Throughput:** `total_prs_merged`, `avg_new_deliveries_per_developer_per_period`, `count_issues_completed`
   - **Flow:** `avg_lead_time_seconds`, `avg_time_awaiting_review_seconds`, `avg_review_cycles`
   - **Quality:** `ci_failure_rate`, `ci_first_pass_rate`, `pct_rework`, `incident_change_failure_rate`
   - **Work mix:** `pct_features`, `pct_refactor`, `pct_churn`
   - **AI:** `active_ai_developer_count`, `total_ai_cost_usd`, `ai_cost_per_new_delivery`, `total_merged_prs_created_by_ai_agents`
5. **Explain the top movers.** For the 2–3 biggest changes, drill in with `contributor_metrics_list` scoped to the responsible group to see whether one person or the whole team moved.

## Output

- Headline sentence: the single most important change.
- 3–5 findings, each a short paragraph: what moved (with numbers), the likely cause, and one next step.
- What's going well.
- Top 3 opportunities, ordered by impact.
- Offer to turn the key metrics into an Antenna dashboard (see the `create-dashboard` skill).
