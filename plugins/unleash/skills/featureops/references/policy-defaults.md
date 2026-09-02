# FeatureOps policy — defaults

This file is the **single source of truth** for every tunable value the FeatureOps skill uses. The other reference files (`feature-flag-conventions.md`, `rollout-guidance.md`, `cleanup-cadence.md`, `high-risk-domains.md`) describe *how* to apply these values — they never restate the numbers. When a value is needed, it comes from **the active policy** (defined below, as overridden by your team).

## How to customize (don't edit this file)

Do **not** edit this file to customize the skill — in a plugin install it lives in a managed cache that a plugin update overwrites. Instead, create an **override file** and set only the values you want to change; anything you omit falls back to the defaults here.

- **Project override (recommended):** `./.unleash/featureops.md` — committed with the repo, travels with it, and **wins** over everything. Put repo-specific policy here, especially [High-risk domains](#high-risk-domains).
- **User override (optional):** `~/.unleash/featureops.md` — your personal cross-repo defaults.

**Precedence: project override → user override → these defaults.** Create `.unleash/featureops.md` and copy in only the section headings you want to change, editing the values under them (leave the rest out — they fall back here). The quickest way to get a full starting copy is to ask the agent — *"set up a FeatureOps policy override for this project"* — and it will write the file from this template. See the skill README for the fork-and-republish alternative if your whole company standardizes on one policy.

---

## Parameters

### Flag naming
- **Convention:** `{domain}-{feature}-{variant}` — lowercase kebab-case, no underscores. `domain` matches the top-level `src/` directory; `variant` is the rollout/experiment arm (omit for simple release flags).

### Flag types and expected lifetimes
The five types `create_flag` accepts, and how long each is expected to live before it's "potentially stale" (Unleash's product defaults; mirror any per-type changes you made in the Unleash admin UI):

| Type | Purpose | Expected lifetime |
|---|---|---|
| `release` | gradual feature rollouts | 40 days |
| `experiment` | A/B tests, multivariate experiments | 40 days |
| `operational` | short-term system toggles (caching, batching, rate limits) | 7 days |
| `kill-switch` | emergency shutoff for external/high-risk paths | permanent |
| `permission` | role- or tier-based access | permanent |

`kill-switch` and `permission` are **permanent** — never treated as stale or audited for removal. Default type when unsure: `release` for new features, `kill-switch` for external-dependency integrations.

### When to require a feature flag
Call `evaluate_change` before implementing changes in these categories:
- Payment processing or billing
- Authentication, authorization, or session handling
- Data migrations or schema changes
- External integrations (third-party APIs, webhooks, message queues)
- Performance-sensitive paths (caching, rate limiting, batching)
- Any user-visible change to existing behavior

**Bar:** flag high-risk changes only. (Some teams require a flag for *all* user-facing changes — widen this list in your override if so.)

### Rollout — default
- **Milestones:** 10% → 50% → 100%
- **Holds:** 24h at the first milestone, 48h at each subsequent milestone
- **Advance when:** error rate healthy and p95 latency stable (see Halt thresholds for the numbers); at 50%, also no new regression reports
- **Environments, in order:** `development` → `staging` → `production`
- **Staging soak before production:** 24h with no regressions

### Rollout — high-risk override
Applies to any change in a [High-risk domain](#high-risk-domains):
- **Milestones:** 1% → 10% → 25% → 50% → 100%
- **Holds:** 48h at every milestone
- Halt thresholds are stricter (below)

### Halt thresholds
Pause the rollout immediately (call `set_flag_rollout` with `percentage: 0` for the affected environment — don't delete the flag) if, during a hold:
- **Error rate** exceeds **1%** (or 1.5× the pre-rollout baseline, whichever is higher). **High-risk: 0.1%.**
- **p95 latency** rises more than **20%** above the pre-rollout baseline.
- **User reports** of broken functionality arrive through any channel.
- **Downstream errors** (database, queue, third-party API) spike.

### Cleanup and staleness
- **No-activity window:** a flag with no SDK evaluation (`lastSeenAt`) for **30 days** in any enabled environment is a cleanup candidate.
- **Age vs. type:** a flag older than its type's expected lifetime (see the table above) is overdue.
- **Permanent types (never audited):** `kill-switch`, `permission`.
- **Audit cadence:** weekly (more often during release-heavy periods).
- **Ownership:** the engineer who created a flag is responsible for removing it.

---

## High-risk domains

Directories or modules that carry enough release risk that **every change is flag-protected by default**. Each domain policy has: **Scope** (path globs) · **Default flag type** · **Naming prefix** · **Required actions** · optional **Rollout override**. Replace the `payments` example below with your team's real domains in your override file — this is the section most teams customize most.

### payments
- **Scope:** `src/payments/**`, `src/billing/**`
- **Default flag type:** `kill-switch` for any change that calls an external payment provider (Stripe, PayPal, Adyen, …); `release` for internal payment logic that doesn't cross a network boundary.
- **Naming prefix:** `payments-` (e.g. `payments-stripe-integration`, `payments-refund-v2`)
- **Required actions:**
  1. Evaluate first (`evaluate_change`) before writing implementation code.
  2. Require a flag — even for "small" or "obvious" changes.
  3. Every external-provider call needs a realistic fallback (legacy provider, graceful failure, or queue-and-retry). Hand to the user if none is clear.
  4. Write at least one test that exercises the fallback (flag disabled).
  5. Default **off in production**; enable in staging first via `toggle_flag_environment`.
- **Rollout override:** use the high-risk ramp (1% → 10% → 25% → 50% → 100%, 48h holds, error halt at 0.1%).

<!-- Add more domains by copying the block above. A common second one is `auth`:
### auth
- **Scope:** `src/auth/**`, `src/middleware/auth*`, `src/session/**`
- **Default flag type:** `release` for new auth methods; `kill-switch` for identity-provider integrations
- **Naming prefix:** `auth-`
- **Required actions:** evaluate first; require a flag for any login/logout/session change; default off in production; roll out internal-first (target by employee email domain); have a documented rollback plan before 10%.
-->
