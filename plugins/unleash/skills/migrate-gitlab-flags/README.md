# Migrate GitLab Feature Flags to Unleash (v8+) — `/unleash:migrate-gitlab-flags`

A skill in the [Unleash plugin for Claude Code](https://github.com/Unleash/unleash-claude-skills) that migrates a codebase from **GitLab Feature Flags** (GitLab's Unleash-compatible legacy client API) to a modern **Unleash v8** server. The skill inventories flags and strategies, maps GitLab constructs to Unleash equivalents, provisions the definitions, rewrites the SDK wiring with a minimal diff, and proves behavior parity against a before-state oracle.

## Install

With the plugin (recommended — the Unleash MCP server comes bundled):

```text
/plugin marketplace add Unleash/unleash-claude-skills
/plugin install unleash@unleash-marketplace
```

Or standalone — copy this directory into a skills location; the directory name becomes the command:

- Project: `<repo>/.claude/skills/migrate-gitlab-flags/`
- Personal (all projects): `~/.claude/skills/migrate-gitlab-flags/`

The skill is self-contained; no other files are required. A standalone copy can't bundle the MCP server — see the [main README](https://github.com/Unleash/unleash-claude-skills#install) for registering it manually (key `unleash`) and for environment variables.

## Invocation

Manual only (`disable-model-invocation: true`) — it rewrites code and provisions server state, so it never auto-triggers:

```text
/unleash:migrate-gitlab-flags <path-to-app-or-repo>   # plugin install
/migrate-gitlab-flags <path-to-app-or-repo>           # standalone skill
```

## Requirements

- `curl` and `jq` on PATH (used by `scripts/preflight.sh` and the recipes).
- An Unleash v8+ target and credentials matching the provisioning mechanism you choose when the skill asks (see `references/provisioning.md`):
  - **MCP server** — a PAT with flag-creation permission. On plugin installs the bundled server is already connected; the skill detects and proposes it.
  - **Import files** — no credentials for the assistant; a human/CI applies the generated files (the import endpoint requires a PAT/service account);
  - **Direct Admin API** — a PAT or service-account token (admin tokens are deprecated).
- Optionally, GitLab management-API credentials (PAT + project id) so the inventory phase can read the live flag definitions.

### Two environment-variable groups

They coexist and serve different consumers — no conflict:

| Group | Variables | Consumed by |
|---|---|---|
| MCP server (plugin-wide) | `UNLEASH_BASE_URL`, `UNLEASH_PAT`, `UNLEASH_DEFAULT_PROJECT` | The bundled Unleash MCP server (see the [main README](https://github.com/Unleash/unleash-claude-skills#environment-variables-shared-by-all-skills)) |
| Migration & app runtime | `UNLEASH_URL`, `UNLEASH_API_TOKEN`, `UNLEASH_CLIENT_TOKEN`, `UNLEASH_FRONTEND_TOKEN`, `GITLAB_API_*` | `scripts/preflight.sh`, the Admin-API recipes, and the migrated app itself |

## Relationship to the `featureops` skill

During a migration, parity rules govern: flag names carry over unchanged, state carries over exactly, and strategy parameters (e.g. `groupId`) are preserved verbatim — the `featureops` skill's naming conventions, evaluate-first gate, and rollout milestones apply to *new* flags, not migrated ones. Once the migration completes, `featureops` governs the migrated flags' ongoing lifecycle (rollouts, audits, cleanup).

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | The phased workflow (discover → inventory → map → provision → rewrite → verify) and its non-negotiable invariants. |
| `references/gitlab-flags-primer.md` | The GitLab before-state model: instance-id auth, wire strategies, per-SDK traps. |
| `references/concept-mapping.md` | GitLab construct → Unleash equivalent translation tables. |
| `references/provisioning.md` | The three provisioning mechanisms, recipes, and idempotency rules. |
| `references/sdk-cheatsheet.md` | Before → after SDK configuration per stack. |
| `references/verification.md` | The behavior-parity verification method and gate checklist. |
| `scripts/preflight.sh` | Pre-run sanity checks (`--mode api\|import\|mcp`, `--frontend`). |
| `evals/` | Fixture-agnostic evaluation scenarios (bring your own fixture; cases are prompt-skippable — see `evals/README.md`). |
