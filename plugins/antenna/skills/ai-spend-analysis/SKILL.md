---
name: ai-spend-analysis
description: >
  Break down AI spend across an Antenna enterprise: who and which teams spend the most, how much of it turns into shipped code, and where it is wasted. Use when the user asks "who is spending the most on AI?", "how efficiently are we using AI?", "how can we optimize AI spending?", or anything about AI cost, tokens, seats, or tool ROI.
---

# AI spend analysis

Answer questions about AI cost with Antenna's contributor and group metrics. Lead with the few people or teams that drive the answer, not a data dump.

## Steps

1. **Pick the window.** Default to the last 3 complete months at `date_granularity: "month"`. For "this month" or "last few weeks", use `week`. `day` is capped at a 92-day window.
2. **Enterprise and team totals.** Call `group_metrics_list` with `order_by: "total_ai_cost_usd"`. Each row's `subject` names the group (`type: "identity_group"`) or the enterprise aggregate (`type: "enterprise"`). Use the aggregate row for the headline totals.
3. **Top spenders.** Call `contributor_metrics_list` with `order_by: "total_ai_cost_usd"` and `limit: 20`. Rows include `display_name`, `username`, and `manager`. To scope to a team, first get its `external_id` from `enterprise_identity_groups`, then pass it as `identity_group_external_id`.
4. **Efficiency, not just volume.** For each top spender and team, compare:
   - `total_ai_cost_usd` split into `total_ai_seat_cost_usd` (licenses) and `total_ai_variable_cost_usd` (usage)
   - `pct_ai_usage_resulting_in_code` and `total_ai_cost_resulting_in_code_usd`: spend that led to committed code
   - `no_commit_spend_usd`: spend by people with no commits in the period
   - `non_developer_spend_usd`: spend by people who aren't active developers
   - `avg_ai_cost_per_new_delivery` (contributors) or `ai_cost_per_new_delivery` (groups): cost per unit of shipped work
   - `cache_hit_rate` and `context_bloat_factor` (input:output token ratio): high bloat with a low cache hit rate usually means oversized prompts or context
   - `active_ai_tools` and `ai_tool_stats` / `ai_tool_model_stats`: which tools and models drive the cost
5. **Trends (optional).** If the user asks whether spend is rising, call `group_metrics_trends` (enterprise aggregate when `identity_group_external_ids` is omitted) or `contributor_metrics_trends` for specific people. `contributor_metrics_trends` needs `enterprise_identity_ids` from `enterprise_identity_search` or a prior list call.

## Output

- One-sentence headline: total spend for the window and the main driver.
- Table of top spenders: name, total cost, seat vs. usage, % resulting in code, cost per new delivery.
- 2–4 concrete optimization moves tied to specific rows. Examples: unused seats (seat cost with little activity), no-commit or non-developer spend, heavy cost per delivery on one model or tool, or low cache hit rate.
- State the window and granularity you used.

## Notes

- Currency fields are USD. Fields ending `_rate` or `_ratio` are 0–1 ratios. `percent_ai_assisted_days` is already a percentage.
- High spend isn't bad by itself; compare it against delivery before calling it waste.
- Enterprise API-key connections see the whole enterprise, so treat individual cost data with care when sharing.
