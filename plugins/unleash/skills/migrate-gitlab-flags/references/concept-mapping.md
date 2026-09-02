# Concept mapping — GitLab constructs → Unleash v8

The translation table applied in Phase 3. Every row of the inventory must map to exactly one row here; anything unmapped is a blocker, not a skip.

## Auth and connection model

| | GitLab (before) | Unleash v8 (after) |
|---|---|---|
| Backend SDKs | project URL + `UNLEASH-INSTANCEID` | `https://<host>/api/` + `Authorization: <backend token>` |
| Frontend SDKs | impossible (proxy/BFF workarounds) | `/api/frontend` or Unleash Enterprise Edge + frontend token |
| Environment selection | `appName` string matching | project+environment-scoped token: `{projects}:{environment}.{hash}` |
| Admin/tooling | GitLab REST API (PAT) | Unleash Admin API `/api/admin/...` (PAT / service account — admin tokens are deprecated) |

## Project and edition mapping

| GitLab construct | Unleash OSS | Unleash Enterprise |
|---|---|
| GitLab project (shared by many services) | The single `default` project — agree a collision-avoiding flag prefix with the user if names aren't already distinct | One Unleash **project per service/application** (separation of concerns, per-project tokens/roles). |
| environments (`production`, `staging`, ad-hoc) | First-class environments, but **cannot create environments via the Admin API** | Map to the environments that exist, and carry strategies for unmappable scopes over disabled, documenting the decision |

## Strategy translation

Payload sketches are the strategy body for `POST /api/admin/projects/<project>/features/<flag>/environments/<env>/strategies` (full recipes in [provisioning.md](provisioning.md)). All `parameters` values are **strings**, per the Unleash API.

| GitLab construct | Unleash v8 equivalent | Strategy payload sketch |
|---|---|---|
| environment scope on a strategy (`production`, `staging`) | first-class **environment**: create the strategy under that environment; enable/disable is per environment | n/a — scope picks the `<env>` in the URL |
| wildcard scope (`review/*`, `*`) | no first-class equivalent. `*` → every environment attached to the project (enumerate via `GET /api/admin/environments/project/<project>` keeping only `visible: true` rows, or `GET …/projects/<project>/overview` — never `GET /api/admin/projects/<project>`, which 404s on v8). An ephemeral family like `review/*` maps to **one shared environment** for the whole family (environment names cannot contain `/`, and per-instance environments do not scale) — each instance selects it via that environment's scoped token | n/a — fan out over environments |
| flag `active: false` (global bit) | flag **disabled in every mapped environment** (`POST …/environments/<env>/off`) — carry over, never drop | n/a |
| `default` strategy | gradual rollout at 100% | `{"name":"flexibleRollout","parameters":{"rollout":"100","stickiness":"default","groupId":"default"}}` |
| `flexibleRollout` | same strategy — copy `rollout`, `stickiness`, `groupId` verbatim | `{"name":"flexibleRollout","parameters":{"rollout":"<r>","stickiness":"<s>","groupId":"default"}}` |
| `gradualRolloutUserId` (legacy) | gradual rollout with **userId stickiness** — same murmur3 bucketing, and missing userId evaluates false, matching the legacy anonymous exclusion | `{"name":"flexibleRollout","parameters":{"rollout":"<percentage>","stickiness":"userId","groupId":"default"}}` |
| `userWithId` (removed in Unleash v7) | gradual rollout 100% + **constraint** `userId IN […]` | `{"name":"flexibleRollout","parameters":{"rollout":"100","stickiness":"default","groupId":"default"},"constraints":[{"contextName":"userId","operator":"IN","values":["alice","zed"]}]}` |
| `gitlabUserList` | **segment** (reusable, centrally managed) referenced by a 100% rollout strategy | `{"name":"flexibleRollout","parameters":{"rollout":"100","stickiness":"default","groupId":"default"},"segments":[<segmentId>]}` |
| Unleash Proxy in front of GitLab | delete it — Frontend API or Unleash Enterprise Edge with a frontend token | n/a |
| GitLab management REST scripts | Admin API (`/api/admin/projects/<project>/features/...`) | see [provisioning.md](provisioning.md) |

## Parity-critical details

- **Keep `groupId: "default"`.** GitLab forces it, so all rollout buckets in a project share one hash space. Unleash's UI default is groupId = flag name — letting that default win reassigns bucket membership and breaks parity for every percentage rollout. Only diverge deliberately, after parity is proven.
- **`gitlabUserList` inventory comes from the management API**, not the wire — on the wire it is indistinguishable from inline `userWithId` (GitLab expands it). Map the *management-API* construct: list → segment, inline → constraint.
- The context field names stay `userId`, `sessionId`, `remoteAddress`; only transport and auth change, not evaluation context.

## Rules of thumb

- User lists become **segments**, never inlined ID constraints — the cohort must stay editable without touching any flag that references it. Name the segment after the cohort (e.g. `vip-users`), not after a flag.
- Anything GitLab could not express (variants, non-userId constraints, dependent flags) is out of scope for parity — do not invent configuration the before-state did not have. Note such opportunities in the final report instead.
- Flag names never change. Unleash flag `type` is not modeled by GitLab — use `release` unless the user says otherwise.

## Related

- For the before-state model behind these constructs: `gitlab-flags-primer.md`
- For the payload recipes and provisioning mechanisms: `provisioning.md`
- For proving the mapping preserved behavior: `verification.md`
