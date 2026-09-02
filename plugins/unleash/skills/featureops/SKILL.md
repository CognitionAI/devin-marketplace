---
name: featureops
description: Manage feature flags with Unleash — evaluate whether a code change needs a flag, create flags with consistent naming, wrap code behind flags, plan progressive rollouts, and clean up stale flags. Use when working with feature flags, feature toggles, rollouts, releases, experiments, kill-switches, canary deploys, or the Unleash MCP server. Ships as a customizable FeatureOps template — set your team's policy in an override file (`.unleash/featureops.md`); no need to edit the skill.
license: Apache-2.0
allowed-tools: mcp__unleash__evaluate_change mcp__unleash__detect_flag mcp__unleash__get_flag_state mcp__unleash__list_projects mcp__unleash__list_flags mcp__plugin_unleash_mcp__evaluate_change mcp__plugin_unleash_mcp__detect_flag mcp__plugin_unleash_mcp__get_flag_state mcp__plugin_unleash_mcp__list_projects mcp__plugin_unleash_mcp__list_flags
---

# Unleash · FeatureOps Template

This skill brings [FeatureOps](https://featureops.io) — the discipline of controlling software behavior at runtime — into your coding agent. It drives the [Unleash MCP server](https://github.com/Unleash/unleash-mcp) to evaluate changes for risk, create flags with consistent naming, generate SDK guard code, manage rollouts, and clean up stale flags.

The defaults work out of the box, but feature-management conventions vary across teams and industries. This skill ships as a **customizable template**: every tunable value lives in one policy file, which you override per project *without editing the skill* — see [Active policy](#active-policy) and [Customize for your team](#customize-for-your-team).

## Setup check

This skill needs the Unleash MCP server connected. When installed as a Claude Code plugin, the server is registered automatically from the bundled `.mcp.json`; you only need to set three environment variables in the shell that launches your agent. With a standalone install on any other agent, connect the Unleash MCP server yourself first (see `examples/README.md` in the repository, https://github.com/Unleash/unleash-claude-skills, including the remote MCP server option):

```bash
export UNLEASH_BASE_URL=https://your-instance.getunleash.io/api
export UNLEASH_PAT=your-personal-access-token
export UNLEASH_DEFAULT_PROJECT=default   # optional; defaults to "default"
```

If the Unleash tools are not available, tell the user to complete setup (see the README at https://github.com/Unleash/unleash-claude-skills for full install, transport, and credential instructions) and stop rather than guessing flag state.

> **Tool naming note (Claude Code):** on Claude Code the read-only tools are pre-approved via `allowed-tools` under two names each: `mcp__unleash__*` (standalone-skill install, where you register the server under the key `unleash`) and `mcp__plugin_unleash_mcp__*` (plugin install, where Claude Code namespaces the bundled server — keyed `mcp` in `.mcp.json` — as `mcp__plugin_<plugin>_<server>__<tool>` → `mcp__plugin_unleash_mcp__<tool>`, verified on a real install). Pre-approval only applies while this skill is active; a read-only tool invoked before the skill has loaded will still prompt once. Write operations (`create_flag`, `set_flag_rollout`, `toggle_flag_environment`, `remove_flag_strategy`) are **never** pre-approved — always let the user confirm them. `wrap_change` and `cleanup_flag` don't mutate server state (they return guard code and removal instructions), but they are deliberately not pre-approved either: each immediately precedes edits to production code paths, so the confirmation prompt stays. On other agents, `allowed-tools` doesn't apply — they use their own permission model — but the read-only vs. write distinction above still holds: never let a write tool run without user confirmation.

## Active policy

Every tunable value — naming convention, flag types and lifetimes, rollout milestones and holds, halt thresholds, staleness windows, and the high-risk domains — comes from the **active policy**. The reference files describe *how* to apply these values and never restate the numbers, so always resolve them from here.

**Precedence, highest first: project override → user override → shipped defaults.** For each value, use the highest layer that sets it; anything unset falls through to the defaults. The project override and the defaults are inlined below at load time. If a user override exists (`~/.unleash/featureops.md`), read it with your file tools and slot it *between* them.

**Project override** — `${CLAUDE_PROJECT_DIR}/.unleash/featureops.md` (repo-specific; wins):
!`cat "${CLAUDE_PROJECT_DIR}/.unleash/featureops.md" 2>/dev/null || echo "(no project override — using user override and/or the defaults below)"`

**Shipped defaults** — `references/policy-defaults.md`:
!`cat "${CLAUDE_SKILL_DIR}/references/policy-defaults.md" 2>/dev/null || echo "(defaults file not found; load references/policy-defaults.md manually)"`

> **If the two blocks above are empty or show a literal `` !`…` `` command**, your agent doesn't run inline injection (this is a Claude Code feature). Read the files yourself with your file tools and apply the same precedence: the project override `.unleash/featureops.md`, the user override `~/.unleash/featureops.md`, and this skill's `references/policy-defaults.md`.

## When to load the reference files

Load the reference file that matches the task. For tasks that span workflows (e.g. "create a flag and plan its rollout"), load both.

| User intent | Load |
|---|---|
| Setting up feature flags, deciding when to flag a change, naming a new flag | `references/feature-flag-conventions.md` |
| Working in a high-risk directory (payments, auth, data migrations, external integrations) | `references/high-risk-domains.md` |
| Planning a gradual rollout, configuring percentages, setting halt conditions | `references/rollout-guidance.md` |
| Removing a flag, cleaning up after a rollout, auditing stale flags | `references/cleanup-cadence.md` |

## Core workflow

For a change that might need a flag, follow this sequence. The reference files hold the detailed rules for each step.

1. **Evaluate risk** — call `evaluate_change` with a description of the change before implementing anything in the active policy's flag-required categories (see [Active policy](#active-policy)). See `references/feature-flag-conventions.md` and `references/high-risk-domains.md`.
2. **Prefer reuse** — call `detect_flag` before creating anything. Reuse a matching flag rather than adding to flag sprawl.
3. **Create** — if no match exists, call `create_flag` with a name following the active policy's naming convention and the right flag type. See `references/feature-flag-conventions.md`.
4. **Wrap** — call `wrap_change` for SDK-appropriate guard code. Apply it verbatim; keep the fallback branch realistic.
5. **Roll out** — use `set_flag_rollout` and `toggle_flag_environment` to progress through milestones. See `references/rollout-guidance.md`.
6. **Clean up** — flags are temporary by design. When a rollout stabilizes or an experiment concludes, remove the flag. See `references/cleanup-cadence.md`.

Do not auto-execute write operations. Present the plan, get confirmation, then act — especially for flag creation, rollout changes, and cleanup, which touch production code paths.

## Migrations are a different workflow

When the task is migrating existing flags from another system (e.g. GitLab feature flags) into Unleash, defer to the `migrate-gitlab-flags` skill (`/unleash:migrate-gitlab-flags`) and do **not** apply this skill's conventions to the migrated flags — migration parity rules win: flag names carry over unchanged (never renamed to `{domain}-{feature}-{variant}`), state carries over exactly (no `evaluate_change` gate, no default rollout milestones), and strategy parameters such as `groupId` are preserved verbatim. This skill's conventions govern new flags, and they resume governing migrated flags once the migration completes.

## Tool reference

The Unleash MCP server exposes the following tools.

| Tool | Description | When to use |
|---|---|---|
| `evaluate_change` | Analyzes a code change and determines whether it should be behind a feature flag. | Before implementing risky changes |
| `detect_flag` | Searches for existing flags that match a description to prevent duplicates. | Before creating new flags |
| `create_flag` | Creates a new feature flag with proper naming, typing, and metadata. | When no suitable flag exists |
| `wrap_change` | Generates framework-specific code to guard a feature behind a flag. | After creating a flag |
| `list_projects` | Lists Unleash projects available to the configured token, with optional pagination. | Discovering available projects |
| `list_flags` | Lists feature flags in a project (active by default; set `archived=true` for archived flags). | Auditing flag inventory; discovering existing flags before creating new ones |
| `get_flag_state` | Returns the current state, strategies, and metadata for a flag. | Debugging, status checks |
| `set_flag_rollout` | Configures rollout percentages and activation strategies. | Gradual releases |
| `toggle_flag_environment` | Enables or disables a flag in a specific environment. | Testing, staged rollouts |
| `remove_flag_strategy` | Deletes a rollout strategy from a flag. | Simplifying flag configuration |
| `cleanup_flag` | Returns file locations and instructions for removing a flag after rollout. | After full rollout |

The read-only tools — `evaluate_change`, `detect_flag`, `get_flag_state`, `list_projects`, `list_flags` — are pre-approved via `allowed-tools`. Every other tool prompts for approval — the write operations because they mutate server state, and `wrap_change`/`cleanup_flag` because their output immediately precedes code edits. Keep it that way unless the user has a specific reason to lower the bar. Use `list_projects` and `list_flags` for inventory discovery before creating new flags; `list_flags` (active + archived) is also the basis of the flag audit workflow in `references/cleanup-cadence.md`.

## Customize for your team

Don't edit this skill's files to customize it — in a plugin install they live in a managed cache that a plugin update overwrites. Instead, put your team's policy in an **override file**; the skill reads it automatically (see [Active policy](#active-policy)). `references/policy-defaults.md` lists every tunable value and doubles as the template.

- **Project (recommended):** create `./.unleash/featureops.md` in the repo and set only the values you want to change — especially your real high-risk domains. It's committed with the repo and wins over everything.
- **User (optional):** `~/.unleash/featureops.md` for personal cross-repo defaults.

Copy the sections you want to change out of `references/policy-defaults.md`, or just ask the agent: *"set up a FeatureOps policy override for this project."* For company-wide standardization, the heavier alternative is to fork this repo, bake your policy into `policy-defaults.md`, and publish it as your own internal plugin — see the skill README.

---

## Metadata

- **License:** Apache-2.0
- **Privacy Policy:** https://www.getunleash.io/privacy-policy
- **Support:** support@getunleash.io · GitHub Issues at https://github.com/Unleash/unleash-claude-skills/issues
- **Source:** https://github.com/Unleash/unleash-claude-skills

### MCP server attribution

This skill configures the **Unleash MCP server**:

- Package: [`@unleash/mcp`](https://www.npmjs.com/package/@unleash/mcp) on npm
- Source: https://github.com/Unleash/unleash-mcp
- License: Apache-2.0
- Maintainer: Unleash (Bricks Software AS)
- Transport: local stdio via `npx`, or remote Streamable HTTP at `https://<your-instance>/api/admin/mcp`
