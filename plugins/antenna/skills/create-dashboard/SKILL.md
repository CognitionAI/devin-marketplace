---
name: create-dashboard
description: >
  Create a custom dashboard in Antenna from its metric catalog: enterprise-wide or per-team stat, line, column, and table widgets, plus per-contributor tables. Use when the user asks to build, save, or share an Antenna dashboard, or wants to track a set of metrics over time.
---

# Create an Antenna dashboard

## Steps

1. **Load the catalog.** Call `enterprise_dashboard_metrics`. Only metric keys listed there are accepted:
   - `metrics`: group and enterprise metrics
   - `contributor_metrics`: per-person metrics, used with `population: "contributors"`
   - Constraints: `allowed_widget_types`, `allowed_granularities`, the `months_back` range, `max_compared_groups` (6), and `contributor_constraints`

   Each metric has a `default_widget_type`; use it unless the user wants something else.
2. **Resolve groups (optional).** For team-specific widgets, get `external_id`s from `enterprise_identity_groups`.
3. **Design the widgets.** A good default layout:
   - 3–4 `stat` widgets for headline numbers, e.g. `active_developer_count`, `active_ai_developer_count`, `total_ai_cost_usd`
   - 2–3 `line` widgets for trends, e.g. `total_new_deliveries_per_developer`, `avg_time_to_merge_days`, `ci_failure_rate`
   - 1 `table` widget with `population: "contributors"` for people, e.g. `total_ai_cost_usd` with `extra_metrics: ["total_new_deliveries", "avg_ai_cost_per_new_delivery"]`

   Rules:
   - `stat` widgets take at most one group in `group_external_ids`. Comparing up to 6 groups only works on `line`, `column`, and `table` widgets.
   - Contributor widgets must be `table` or `column`, need exactly one group in `group_external_ids`, allow up to 3 `extra_metrics`, and take a `limit` of 5–50 (default 10).
4. **Confirm with the user.** Show the proposed name, window, granularity, widget list, and visibility before creating anything.
5. **Create it.** Call `enterprise_dashboard_create` with `name`, `months_back` (1–24), `date_granularity` (`week`, `month`, or `quarter`), `widgets`, and `visibility` (`private`, `shared`, or `everyone`). Add `share_with_emails` for `shared`. On this plugin's enterprise API-key connection, `owner_email` is **required**: ask the user which enterprise member should own the dashboard.
6. Return the dashboard link from the response.
