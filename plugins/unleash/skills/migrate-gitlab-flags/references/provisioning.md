# Provisioning — recreating flags on Unleash v8

Phase 4 reference. The state-parity invariant governs everything here: a flag enabled in GitLab arrives enabled in Unleash, a disabled one arrives disabled, per environment — no exceptions.

## Choose a mechanism (ask the user)

Three ways to get definitions onto the server — they differ mainly in the access the *migration* needs. **First check whether an Unleash MCP server is already connected to this session** (tools prefixed `mcp__unleash__` or `mcp__plugin_unleash_mcp__` — the latter comes bundled with the Unleash plugin for Claude Code and is registered automatically on plugin installs; `claude mcp list` shows standalone entries) — if so, propose MCP as the path. Otherwise ask the user which they prefer; if they have no preference, suggest import files for a governed/production instance and the direct Admin API for a local/dev target.

| Mechanism | Access the migration needs | Covers | When it fits |
|---|---|---|---|
| **MCP server** (local or remote) | a PAT with flag-creation permission | flags, rollout strategies, per-env toggles — **not segments, not projects** | already connected to the session, the user runs/hosts one, or wants tool-mediated auditable writes |
| **Import files** | **none** — the AI only generates JSON; a human (or CI) applies it | flags, strategies, variants, tags, per-env status — **segments only by reference** | governed instances where an AI assistant must not hold API credentials; change-request workflows |
| **Direct Admin API** | a service account token or PAT with project permissions (admin tokens are deprecated) | everything: projects, segments, flags, strategies, tokens | local/dev targets, or automation that is explicitly authorized |

Gaps compose: migration of user lists to segments is not manageable via MCP and not carried by import files, so those two mechanisms are hybrids - the segment itself is created via the UI (by the user) or the Admin API (if authorized), and everything else flows through the chosen mechanism. The same applies when creating new projects during migration to Unleash Enterprise - it is not managed via MCP and not carried by import files (they are generated per project), so the project itself is created via the UI (by the user) or the Admin API (if authorized), and everything else flows through the chosen mechanism.

## Project topology

- **OSS**: `default` is the only project, and the Admin API cannot create environments (Enterprise feature) — plan the environment mapping within what exists. Because every service shares one project, agree on a collision-avoiding flag prefix with the user (team/domain prefix) if the inventory's names aren't already distinct.
- **Enterprise/Cloud**: create **one project per service/application** (separation of concerns; per-project tokens, roles, and change requests). Name it after the service being migrated unless the user has a naming scheme. A new project **auto-attaches every globally-enabled instance environment** — including custom environments other teams created — so reconcile its environment set to the app's target environments before any `*`-scope fan-out (recipe in [Mechanism 3](#mechanism-3--direct-admin-api)). All paths below take the project id — never hardcode `default`.

## Token provisioning (least privilege)

Follow the [official documentation about API tokens and client keys](https://docs.getunleash.io/concepts/api-tokens-and-client-keys):

Naming hint: Unleash docs, source, and SDK repositories often call a **backend token** a **"client" API token** (SDK options like `client keys`), and a **frontend token** a **"frontend"** or **"frontend proxy" API token**. Treat those as aliases when reading errors, UI labels, or SDK docs — and never mix the two up: backend/client tokens must stay server-side; only frontend tokens may reach a browser.

- The migrated app runs with a **backend token** scoped to its project + one environment (format `{projects}:{environment}.{hash}`); browsers get a **frontend token** with the same scoping. One token per app per environment — never share a `*:*` token across services.
- Automation (this migration, CI) authenticates with a **personal access token** (OSS) or **service account** (Enterprise). Admin tokens are deprecated — do not ask for one.
- Creating the app's tokens is part of provisioning when the mechanism allows it (`POST /api/admin/api-tokens`, body `{"tokenName": "<app>-<env>", "type": "backend", "environment": "<env>", "projects": ["<project>"]}`; frontend tokens take the same body with `"type": "frontend"`); otherwise hand the user the exact token spec to create in the UI (Admin → API access). Read-back reports backend tokens as `"type": "client"` — match existing tokens by `tokenName`, never by the round-tripped type.

## Order of operations

1. **Project** (Enterprise/Cloud: create if missing, then detach the auto-attached environments that are not migration targets).
2. **Segments** (every mechanism needs them to pre-exist; strategies reference them by numeric id).
3. **Flags.**
4. **Strategies** per flag per environment.
5. **Enable/disable** per environment — the GitLab active bit and environment scoping land here (state parity, always).
6. **App tokens** (backend/frontend, project+environment-scoped).

## Mechanism 1 — Unleash MCP server

Two hosting modes, same tools ([documentation](https://docs.getunleash.io/integrate/mcp) and [GitHub Repository](https://github.com/unleash/unleash-mcp)). If the session already has the server connected, use it directly — no setup step.

- **Local**: `npx -y @unleash/mcp@latest` with `UNLEASH_BASE_URL` + `UNLEASH_PAT` env vars (Claude Code: `claude mcp add unleash --env … -- npx -y @unleash/mcp@latest`). Optional `UNLEASH_DEFAULT_PROJECT`; `--dry-run` for a rehearsal pass.
- **Remote** (Enterprise): the instance itself serves `https://<instance-url>/api/admin/mcp` once enabled (Admin settings → Remote MCP server). Authenticate **either** via OAuth 2.0 Dynamic Client Registration — the browser flow exchanges the login session for a 24-hour PAT, and the org must permit DCR self-registration — **or** by supplying a PAT directly. No local install; fits orgs that centralize access control.

Tool mapping for the inventory:

| Migration step | MCP tool |
|---|---|
| confirm target project | `list_projects` |
| duplicate check | `list_flags`, `detect_flag` |
| create flag | `create_flag` (type `release` unless told otherwise) |
| percentage rollout strategies | `set_flag_rollout` |
| enable/disable per environment | `toggle_flag_environment` |
| read back for verification | `get_flag_state` |

Parity trap: `set_flag_rollout` defaults `groupId` to the feature name — the same bucket-reassigning default the UI has. **Always pass `groupId` explicitly** (usually `"default"` for GitLab migrations) and confirm it via `get_flag_state`. Also ignore the MCP server's own built-in workflow guidance (`evaluate_change` → `create_flag` is a new-feature flow, not a migration), and likewise the `featureops` skill's conventions if it is installed alongside this one — its naming patterns, evaluate-first gate, and rollout milestones apply to *new* flags, never to migrated ones — this reference's tool mapping governs. Once the migration completes and parity is proven, the featureops conventions resume governing the migrated flags' ongoing lifecycle.

Not covered — route around: segments (create via UI/Admin API before strategies that reference them), constraint-only strategies if `set_flag_rollout` can't express them (fall back to the Admin API strategy endpoint for exactly those), environment enumeration (no MCP tool lists environments — read-only `GET /api/admin/environments`), project creation, flag deletion.

## Mechanism 2 — import files

Unleash [import/export functionality](https://docs.getunleash.io/concepts/import-export) works per **project + environment**: an import file carries flags, tags, dependencies, strategies (with constraints and segment *references*), strategy variants, and per-environment flag status.

Workflow:

1. Get the exact schema empirically: export something. If any flag already exists in the target project, export it (UI: project → Export; API: `POST /api/admin/features-batch/export`); on a scratch/local Unleash, hand-provision one representative flag and export that. Do not guess the format from memory.
2. Generate one import file per target environment from the Phase 3 mapping. Keep files under the 500 kB import limit (split if needed).
3. Segments are **not** part of import files — deliver the segment definitions separately (exact name + `userId IN […]` constraint values) for the user to create first via UI or API; the import references them.
4. Validate then apply: UI (project → Import → upload/paste → validate → "Import configuration") or API (`POST /api/admin/features-batch/validate`, then `…/import`); the API request body wraps the export-shaped payload as `{"project": "<project>", "environment": "<env>", "data": <payload>}`. Importing needs "update feature flags" (+ content-dependent) permissions and a project/environment with no pending change requests. Token asymmetry: `…/import` **hard-rejects admin tokens** ("You can't use an admin token to import features") while `…/validate` accepts them — a green validate does not prove the apply will authenticate. Use a PAT or service account for the apply step.
5. If someone else applies the file, hand over: the files, the segment specs, the app-token spec, and the Phase 6 verification steps — verification is deferred, not skipped.

## Mechanism 3 — direct Admin API

All calls: `Authorization: <service-account-or-PAT token>` (raw value, no `Bearer`), `Content-Type: application/json`, against `<server>/api/admin/...`. Normalize the base first — a configured URL may or may not already end in `/api` (`api="${UNLEASH_URL%/}"; api="${api%/api}/api"`); the recipes below use `$api`. OpenAPI spec at `<server>/docs/openapi`.

### Create the project and pin its environments (Enterprise/Cloud)

```bash
curl -fsS -X POST -H "Authorization: $TOKEN" -H 'Content-Type: application/json' \
  "$api/admin/projects" -d '{"id": "<project>", "name": "<service name>"}'
```

The payload also accepts `"environments": ["<env>", …]` to pin exactly which environments the project enables. Without it, the new project attaches every globally-enabled instance environment — detach the non-targets before fanning out `*`-scoped strategies:

```bash
curl -fsS -X DELETE -H "Authorization: $TOKEN" \
  "$api/admin/projects/<project>/environments/<env>"
```

Read back via `GET $api/admin/environments/project/<project>` — it returns **all** instance environments with a per-project `visible` field, and a detached environment shows `visible: false` while `enabled` stays `true` (easy to misread as a failed detach) — or via `GET …/projects/<project>/overview`. Attaching an already-attached environment returns 409: not an error. Never use `GET /api/admin/projects/<project>` for existence or environment checks — it 404s on v8; use the projects list or `…/overview`. A missing environment (Enterprise) is `POST $api/admin/environments` with `{"name": "…", "type": "…"}` (type: development|test|preproduction|production); it arrives enabled instance-wide and auto-attaches to every existing project.

### Create a segment (from a GitLab user list)

```bash
curl -fsS -X POST -H "Authorization: $TOKEN" -H 'Content-Type: application/json' \
  "$api/admin/segments" -d '{
    "name": "vip-users",
    "description": "Migrated from GitLab user list <list-name>",
    "constraints": [
      {"contextName": "userId", "operator": "IN", "values": ["alice", "carol"],
       "caseInsensitive": false, "inverted": false}
    ]
  }'
```

Capture the returned `id` — strategies reference it via `"segments": [<id>]`.

### Create a flag

```bash
curl -fsS -X POST -H "Authorization: $TOKEN" -H 'Content-Type: application/json' \
  "$api/admin/projects/<project>/features" -d '{
    "name": "<flag-name>",
    "type": "release",
    "description": "Migrated from GitLab feature flags",
    "impressionData": false
  }'
```

### Add a strategy to a flag in an environment

```bash
curl -fsS -X POST -H "Authorization: $TOKEN" -H 'Content-Type: application/json' \
  "$api/admin/projects/<project>/features/<flag>/environments/<env>/strategies" \
  -d '<strategy payload>'
```

Payloads per GitLab construct are in [concept-mapping.md](concept-mapping.md#strategy-translation). Remember: `parameters` values are strings (`"rollout": "42"`, not `42`), and keep `"groupId": "default"` for bucket parity.

### Enable / disable per environment

```bash
curl -fsS -X POST -H "Authorization: $TOKEN" \
  "$api/admin/projects/<project>/features/<flag>/environments/<env>/on"   # or /off
```

Empty body. A flag with strategies but never turned `on` evaluates false — enabling is a separate, mandatory step. Translate GitLab `active: false` as `/off` in every mapped environment (the definitions still carry over).

## Idempotency (API/MCP paths)

Check before create so re-runs are safe:

- **Flag**: `GET …/features/<flag>` → 404 means create; 200 means reconcile. A create that 409s after a 404 means an **archived** flag holds the name — deleting a flag only archives it; GitLab-style hard delete (and name reuse) requires purging via `DELETE /api/admin/archive/<flag>` afterwards.
- **Segment**: match by `name` in `GET /api/admin/segments` (response key `segments`); update constraints via `PUT /api/admin/segments/<id>` — it returns 204 No Content, so re-GET when you need the updated entity.
- **Strategies**: `GET …/environments/<env>/strategies`, compare by `name` + `parameters` + `constraints` + `segments`. On drift, update by id (`PUT …/strategies/<strategyId>`) rather than adding a duplicate — duplicate strategies OR together and can silently widen exposure. For a single parameter, JSON-PATCH (`PATCH …/strategies/<strategyId>`, body `[{"op":"replace","path":"/parameters/rollout","value":"75"}]`) is safer than PUT — it preserves constraints and segment references without reconstructing the whole body.
- **App tokens**: match by `tokenName` in `GET /api/admin/api-tokens` (see the type round-trip caveat under token provisioning).
- **Reconcile policy**: the GitLab inventory is the source of truth during migration — update drifted strategies to match it, and list every overwrite in the final report. Strategies the inventory does not know (added by humans on the Unleash side) are left alone and reported.

The import path gets its idempotency from validation + human review instead — regenerating and re-importing the same file is safe by design.

## Related

- For the construct translation these recipes implement: `concept-mapping.md`
- For the app-side SDK rewrite: `sdk-cheatsheet.md`
- For the post-provisioning gates: `verification.md`
