---
name: team-comparison
description: >
  Compare engineering teams (Antenna identity groups) on delivery, AI adoption and cost, code review, and CI health. Use when the user asks how teams stack up, which team is fastest or slowest, how a team changed over time, or wants a ranking across groups or managers.
---

# Team comparison

## Steps

1. **Find the groups.** Call `enterprise_identity_groups` and page with `limit` and `offset` until `has_more` is false. Match the user's team names to `display_name`, then keep the `external_id`s. Manager-synced groups carry `parent_external_id`, `depth`, and `has_children`, so you can roll a manager's org up or down.
2. **Snapshot ranking.** Call `group_metrics_list` for the window (default: last 3 complete months, `month`). Pass `identity_group_external_ids` to compare specific teams. Omit it to rank every group plus the enterprise aggregate, which is the baseline. Set `order_by` to the metric the user cares about.
3. **Over time.** Call `group_metrics_trends` with the same group IDs for a per-period series. Use `week` for the last 1–3 months and `month` or `quarter` for longer windows.

## Metrics to compare

Normalize per developer; raw totals favor bigger teams.

- **Size:** `active_developer_count`, `active_ai_developer_count`
- **Throughput:** `avg_new_deliveries_per_developer_per_period`, `avg_prs_merged_per_developer_per_period`, `avg_issues_completed_per_developer_per_period`
- **Work mix:** `pct_features`, `pct_rework`, `pct_refactor`, `avg_innovation_rate`
- **Review and flow:** `avg_time_awaiting_review_seconds`, `avg_review_cycles`, `avg_lead_time_seconds`, `code_review_participation_rate`
- **CI:** `ci_failure_rate`, `ci_first_pass_rate`, `total_wasted_ci_compute_seconds`
- **AI:** `avg_ai_cost_usd_per_ai_developer`, `ai_cost_per_new_delivery`, `pct_ai_usage_resulting_in_code`, `avg_days_per_week_ai_developer_engaged`
- **Delivery reliability:** `deployment_success_rate`, `incident_change_failure_rate`, `avg_incident_time_to_restore_seconds`

## Output

- Table with one row per team plus the enterprise baseline, limited to the 5–8 metrics that answer the question.
- Call out where each team is meaningfully above or below the baseline, and note small teams (few active developers), where numbers are noisy.
- Convert `_seconds` fields to hours or days.
