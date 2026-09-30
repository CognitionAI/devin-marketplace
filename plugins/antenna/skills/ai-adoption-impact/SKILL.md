---
name: ai-adoption-impact
description: >
  Measure AI adoption across an Antenna enterprise and whether it's changing output: adoption and engagement trends, AI-assisted vs. non-AI developer throughput, before-vs-after-adoption delivery, and agent-authored PRs. Use when the user asks "is AI making us faster?", "how is AI adoption going?", "what's the impact of Copilot/Cursor/Claude/Devin?", or about AI agents' share of merged work.
---

# AI adoption and impact

## Steps

1. **Adoption trend.** Call `group_metrics_trends` with no group IDs (enterprise aggregate), `month`, over 6–12 months. Track `active_developer_count`, `active_ai_developer_count`, `max_active_ai_developer_count`, `avg_days_per_week_ai_developer_engaged`, and `total_ai_interactions`.
2. **AI vs. non-AI throughput.** From the same rows, compare `avg_new_deliveries_per_ai_developer_per_period` with `avg_new_deliveries_per_non_ai_developer_per_period`. The non-AI value is null when there are no non-AI developers; say so rather than inventing a comparison.
3. **Agent-authored work.** Compare `total_merged_prs_created_by_ai_agents` with `total_prs_merged` to get the agents' share. For who is driving it, call `contributor_metrics_list` with `order_by: "count_agent_prs_merged"`. That also gives the `count_remote_agent_prs_merged` vs. `count_local_agent_prs_merged` split.
4. **Before vs. after adoption (per person).** In `contributor_metrics_list`, use `ai_adoption_date`, `count_active_developer_days_post_ai_adoption`, `total_new_deliveries_post_ai_adoption`, and `total_deliveries_post_ai_adoption` alongside the full-period totals.
5. **By team.** Run `group_metrics_list` across groups to show where adoption lags.
6. **Tool mix.** In contributor rows, `active_ai_tools`, `engaged_ai_tools`, and `ai_tool_stats` show which tools people actually use.

## Output

- Adoption headline, e.g. "X of Y active developers used AI last month, up from Z".
- A throughput comparison with the caveat that AI users and non-users aren't a controlled experiment; self-selection and role mix matter.
- Agent share of merged PRs and its trend.
- Teams with low adoption, and one or two concrete next steps.
