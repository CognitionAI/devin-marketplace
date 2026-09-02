---
name: migrate-gitlab-flags
description: Migrates a codebase from GitLab Feature Flags (the Unleash-compatible legacy API authenticated with UNLEASH-INSTANCEID) to a modern Unleash v8 server. Inventories flags and strategies, maps GitLab constructs to Unleash equivalents, provisions flags via multiple mechanisms (Unleash MCP server, import files, or direct Admin API), rewrites SDK configuration with minimal code changes, and verifies behavior parity. Use when asked to migrate off GitLab feature flags, move flags to Unleash, or port GitLab flag definitions to an Unleash server.
license: Apache-2.0
argument-hint: [path-to-app-or-repo]
disable-model-invocation: true
allowed-tools: mcp__unleash__list_projects mcp__unleash__list_flags mcp__unleash__detect_flag mcp__unleash__get_flag_state mcp__plugin_unleash_mcp__list_projects mcp__plugin_unleash_mcp__list_flags mcp__plugin_unleash_mcp__detect_flag mcp__plugin_unleash_mcp__get_flag_state
---

# Migrate GitLab Feature Flags to Unleash (v8+)

Migrate one app or service off GitLab's Unleash-compatible legacy flag API onto a real Unleash v8 server: recreate the flag definitions, rewrite the SDK wiring, and prove behavior parity. There is no automated import/export mechanism from GitLab to Unleash, therefore recreating definitions is always part of the job.

## Non-negotiable invariants

- **State carries over exactly.** A flag enabled in GitLab is enabled in Unleash; a disabled flag arrives disabled (per environment). Always — never ship flags "off for safety" or "on for convenience".
- **Flag names are unchanged** (the only exception: a collision prefix agreed with the user when sharing an OSS `default` project — see Inputs step 3).
- **Minimal code diff.** Mirror the existing patterns; the migration is not a refactoring opportunity (see Phase 5).
- **Least-privilege credentials.** The app gets an Unleash backend/frontend token scoped to its project + environment; the migration itself uses only the access level its provisioning mechanism requires. Never assume an admin token (admin tokens are deprecated by Unleash anyway, so automation uses personal access tokens or service accounts).

## Inputs

1. Resolve `$ARGUMENTS` to the target directory. If empty or ambiguous, ask the user which app/service to migrate before touching anything.
2. Detect the stack from manifests: `package.json`, `go.mod`, `pom.xml` / `build.gradle`, `Gemfile`, `composer.json`, `*.csproj`, `requirements.txt` / `pyproject.toml`, or plain shell scripts.
3. **Ask the user for the target topology and mechanism** (skip whatever the request already states; never assume the rest):
   - **Unleash edition** — OSS, or Enterprise/Cloud. Determines what is possible: OSS has a single `default` project and its Admin API cannot create environments; Enterprise/Cloud supports multiple projects, environments, change requests.
   - **Project topology** — Enterprise/Cloud best practice: **one project per service/application** (separation of concerns, per-project tokens and permissions). OSS: everything shares `default`, so agree on a collision-avoiding flag prefix (team/domain prefix, e.g. `checkout_…`) if the flags aren't already distinctly named.
   - **Provisioning mechanism** — one of the three in [references/provisioning.md](references/provisioning.md): Unleash MCP server (local or remote), import-file generation, or direct Admin API. Before asking, check whether an Unleash MCP server is already connected to this session — tools prefixed `mcp__unleash__` or `mcp__plugin_unleash_mcp__` (the latter is the Unleash plugin's bundled server, registered automatically on plugin installs; `claude mcp list` shows standalone entries) — and propose it if so. The mechanisms differ in the access the migration needs (PAT vs none vs elevated) — on a governed instance the user may not be able to hand an AI direct API access at all; import files are the least-privilege default there.
   - **Credentials** — only what the chosen mechanism needs, plus the project+environment-scoped backend token (`{project}:{environment}.{hash}`) the app itself will run with (it can also be created during Phase 4).
4. Run `${CLAUDE_SKILL_DIR}/scripts/preflight.sh <target-dir> --mode <api|import|mcp>` and stop on failure. Add `--frontend` only when the browser will talk to Unleash *directly* (Frontend API/Edge) — a BFF whose browser code never touches Unleash needs no frontend token.

## Phase 1 — Discover

Find every GitLab flag touchpoint in the target:

```
grep -rniE "feature_flags/unleash|UNLEASH-INSTANCEID|instance_?id|InstanceTag" <target-dir>
```

Also look for the appName-as-environment trick (an `appName` / `app_name` config value naming a GitLab environment like `production` rather than the application) and for SDK version pins that only exist to keep instance-id auth working. Read [references/gitlab-flags-primer.md](references/gitlab-flags-primer.md) for the before-state model and the per-SDK trap table before judging what you find.

Record: SDK + pinned version, abstraction style (direct calls, thin wrapper, DI service, port/adapter, OpenFeature provider, proxy, BFF), and every call site.

## Phase 2 — Inventory

Enumerate the flags the app depends on. Prefer the live source when GitLab credentials (`GITLAB_API_TOKEN` PAT + project id) are available:

```
curl -fsS -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  "$GITLAB_API_URL/projects/$GITLAB_PROJECT_ID/feature_flags?per_page=100"
curl -fsS -H "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  "$GITLAB_API_URL/projects/$GITLAB_PROJECT_ID/feature_flags_user_lists"
```

Fall back to code and any flag manifest in the repo. Do not inventory from the Unleash-compatible wire endpoint — it inlines user lists as `userWithId`, so the real construct is invisible there. Scope the inventory to the flags the target app actually references (the Phase 1 call sites) — a shared GitLab project often holds other services' flags and user lists, which are out of scope for a single-app run.

For each flag record: name, environment scopes, strategies (with parameters), user lists, and the global `active` bit. Also capture the before-state behavior table now, per [references/verification.md](references/verification.md) — you cannot capture it after the rewrite.

## Phase 3 — Map

Translate every GitLab construct to its Unleash v8 equivalent using [references/concept-mapping.md](references/concept-mapping.md). Do not drop anything silently — the inactive bit and environment scoping must carry over, and `groupId: "default"` must survive verbatim on every rollout strategy or percentage buckets shift.

## Phase 4 — Provision

Recreate flags, strategies, and segments through the mechanism chosen in Inputs step 3, following [references/provisioning.md](references/provisioning.md): segments first (every mechanism needs them to pre-exist), then flags, then strategies, then per-environment enable/disable — the state-parity invariant lands here. On Enterprise/Cloud, a freshly created project auto-attaches every globally-enabled instance environment — reconcile its environment set to the app's targets *before* provisioning strategies (details in provisioning.md). Provisioning must be idempotent or reviewable: check-before-create for API/MCP, a validated import file for the import path.

## Phase 5 — Rewrite

Swap the SDK wiring per [references/sdk-cheatsheet.md](references/sdk-cheatsheet.md), keeping the diff minimal — same files, same patterns, same abstraction:

- URL: GitLab project endpoint becomes `https://<host>/api` (backend) or `<host>/api/frontend` (browser).
- Auth: drop every instance-id knob; send `Authorization: <token>` instead — the app's project+environment-scoped backend token server-side, a frontend token in browsers.
- Environments: drop appName-as-environment — tokens are environment-scoped; appName goes back to naming the application.
- Modernize SDKs pinned only for instance-id auth (e.g. `no.finn.unleash` → `io.getunleash`, Node `unleash-client` ≤5 → current, Go module rename).
- Preserve the app's abstraction style: a wrapper stays a wrapper, a port/adapter migration lands in the adapter, DI registration stays DI, OpenFeature call sites don't change. Direct SDK calls stay direct — do NOT introduce an abstraction layer the code didn't have. If one would clearly pay off, *recommend* it in the final report based on [Unleash's own guidance](https://docs.getunleash.io/guides/manage-feature-flags-in-code#use-an-abstraction-layer), as follow-up work — never bundle it into the migration.
- Keep flag names, response shapes, and public behavior unchanged.

## Phase 6 — Verify

Follow the gate checklist in [references/verification.md](references/verification.md): re-run the identity matrix captured in Phase 2, diff against the before-state, grep for GitLab remnants, and start the app with all `GITLAB_*` env unset. Do not report the migration done until every gate passes; on a parity mismatch, return to Phase 3/4 — never weaken the oracle. If provisioning went through import files that someone else applies, verification waits until the import is committed — hand over the file plus the verification steps instead of skipping them.

## Special cases

- **Frontend apps behind Unleash Proxy**: delete the proxy container and its secrets; point the browser SDK at `/api/frontend` with a **frontend** token (a client token in a browser is a secret leak). Unleash Enterprise Edge replaces the proxy for high-traffic setups.
- **BFF frontends**: keep the BFF and its JSON contract byte-compatible; only the server-side SDK config changes.
- **OpenFeature providers**: rewrite the provider internals (or swap in an official provider with identical context mapping); evaluation call sites must not change, and fallback semantics (serve-default on timeout) must survive.
- **Ops/REST tooling**: scripts hitting the GitLab management REST API move to the Unleash Admin API, preserving each script's CLI contract; the global `active` bit becomes per-environment on/off — decide and document which environment(s) each script targets.
- **Config-only migrations**: when the SDK already speaks modern Unleash (e.g. Python `UnleashClient` 6.x) *and* the surrounding code is GitLab-agnostic, change only URL + auth header and leave the code alone. A GitLab-branded wrapper/adapter (hard-required instance-id, GitLab naming) is not config-only — rewrite it per the abstraction-preservation rule. "Config" includes the code lines that read/pass auth (env-var checks, client kwargs) — changing those does not break the config-only tier.
- **Workers / one-shot jobs**: verify via per-identity runs; clear stale `unleash-backup-*.json` files from tmp first so backup fallback cannot mask a broken connection.

## Scope

Default: migrate exactly one app/service per invocation. For a monorepo batch migration, run the skill once per service and share the Phase 2 inventory across runs — do not interleave rewrites of multiple services.

Resuming an interrupted migration: reconcile, don't redo. Audit the existing code diff against the cheatsheet (and the installed SDK's actual behavior) and the server state against the inventory; keep what's correct, fix what isn't, then continue from the first unfinished phase. If the working tree can no longer run against GitLab, capture the before-state oracle from the pristine version in version control.

---

## Metadata

- **License:** Apache-2.0
- **Privacy Policy:** https://www.getunleash.io/privacy-policy
- **Support:** support@getunleash.io · GitHub Issues at https://github.com/Unleash/unleash-claude-skills/issues
- **Source:** https://github.com/Unleash/unleash-claude-skills
