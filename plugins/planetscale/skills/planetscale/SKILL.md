---
name: planetscale
description: Index of PlanetScale operating skills — read-only inventory, Vitess and Postgres safety reviews, Insights and query tags, Traffic Control, webhooks, schema recommendations, approval gates, and the full best-practices assessment. Use to pick the right workflow skill before inspecting or changing a PlanetScale organization, database, branch, or schema.
---

# PlanetScale operating skills

These skills drive PlanetScale itself: they gather evidence through the PlanetScale MCP server, review it, and turn it into recommendations.

## Where to start

- Full best-practices assessment across every area, ending in one report: `safe-orchestrator`.
- Anything narrower: run `readonly-inventory` first so later steps work from real organization, database, and branch data instead of assumptions.
- Engine-specific schema, indexing, and query guidance: use the `database` skill index instead.

## Rules that apply to all of them

- Gather read-only evidence before recommending anything.
- Never create, modify, or delete a PlanetScale resource without explicit approval; `change-gates-and-approval-contract` defines the approval contract, and `autonomous-execution-mode` defines the only conditions under which approval can be granted up front.
- State what you verified separately from what you inferred.

## Skills

<!-- BEGIN GENERATED INDEX -->
| Skill | Path | Description |
| --- | --- | --- |
| `autonomous-execution-mode` | `skills/autonomous-execution-mode/SKILL.md` | Execute approved PlanetScale changes end-to-end without per-step approval when the operator has explicitly acknowledged the risk. |
| `best-practices-matrix` | `skills/best-practices-matrix/SKILL.md` | A concise feature matrix for deciding which PlanetScale safety, observability, and automation recommendations apply by engine. |
| `change-gates-and-approval-contract` | `skills/change-gates-and-approval-contract/SKILL.md` | Enforce explicit approval gates for any PlanetScale, database, repository, credential, network, or automation mutation. |
| `codebase-sqlcommenter-instrumentation` | `skills/codebase-sqlcommenter-instrumentation/SKILL.md` | Inspect an application repository connected to PlanetScale and recommend SQLCommenter-compatible query tagging packages and conventions. |
| `customer-report-template` | `skills/customer-report-template/SKILL.md` | Produce the final PlanetScale best-practices report after running the inventory and relevant review skills. |
| `mcp-agent-operating-model` | `skills/mcp-agent-operating-model/SKILL.md` | Configure safe agent behavior around PlanetScale MCP, Insights, schema recommendations, and repository work without autonomous production mutation. |
| `postgres-safety-review` | `skills/postgres-safety-review/SKILL.md` | Review PlanetScale Postgres for Traffic Control, query tags, roles, pg_strict, backups/PITR, private connectivity, webhooks, branches, and safe agent operation. |
| `pscale-cli-automation` | `skills/pscale-cli-automation/SKILL.md` | Use the PlanetScale CLI (pscale) from automated agents with --format json, auth check, pscale sql, and per-command --force. |
| `query-insights-and-tags` | `skills/query-insights-and-tags/SKILL.md` | Use PlanetScale Insights and SQLCommenter-style query tags to attribute database load, identify risky queries, and prepare safe Traffic Control or schema recommendations. |
| `readonly-inventory` | `skills/readonly-inventory/SKILL.md` | Collect read-only evidence about PlanetScale org, database, branches, webhooks, backups, roles, Insights, recommendations, and traffic configuration. |
| `safe-orchestrator` | `skills/safe-orchestrator/SKILL.md` | Master skill that runs the full PlanetScale safe best-practices assessment — inventory, engine review, Insights, Traffic Control, webhooks, schema recommendations, codebase instrumentation, and agent operating model — then produces a unified recommendations report. |
| `schema-recommendations-agent-loop` | `skills/schema-recommendations-agent-loop/SKILL.md` | Safely triage PlanetScale schema recommendations and turn them into reviewed branches, migrations, issues, or pull requests without applying production changes. |
| `traffic-control-recommendations` | `skills/traffic-control-recommendations/SKILL.md` | Build a safe recommendation plan for PlanetScale Postgres Database Traffic Control budgets and rules without applying them. |
| `vitess-safety-review` | `skills/vitess-safety-review/SKILL.md` | Review a PlanetScale Vitess database for safe migrations, deploy requests, schema recommendations, Insights, webhooks, and operational safety. |
| `webhook-automation-recommendations` | `skills/webhook-automation-recommendations/SKILL.md` | Recommend webhook subscriptions and safe automation patterns for PlanetScale alerts, anomalies, schema recommendations, deploy requests, and agent workflows. |
<!-- END GENERATED INDEX -->
