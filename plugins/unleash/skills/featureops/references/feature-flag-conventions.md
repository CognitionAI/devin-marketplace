# Feature flag conventions

Values — the naming convention, the flag types and their expected lifetimes, and which changes require a flag — come from the **active policy** (see the *Active policy* section of `SKILL.md`). This file covers *how* to apply them. Customize by creating `.unleash/featureops.md`, not by editing this file.

---

FeatureOps rests on a simple default: **every change is reversible.** If you cannot turn it off, you should not turn it on. Flags are how that default is enforced in code.

## 1. Evaluate risk before implementing

Before implementing a change that falls into the active policy's flag-required categories, call the Unleash MCP server's `evaluate_change` tool with a description of the change. It returns a recommendation; if it says yes, continue below.

## 2. Prefer reuse over creation

Always call `detect_flag` with a description of the new flag's intent **before** `create_flag`. If a suitable flag comes back, reuse it — reuse reduces flag sprawl and keeps related code paths consistent.

If nothing matches, call `create_flag`, naming the flag per the active policy's convention and choosing the type that matches its purpose (the policy lists the five types and when to reach for each — default to `release` for new features, `kill-switch` for external-dependency integrations).

## 3. Wrap with the right SDK pattern

After `create_flag` returns, call `wrap_change` with the file path and language context. It returns SDK-appropriate guard code — apply it verbatim, don't hand-roll equivalent checks.

For a TypeScript Express endpoint, expect output like:

```typescript
if (unleash.isEnabled('checkout-stripe-integration', context)) {
  return stripeService.processPayment(request);
} else {
  return legacyPaymentService.process(request);
}
```

Keep the fallback branch realistic — if there is no legacy path, the fallback should be a clear failure message, not a silent no-op. Resilience is designed, not improvised: decide what happens when the new path is off *before* you ship it.

## 4. Clean up after rollout

Every flag should have an owner, a purpose, and an expiration plan. See `cleanup-cadence.md` for the removal workflow.

## Tools available from this skill

The Unleash MCP server (configured in `.mcp.json`) exposes: `evaluate_change`, `detect_flag`, `create_flag`, `wrap_change`, `list_projects`, `list_flags`, `get_flag_state`, `set_flag_rollout`, `toggle_flag_environment`, `remove_flag_strategy`, `cleanup_flag`.

Read-only tools (`evaluate_change`, `detect_flag`, `get_flag_state`, `list_projects`, `list_flags`) are pre-approved via the skill's `allowed-tools`; every other tool prompts for confirmation. Use `list_projects` and `list_flags` for inventory discovery before creating new flags — `list_flags` is also the primitive behind the flag audit workflow in `cleanup-cadence.md`.
