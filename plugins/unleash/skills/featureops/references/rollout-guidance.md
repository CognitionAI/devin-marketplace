# Rollout guidance

The numbers — milestones, hold durations, halt thresholds, environments, and the stricter high-risk override — come from the **active policy** (see the *Active policy* section of `SKILL.md`). This file covers *how* to run a rollout. Customize the numbers via `.unleash/featureops.md`, not by editing this file.

---

This file applies when rolling out feature flags. Use it to configure `set_flag_rollout` and `toggle_flag_environment`.

Small batches beat big bangs: releasing to a slice of users and watching the metrics is safer than releasing to everyone and hoping. Progressive exposure limits blast radius and gives real feedback before full commitment.

## Progressive rollout

Advance a new release flag through the active policy's milestones, holding at each for the policy's hold duration and advancing only when its advance criteria are met. For a change in a high-risk domain, use the policy's **high-risk ramp** instead — more steps, longer holds, and stricter halt thresholds.

## Halt conditions

During any hold, watch the active policy's halt thresholds (error rate and p95 latency), plus user reports of broken functionality and spikes in downstream systems (database, message queue, third-party APIs). If any threshold is breached, pause immediately: call `set_flag_rollout` with `percentage: 0` for the affected environment. Do **not** delete the flag — pausing preserves the rollout history for the postmortem. This is precision rollback: disable what is broken, leave everything else running.

## Per-environment activation

Use `toggle_flag_environment` to enable a flag one environment at a time, in the active policy's environment order:

1. **development** — enable as soon as the flag is created; default-on for local testing.
2. **staging** — enable after integration tests pass against the new code path.
3. **production** — enable only after staging has run the new path for the policy's staging soak with no regressions.

Never enable in production before staging unless the user explicitly confirms (e.g. pre-positioning a kill-switch).

## Targeting strategies

`set_flag_rollout` supports targeting beyond simple percentages:

- **Internal-first:** target by employee email domain or a `userType=employee` context attribute — use this before any external exposure.
- **Beta users:** target a named segment (a curated early-access list).
- **Geographic:** target by region for regulatory or capacity reasons.
- **Sticky percentage:** hash on `userId` so the same user sees consistent behavior across requests.

Always include a sticky identifier so the user experience is consistent across sessions.

## Tools to use

- `set_flag_rollout` — configure percentages, strategies, and targeting.
- `toggle_flag_environment` — enable/disable in a specific environment.
- `get_flag_state` — check current rollout state before changing it.
- `remove_flag_strategy` — clean up unused strategies as the rollout simplifies.

## Related

- Naming and creation: `feature-flag-conventions.md`
- Cleanup after a rollout reaches 100%: `cleanup-cadence.md`
- High-risk domain policies (and their rollout override): the active policy — see `SKILL.md` and `high-risk-domains.md`
