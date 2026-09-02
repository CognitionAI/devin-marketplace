# FeatureOps — `/unleash:featureops`

A skill in the [Unleash plugin for Claude Code](https://github.com/Unleash/unleash-claude-skills). It brings [FeatureOps](https://featureops.io) — the discipline of controlling software behavior at runtime — into your coding agent: evaluate changes for risk, create flags with consistent naming, wrap code behind flags, plan progressive rollouts, and clean up stale flags.

This skill ships as a **customizable template**: the defaults work out of the box, and you tailor them to your team by writing a policy override file — no editing the skill. See [Customize for your team](#customize-for-your-team).

Install it with the plugin (`/plugin install unleash@unleash-marketplace`) or standalone (`cp -r skills/featureops ~/.claude/skills/`). See the [main README](https://github.com/Unleash/unleash-claude-skills#install) for MCP setup and environment variables.

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | Skill entry point: setup check, active-policy loader, core workflow, tool reference. |
| `references/policy-defaults.md` | **The policy** — every tunable value (naming, flag types & lifetimes, rollout milestones/holds/thresholds, staleness windows) plus the high-risk domains. Single source of truth, and the template you copy to override. |
| `references/feature-flag-conventions.md` | *How* to evaluate, reuse, wrap, and name flags. |
| `references/rollout-guidance.md` | *How* to run a progressive rollout and halt safely. |
| `references/cleanup-cadence.md` | *How* to decide a flag is stale and remove it; the flag-audit workflow. |
| `references/high-risk-domains.md` | *How* to apply a high-risk domain policy. |

## Use it

The skill activates automatically when you talk about feature flags, rollouts, kill-switches, experiments, or Unleash — or invoke it directly with `/unleash:featureops`. Typical prompts:

- *"Should this checkout change be behind a feature flag?"* → runs `evaluate_change`
- *"Create a release flag for the new search ranking and wrap the endpoint."* → `detect_flag` → `create_flag` → `wrap_change`
- *"Roll out `checkout-stripe-integration` to 10% in staging."* → `set_flag_rollout` / `toggle_flag_environment`
- *"Run a flag audit on the default project."* → the audit workflow in `references/cleanup-cadence.md`

The five read-only tools (`evaluate_change`, `detect_flag`, `get_flag_state`, `list_projects`, `list_flags`) are pre-approved while the skill is active; write operations always prompt for confirmation.

## Customize for your team

Don't edit the skill's files — in a plugin install they live in a managed cache that a plugin update overwrites. Instead, put your team's policy in an **override file**; the skill loads it automatically (see the *Active policy* section of `SKILL.md`) and it survives updates.

- **Project override (recommended)** — create `./.unleash/featureops.md` in your repo and set only the values you want to change, especially your real high-risk domains. It's committed with the repo and wins over everything.
- **User override (optional)** — `~/.unleash/featureops.md` for personal cross-repo defaults.

Precedence: **project → user → shipped defaults**. [`references/policy-defaults.md`](references/policy-defaults.md) lists every value and doubles as the template — copy the sections you want to change. Or just ask the agent: *"set up a FeatureOps policy override for this project."*

The opt-in high-risk-edit hook is configured separately (it lives in the plugin repo's `hooks/`, not this skill) — point its `if` glob at your high-risk directories; see [`hooks/README.md`](https://github.com/Unleash/unleash-claude-skills/blob/main/hooks/README.md).

### Company-wide standardization (fork & republish)

If your whole company should share one policy, the heavier alternative is to **fork this repo, bake your policy into `references/policy-defaults.md`, and publish it as your own internal plugin** (see the [main README's "Add a new skill"](https://github.com/Unleash/unleash-claude-skills#add-a-new-skill) for the marketplace mechanics). Your developers install your fork and inherit your defaults with no per-repo override, and you pull upstream changes on your own schedule (`git merge`). Use this when the policy is an org standard rather than per-repo.
