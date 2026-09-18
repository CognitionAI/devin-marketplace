---
name: run-scan
description: >
  Start or rerun a Strix penetration test against a verified domain or a
  connected repository. Use when the user says "pentest this", "scan
  example.com with Strix", "run a security scan on the repo", "rerun the
  last scan", or asks for a scan schedule.
---

# Run a Strix scan

Propose a scan configuration, get confirmation, and start the scan.

## When

- The user wants a new penetration test, a code security review of a repository, or a repeat of an earlier scan.

Do not use this skill to review a pull request (pr-review-status) or to retest one finding (fix-finding).

## How

1. Call `list_domains` and `list_repositories` to find assets that match the target. If nothing matches, show the available assets and ask which to use.
2. If the target is not registered, offer to call `create_domain` (arguments `domain` and `asset_type`) or `create_repositories`. `create_repositories` takes a `body` argument that holds one repository object, or an array of them, each with `full_name` and optional `provider` and `installation_id`. A new domain must pass `verify_domain` before a scan can run against it.
3. If a similar scan exists, call `get_scan_template` on it and reuse its configuration. For an exact repeat, prefer `rerun_scan`.
4. Propose the configuration: targets, engagement type, scan tier, and scope notes. Tell the user that the scan spends credits and sends traffic to the targets. Call `get_credit_balance` when the balance matters.
5. Wait for the user to confirm. Do not call `create_scan` before the user confirms.
6. After confirmation, call `create_scan` once with an `Idempotency-Key`. Report the scan id and the link to follow progress.
7. To follow progress, call `get_scan`. Call `list_scan_agents` and `get_scan_agent_trace` when the user wants to see what the agents did. Call `send_scan_message` to give a running scan extra context, for example test credentials that already exist as a test user.

## Schedules

- For recurring scans, call `create_schedule`. Put the schedule definition in the `body` argument: every `create_scan` field plus `cron_expression` and `timezone`. Set `also_run_now` in `body` only when the user wants a scan immediately, and confirm first because that scan spends credits.
- Call `list_schedules`, `update_schedule`, and `trigger_schedule` to manage existing schedules.

## Rules

- One confirmation per scan. Never start a scan in a loop.
- Never scan a target that the user does not own or is not authorized to test.
- Use `cancel_scan` only when the user asks to stop a scan.
