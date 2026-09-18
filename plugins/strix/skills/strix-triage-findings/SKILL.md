---
name: strix-triage-findings
description: >
  Review and prioritize open Strix vulnerabilities. Use when the user asks
  "what did Strix find", "triage the open findings", "what should we fix
  first", "show critical vulnerabilities", or wants a list of open security
  issues grouped by severity or asset.
---

# Triage Strix findings

Load the open findings, group them, and propose the order of fixes.

## When

- The user wants an overview of open findings across the workspace or for one scan.
- The user wants to know which finding to fix first.

Do not use this skill to change code (strix-fix-finding) or to write a periodic report (strix-security-report).

## How

1. Call `list_vulnerabilities` with `status` `open`. Pass `scan_id` when the user names a scan and `severity` when the user names a minimum severity. Page through the results until every open finding is loaded.
2. Group the findings by severity, then by `target` or `endpoint`.
3. For each critical and high finding, call `get_vulnerability` and summarize the impact, the evidence, and the recommended fix in two or three sentences.
4. Point out findings that look like duplicates or false positives and explain why. Call `get_vulnerability_history` when the status history matters.
5. End with a prioritized list of the fixes to ship first. Cite finding ids so the user can open them in Strix.

## Status changes

- Change a status only when the user asks. Use `update_vulnerability` with `status` and a `note`. Valid statuses are `open`, `in_progress`, `snoozed`, `fixed`, `ignored`, and `not_affected`.
- Lower a severity only with a `severity_reason` the user agreed to.
- When the user wants tickets, call `push_vulnerability_to_ticket` for one finding or `bulk_push_vulnerabilities_to_ticket` for many. Both create or update Jira or Linear tickets, so confirm the target project first.

Do not start a retest or a new scan from this skill.
