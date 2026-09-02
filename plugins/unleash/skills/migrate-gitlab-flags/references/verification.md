# Verification — proving behavior parity

Phase 6 gates. The oracle is the app's own observable behavior captured **before** the rewrite — never a mental model of what the flags should do.

## Capture the before-state first

Before touching code, exercise every flag-reading surface (endpoints, CLI output, rendered pages) with a fixed identity matrix and record the results.

Build the matrix from the inventory: for each flag, include identities inside and outside its cohorts — user-list/constraint members and non-members, ids on both sides of every percentage bucket, plus an anonymous probe (no userId; it exercises the legacy anonymous-exclusion behavior). Sessions matter when any strategy uses `sessionId` stickiness. An app that sends no identity context at all collapses the matrix to repeated anonymous probes — that is the correct matrix, not a shortcut.

Capture recipe (adapt endpoint and params to the app):

```bash
ENDPOINT="http://localhost:<port>/<flag-reading-path>"
{
  echo "| identity | session | response |"
  echo "|---|---|---|"
  for u in alice bob carol dave ""; do
    for s in session-1 session-2; do
      q="sessionId=$s"; [[ -n "$u" ]] && q="userId=$u&$q"  # omit absent ids entirely
      r=$(curl -sS "$ENDPOINT?$q")   # no -f: 4xx bodies are behavior too
      echo "| ${u:-anonymous} | $s | $r |"
    done
  done
} | tee before-<app>.md
```

Absent identities must be omitted from the query string entirely — `userId=` (empty string) is a different evaluation context than no `userId` at all and silently shifts default-stickiness outcomes.

Namespace the capture files per app (`before-<app>.md`, not `before.md`) — parallel migrations of sibling services sharing a scratch directory will otherwise clobber each other's oracle.

Re-run the identical loop after migration into `after-<app>.md`; the gate is `diff before-<app>.md after-<app>.md` returning nothing. For apps without HTTP surfaces (workers, CLIs), capture their per-identity output the same way — run once per identity, record stdout.

If a response echoes SDK configuration the migration legitimately changes (e.g. an endpoint that prints `appName`, which Phase 5 renames from GitLab environment to application name), decide **before capturing** to exclude exactly that field from both captures (e.g. `jq 'del(.context.appName)'`) and note the exclusion. Flag-driven behavior always stays in the oracle, and the oracle is never adjusted after capture.

Random-stickiness strategies cannot byte-diff. Decide before capture to mask exactly that flag's value in both captures, and gate it statistically instead: over N≥100 evaluations the true-rate stays consistent with the strategy's rollout percentage (±3σ), and every identity observes both values across runs — proving the flag stayed per-evaluation rather than silently becoming sticky.

## Gate checklist

All gates must pass; there is no partial credit.

1. **Parity**: `diff before-<app>.md after-<app>.md` is empty.
2. **No GitLab remnants**:
   ```
   grep -rniE "feature_flags/unleash|UNLEASH-INSTANCEID|instance_?id|InstanceTag" <target-dir>
   ```
   returns nothing outside comments and lockfile noise (exclude vendored dependencies — `vendor/`, `node_modules/`, `.venv/` and similar — the SDK's own source legitimately mentions these strings). Prose documentation *describing* the before-state or the migration task itself (READMEs, exercise/ticket text) does not count as a remnant; config metadata that still claims GitLab (e.g. a package description) should be rewritten, and so should run instructions that no longer work because the migration deleted the infrastructure they reference (a start-the-proxy step, a dead port) — history is exempt, broken instructions are not.
3. **Clean environment**: the app starts and connects with every `GITLAB_*` environment variable unset; config comes only from the Unleash URL + token variables.
4. **Central cohorts**: wherever a GitLab user list existed, the Unleash side uses a segment — editing the cohort must not require touching the flag. Confirm the wiring by Admin API read-back of the strategy (`"segments": [<id>]`), not from the client API — `/api/client/features` may inline the segment's constraints into the strategy depending on the SDK's `Unleash-Client-Spec` header, so an empty or absent top-level `segments` key on the wire is not a dropped reference.
5. **Health**: whatever readiness signal the app exposes reports the SDK connected to the new server. Any SDK with a filesystem bootstrap/cache (Node and Java `unleash-backup-*` files, PHP's default filesystem cache) can serve stale flags and mask a dead server or bad credentials — run fail-closed checks with an isolated or cleared cache directory (e.g. a fresh `TMPDIR`).

## Per-shape variants

- **Workers / one-shot jobs**: no server to keep up — run the job once per identity (env vars or args carry the identity), or if the job sweeps its identities internally, treat one run as one full sweep and repeat runs for distributions; diff the collected stdout. Watch the first run after rewrite for backup-file fallback: a stale `unleash-backup-*.json` in tmp can mask a broken connection; clear it before verifying gate 5.
- **SPAs / frontend apps**: the browser must reach `<server>/api/frontend` directly — verify with a raw request first: `curl -fsS -H "Authorization: $UNLEASH_FRONTEND_TOKEN" "<server>/api/frontend"`. Then drive the identity matrix through the app itself (the frontend SDK sends context as query params); confirm the old proxy process/container is gone, not just unused. Anonymous probes are non-deterministic here for sessionId-stickiness rollouts — both the old Unleash Proxy and the frontend API invent a random sessionId per request when none is sent; treat them like random stickiness (mask + statistical gate).
- **SSR**: verify both render paths — server-rendered HTML for each identity and any client-side re-evaluation — they can disagree if only one side was rewritten.
- **Ops scripts**: parity means *equivalent effect*, not identical output. For each script, run the rewritten version against a scratch flag on the target server and confirm the resulting state via `GET /api/admin/projects/<project>/features/<flag>` (strategy parameters, on/off state, segment membership).
- **Config-only migrations**: code is untouched, so gate 2 applies only to config files; everything else applies unchanged.

## On failure

Diff mismatches point at Phase 3 (wrong mapping) or Phase 4 (wrong payload) far more often than Phase 5. The classic silent killer is `groupId`: a rollout provisioned with groupId = flag name instead of `"default"` reassigns every percentage bucket. An all-false after-state with the flags visible on the wire points at token/environment scope: flags stay present-but-disabled on `/api/client/features` even when the token's environment has been detached from the project, so presence checks pass while every evaluation stays false. Fix the definitions and re-verify. Never adjust the captured before-state table to match the after-state — the oracle does not move.

## Related

- On a parity mismatch, re-check the mapping first: `concept-mapping.md`
- For fixing provisioned definitions: `provisioning.md`
- For before-state gotchas that skew captures: `gitlab-flags-primer.md`
