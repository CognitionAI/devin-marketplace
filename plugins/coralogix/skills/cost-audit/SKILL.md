---
name: cost-audit
description: Audit Coralogix data ingestion costs — analyse usage, TCO policies, and find optimisation opportunities
argument-hint: "[time range, e.g. 'last 7 days']"
triggers:
  - user
  - model
---

Analyse the team's Coralogix data usage and cost optimisation posture. Default to the last 7 days unless the user specifies a different range.

## 1. Understand capabilities

- Use `get_data_usage_capabilities` to discover available labels, measurement kinds, and units for data usage queries.

## 2. Ingestion volume analysis

- Use `query_data_usage` to pull daily ingestion volumes broken down by:
  - **Pillar** (logs, metrics, traces) to see which data type dominates.
  - **Application** and **subsystem** to identify the top contributors.
- Highlight the top 5 applications/subsystems by volume.
- Flag any sudden spikes or anomalies in the daily trend.

## 3. TCO policy review

- Use `manage_tco_log_policies` with a list action to review current log TCO policies.
- Use `manage_tco_trace_policies` to review trace TCO policies.
- Use `manage_tco_rum_policies` to review RUM TCO policies if applicable.
- For each policy, note what priority tier data is assigned to (high, medium, low) and which applications/subsystems are covered.

## 4. Quota allocation

- Use `manage_quota_allocation_rule_set` to review how ingestion quota is distributed across teams or applications.

## 5. Identify optimisations

Look for these common cost reduction opportunities:
- **Verbose logging**: Applications sending disproportionately high log volume relative to their error rate.
- **Unattended data**: Applications or subsystems with no alerts, dashboards, or saved views referencing them (use `search_alert_definitions` and `search_dashboard` to check).
- **TCO gaps**: High-volume data that isn't covered by a TCO policy (defaulting to high priority when medium or low would suffice).
- **Parsing overhead**: Use `manage_parsing_rules` to check if parsing rules are running on data that could be deprioritised.

## 6. Report

Present a cost audit summary:

- **Total ingestion**: Volume by pillar with trend.
- **Top consumers**: Top 5 applications/subsystems by volume.
- **TCO coverage**: Percentage of data covered by TCO policies, and what tier.
- **Optimisation recommendations**: Ranked list of actions with estimated impact (e.g. "Move application X logs to medium priority — saves ~30% of its ingestion cost").
- **Quick wins**: Changes that can be made immediately vs longer-term architectural changes.
