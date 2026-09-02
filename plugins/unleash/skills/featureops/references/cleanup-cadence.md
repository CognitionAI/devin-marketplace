# Cleanup cadence

Thresholds — the no-activity window, per-type expected lifetimes, which types are permanent, the audit cadence, and ownership — come from the **active policy** (see the *Active policy* section of `SKILL.md`). This file covers *how* to decide a flag is stale and *how* to remove it. Customize the thresholds via `.unleash/featureops.md`, not by editing this file.

---

Most feature flags are temporary by design. Flags have lifecycles: every flag should have an owner, a purpose, and an expiration plan. Stale flags accumulate technical debt, confuse future readers, and increase the risk that an unrelated change accidentally re-enables old code. This file applies when the conversation involves removing flags or auditing for cleanup opportunities.

## When a flag is ready for cleanup

A flag is a cleanup candidate when **any** of these hold (signals in order of confidence):

1. **Unleash marked it `stale: true`.** The strongest signal — Unleash's own staleness logic decided it's overdue for its type and age.
2. **No SDK has evaluated it within the policy's no-activity window** in any enabled environment (`environments[].lastSeenAt`). If clients aren't checking it, removing it from code won't change behavior.
3. **Its age exceeds its type's expected lifetime** (from the policy). 
4. **The feature has fully launched** and the legacy code path is no longer needed (user judgment, not metadata).
5. **The experiment has concluded** and a winning variant has been picked.

Skip flags whose type the policy marks **permanent** — they have no expected lifetime and are not audited for removal.

## Removal workflow

When the user asks to clean up a flag, follow this sequence:

### 1. Get the full picture

Call `cleanup_flag` with the flag name. The tool returns framework-specific guidance based on the language and conventions detected in the codebase. Expect it to include:

- Every file and (where determinable) line number where the flag is referenced — including indirect usages through wrappers.
- The current rollout state across all environments.
- The "enabled" branch — the code path that becomes the default after removal.
- A cleanup checklist tailored to the framework.

Trust the tool's output over your own grep instincts. Real codebases rarely have raw `unleash.isEnabled('flag-name')` calls everywhere; the tool knows how to find the indirect references.

### 2. Confirm the keep path

Before editing anything, confirm with the user which branch should be preserved:

- For a `release` flag at 100%: keep the enabled branch, remove the conditional.
- For an `experiment` flag: keep the winning variant, remove all others and the conditional.
- For a `kill-switch` flag that's being decommissioned: keep the "enabled" path (the new behavior).

Ask the user explicitly if there is any ambiguity. Do not guess.

### 3. Remove the flag's surface area

The shape of "remove the conditional" depends entirely on how the flag is used. Real codebases rarely have raw `unleash.isEnabled('name')` calls scattered through business logic — that's the textbook example, not the common case. Be ready for any of these patterns:

- **Custom wrapper functions:** `featureFlags.isEnabled('name')`, `flags.get('name')`, or project-specific helpers. Removing the flag means removing the call sites *and* potentially the wrapper if this was its only caller.
- **Dependency-injected flag service:** `this.flagService.isEnabled('name')` or constructor-injected `featureFlags`. Check whether the injection can be simplified after removal (e.g., a service that no longer needs the flags dependency).
- **React/Vue hooks and HOCs:** `useFlag('name')`, `useFeatureFlag('name')`, `withFeatureFlag('name')`. Removing the hook usage also means unwrapping the conditional rendering and possibly the HOC.
- **Decorators or annotations:** `@FeatureFlag('name')`, `[FeatureGate("name")]` in some Java/.NET stacks. The decorator itself disappears; whatever it guarded becomes unconditional.
- **Config-driven gating:** flag values mapped into a config object at startup (`config.features.newCheckout`). Remove the config entry, then trace every reader.
- **Server-side rendering / edge:** flag context passed into render functions, middleware, or CDN edge logic. Cleanup may span multiple deployment artifacts.
- **A/B routing:** experiment flags that route traffic to different controllers or templates. Cleanup means deleting the losing branch's code, not just the routing logic.
- **Test fixtures and mocks:** mock providers, fixture flag-state objects, `jest.mock('unleash-client')` setups. These often outlive the production code.
- **Analytics and logging:** flag name as a tag, dimension, or log field. Search for the literal flag-name string, not just the SDK call.

The `cleanup_flag` tool surfaces the language- and framework-appropriate patterns. Use its output as the source of truth. If it misses a pattern that exists in this codebase, surface that gap to the user — don't silently work around it.

After removing all references:

- Promote the "kept" branch to the surrounding scope.
- Delete the fallback/legacy branch entirely.
- Remove now-unused imports, wrappers, hooks, decorators, mocks, and config entries.
- Search the codebase for the literal flag name string (including dashes/underscores variants) to catch references in non-code locations like analytics events.

Do not leave the conditional in place with a TODO. The point of cleanup is to eliminate the branching, not document it.

### 4. Run the relevant tests

Run the test suite for the touched code paths. Pay special attention to:

- Tests that exercised the fallback/losing branch — they should be deleted, not patched to pass.
- Mock providers that listed the removed flag — these need updating.
- Snapshot tests that captured the old conditional rendering — re-snapshot intentionally.

### 5. Delete the flag from Unleash

Only after the code change is merged and deployed to production, delete (or archive) the flag in Unleash. If the flag is deleted while production code still references it, every call to `isEnabled()` returns `false` — silently switching production to the fallback path. Sequence matters.

For `kill-switch` flags, prefer **archive** over delete so the historical incident log is preserved.

### 6. Document the cleanup

If your team tracks technical-debt removal, mention the flag name and merge SHA in the PR description so the rollout history is searchable later.

## Periodic audits

Run a flag audit on the policy's cadence. Ask the agent to "run a flag audit" and it should follow these steps:

1. **Enumerate active flags** with `list_flags` (default `archived=false`).
2. **Enumerate archived flags** with a second `list_flags` call setting `archived=true`. Active and archived flags are disjoint result sets in Unleash; both calls are required for a complete inventory.
3. **Fetch each flag's state** via `get_flag_state` for the metadata the list view doesn't include (full environment data, last-seen-at per env, etc.).
4. **Skip** flags whose type the policy marks permanent — they are permanent by design.
5. **Surface** flags where any of these are true:
   - `stale === true` (Unleash already flagged it)
   - `archived === true` but code references may still exist (check with `cleanup_flag`)
   - all `environments[].lastSeenAt` older than the policy's no-activity window (no SDK is hitting it)
   - `age(createdAt)` exceeds the type's expected lifetime (overdue by the policy)
6. **Prioritize** by `stale === true` first, then archived, then by oldest `lastSeenAt`, then by how far age exceeds the expected lifetime.
7. **Report, don't act.** Produce a prioritized cleanup report for the user to triage. Do not call `cleanup_flag` or remove code automatically — the report is for triage.
8. If `get_flag_state` returns no `environments[]` data for some flags, note that in the report rather than guessing.

## What not to clean up automatically

Never auto-execute `cleanup_flag` followed by code removal without the user reviewing each step. Flag cleanup touches production code paths and can re-introduce bugs if the wrong branch is preserved. Always present the plan, get confirmation, then act.

## Related

- For naming and creation: `feature-flag-conventions.md`
- For rollout state checks: `rollout-guidance.md`
- For high-risk domain policies: the active policy (`references/policy-defaults.md`)
