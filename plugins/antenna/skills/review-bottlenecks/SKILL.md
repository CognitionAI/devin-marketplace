---
name: review-bottlenecks
description: >
  Find code review and CI bottlenecks in Antenna: whose PRs wait longest for review, which teams have slow lead time or high CI failure rates, and whether PR size explains it. Use when the user asks "whose PRs take the longest to get reviewed?", "is there a correlation with PR size?", "why is our lead time slow?", or about review load, CI failures, or wasted CI time.
---

# Review and CI bottlenecks

## Steps

1. **Rank contributors by review wait.** Call `contributor_metrics_list` (default: last 3 complete months, `month`) with `order_by: "avg_time_awaiting_review_seconds"` and `limit: 25`. Only compare people with meaningful `count_prs_authored` (e.g. 3 or more); ignore the rest as noise.
2. **Pull the context columns** from the same rows:
   - Size: `avg_lines_changed_excluding_other`, `p75_lines_changed_excluding_other`
   - Friction: `avg_review_cycles`, `count_prs_with_changes_requested`, `count_prs_merged_without_review`
   - Flow: `avg_lead_time_seconds`, `avg_time_to_open_seconds`, `avg_time_to_ci_success_seconds`
   - CI: `ci_failure_rate`, `first_pass_rate`
   - Load: `count_prs_reviewed`, which shows who carries the review burden
3. **Correlation with size.** With the contributor rows, compute a rank correlation (Spearman) between `avg_lines_changed_excluding_other` and `avg_time_awaiting_review_seconds`. Report the coefficient and the sample size, and say plainly whether size explains the wait.
4. **Team view.** Call `group_metrics_list` with `order_by: "avg_time_awaiting_review_seconds"` (or `avg_lead_time_seconds`) to see whether the problem is concentrated in a few teams. Include `code_review_participation_rate`, `ci_failure_rate`, and `total_wasted_ci_compute_seconds`.
5. **Trend.** Use `group_metrics_trends` at `week` to check whether wait times are getting better or worse.

## Output

- Table of the slowest-reviewed authors with PR count, wait (in hours), review cycles, and average size.
- The size correlation and what it implies.
- Reviewers carrying a large share of reviews, and teams with low participation.
- 2–3 fixes tied to the data, e.g. split large PRs, rebalance reviewers, or fix flaky CI where `first_pass_rate` is low.
