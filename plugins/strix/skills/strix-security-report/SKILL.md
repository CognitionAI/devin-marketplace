---
name: strix-security-report
description: >
  Compile a security posture report from Strix data. Use when the user asks
  for a weekly or monthly security report, a summary of scan activity, new
  and fixed findings, remediation trends, or supply-chain risk for
  leadership, engineering, or a customer.
---

# Strix security report

Write a periodic security report from scans, findings, PR reviews, and supply-chain data.

## When

- The user wants a report for a period, for example the last 7 or 30 days.

Do not use this skill to summarize one scan (call `get_scan` directly) or to triage findings (strix-triage-findings).

## How

1. Ask for the audience when it is not clear: engineering, leadership, or customer. Default to engineering.
2. Call `get_analytics_overview` with `range` set to the period, for example `7d` or `30d`, to get the KPIs, the severity breakdown, and the remediation trends.
3. Call `list_scans` and `list_pr_reviews` with `date_from` set to the start of the period.
4. Call `list_vulnerabilities` with `status` `open` twice: once with `severity` `critical` and once with `severity` `high`. Page through both result sets.
5. Call `get_supply_chain_org_summary` for the dependency risk position.
6. Write the report with these sections: Highlights, New findings, Fixed findings, Open critical and high findings, Scan and review activity, Recommendations for next period.

## Style

- Use plain language for leadership and customer audiences. Keep technical detail for engineering.
- Cite finding ids so readers can open them in Strix.
- Do not change any data while you compile the report.
