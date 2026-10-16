---
name: contributor-profile
description: >
  Build a profile of one engineer (or a handful) from Antenna: delivery, review, CI, and AI usage over time, compared against their team. Use when the user asks about a specific person ("how is Sam doing?", "show me Priya's AI usage"), wants 1:1 prep, or compares named individuals.
---

# Contributor profile

Always pass `start_date` and `end_date` for the window. If you omit them, the tools return about six months through the start of next month, including the current partial month. `day` granularity is valid only on `contributor_metrics_list` and `contributor_metrics_trends`, and only for a window of 92 days or less. `group_metrics_list` and `group_metrics_trends` accept `week`, `month`, and `quarter` only.

## Steps

1. **Resolve the person.** Call `enterprise_identity_search` with their name, username, or email. If several identities match, ask which one; don't guess. Keep the match's `id`.
2. **Period snapshot.** Call `contributor_metrics_list` for the window (default: last 3 complete months, `month`). To also get their team's rows for comparison, pass their team's `identity_group_external_id` (from `enterprise_identity_groups`). Then find the person's row by matching its `enterprise_identity_id` to that `id`.
3. **Trend.** Call `contributor_metrics_trends` with the `id` as `enterprise_identity_ids: [<id>]` (up to 50 IDs to compare people) over a longer window (default 6 months, `month`; use `week` for recent changes).
4. **Team baseline.** Call `group_metrics_list` for the person's group and compare per-developer averages.

## What to cover

- **Delivery:** `count_prs_authored`, `total_new_deliveries`, `avg_lines_changed_excluding_other`, `count_issues_completed`
- **Review:** `count_prs_reviewed`, `avg_time_awaiting_review_seconds`, `avg_review_cycles`, `count_prs_merged_without_review`
- **Quality and CI:** `ci_failure_rate`, `first_pass_rate`, `avg_rework_ratio`
- **AI:** `ai_engagement_level`, `ai_adoption_date`, `percent_ai_assisted_days`, `active_ai_tools`, `total_ai_cost_usd`, `avg_ai_cost_per_new_delivery`, `count_agent_prs_merged`

## Output

- 2–3 sentence summary of how the person is trending.
- A small table of this period vs. their previous period vs. the team average.
- Strengths and areas to discuss, framed as questions for a 1:1 rather than verdicts. Metrics describe activity, not a person's value.
