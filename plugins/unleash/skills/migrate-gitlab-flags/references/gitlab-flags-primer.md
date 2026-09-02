# GitLab Feature Flags — before-state primer

How GitLab serves feature flags over its Unleash-compatible legacy client API, and the traps that shaped the code you are about to migrate. Wire behavior notes were verified against GitLab.com.

## API model

GitLab implements a **legacy Unleash client API** per project — and nothing else. No frontend API, no admin API, no Unleash Enterprise Edge.

```
API URL   https://gitlab.com/api/v4/feature_flags/unleash/<project_id>
          (SDKs append /client/features, /client/register, /client/metrics)
Auth      instance ID → sent as header UNLEASH-INSTANCEID (no token auth)
appName   the GITLAB ENVIRONMENT NAME → sent as header UNLEASH-APPNAME
```

Both values come from *Project → Deploy → Feature flags → Configure*.

**The appName inversion**: in Unleash, `appName` identifies the application and environments are first-class server objects. GitLab repurposes `appName` as the *environment selector* — each strategy carries environment scopes (exact name or wildcard like `review/*`), and GitLab serves a strategy only to clients whose `appName` matches. One process = one environment.

Flags are read-only over this API; all mutation happens through the GitLab management REST API (below).

## Wire strategies

GitLab serves exactly five strategy types on the wire:

| UI name | Wire name | Parameters |
|---|---|---|
| All users | `default` | `{}` |
| Percent rollout | `flexibleRollout` | `rollout` (0–100), `stickiness` (`default`/`userId`/`sessionId`/`random`), `groupId` |
| Percent of Users (legacy) | `gradualRolloutUserId` | `percentage`, `groupId` — userId only, anonymous excluded |
| User IDs | `userWithId` | `userIds` (comma-separated, inline) |
| User List | `gitlabUserList` | references a GitLab-side list via `user_list_id` |

Not supported by GitLab: variants, segments, custom context fields, custom strategies, impression data, metrics dashboards, dependent flags. Evaluation context is limited in practice to `userId`, `sessionId`, `remoteAddress`.

## SDK instance-id trap table

The Unleash SDK v6 generation removed the user-settable `instanceId` (it is auto-generated now), and GitLab authenticates on that exact value (otherwise it's a **401** response). Therefore GitLab-based apps need to pin old SDK versions or inject the header manually. Recognize the pattern during discovery instead of "fixing" it — removing the pin is a Phase 5 (Rewrite) action.

| SDK | GitLab-safe | Notes |
|---|---|---|
| Node `unleash-client` | ≤ 5.x | 6.x works only via `customHeaders: {"UNLEASH-INSTANCEID": …}` |
| Go `unleash-client-go` | v3 and v4 | [v5+](https://github.com/Unleash/unleash-go-sdk/releases/tag/v5.0.3) renamed the module to `unleash-go-sdk` in August 2025 |
| Ruby gem `unleash` | 5.x line | instance-id removal tracked upstream ([PR #179](https://github.com/Unleash/unleash-ruby-sdk/pull/179) form July 2024) |
| Java | any (`.instanceId()` kept) | but groupId/package renamed `no.finn.unleash` → `io.getunleash` at [5.0](https://github.com/Unleash/unleash-java-sdk/releases/tag/unleash-client-java-5.0.0) in October 2021 |
| Python `UnleashClient` | **all versions** | kept `instance_id` — easiest to miss during rewrite |
| PHP `unleash/client` | current | `->withInstanceId(...)` |
| .NET `Unleash.Client` | current | `InstanceTag`; removal tracked upstream ([PR #226](https://github.com/Unleash/unleash-dotnet-sdk/pull/226) from July 2024) |
| Unleash Proxy | **1.4.0 only** | 1.4.1+ bundles client v6 → 401 |

## Wire behavior gotchas

- **`groupId` must be `"default"`.** GitLab's API rejects any other value — its UI never exposes groupId and always writes `default`. Consequence: all percentage buckets in one project share one hash space (same userId + same rollout % ⇒ same outcome across flags). **Carry `groupId: "default"` over verbatim during migration** — Unleash's UI default (groupId = flag name) changes which users land in the bucket and silently breaks parity.
- **`gitlabUserList` never reaches clients.** GitLab expands it server-side and serves a plain `userWithId` with the member IDs inlined (`{"name":"userWithId","parameters":{"userIds":"alice,zed"}}`), so any SDK evaluates user lists without special support. A wire capture therefore cannot distinguish a user list from inline IDs — use the management API to find the real construct.
- **Inactive flags are served** with `enabled: false`, but a flag whose strategies all match *other* environments is **omitted from the response entirely** for the requesting appName. Absence ≠ disabled.
- **User list ids**: strategy payloads reference lists by their **global `id`**; the `feature_flags_user_lists/:iid` URL paths use the project-scoped **`iid`**. Mixing them up yields a plain `404 Not found`.

## Backup-file collision hazard

Several Unleash SDKs persist a fallback copy of flag definitions in the system temp directory named after the appName — both Node `unleash-client` and legacy Java default to `tmpdir/unleash-backup-<appName>.json`, with **incompatible formats** (the Node file lacks a `version` field and crashes the Java 4.4.1 deserializer with an NPE at startup). Because GitLab forces every service's appName to be the environment name, polyglot services on one host/CI runner collide on the same file; you may find explicit `.backupFile(...)` mitigations in the code. Migration to Unleash dissolves the root cause — appName goes back to identifying the application — so drop the mitigation unless appNames still collide for other reasons.

## Management REST API

PAT-authenticated (`PRIVATE-TOKEN: <token>` header) against `https://gitlab.com/api/v4` — use it in Phase 2 (Inventory) when credentials are available:

- `GET /projects/:id/feature_flags?per_page=100` — list flags with their strategies and environment scopes (the authoritative inventory source).
- `GET /projects/:id/feature_flags/:name` — one flag.
- `POST /projects/:id/feature_flags` — create (requires `version: "new_version_flag"`); strategies are updated **by id** from a prior GET, removed with `_destroy: true`.
- `GET /projects/:id/feature_flags_user_lists` — list user lists; `user_xids` is a comma-separated string. `PUT/DELETE …/:iid` — mutate by project-scoped iid (strategies reference lists by global `id`).

## Limits

Flags per project on GitLab: Free 50, Premium 150, Ultimate 200. The flag-serving endpoint counts against unauthenticated per-IP rate limits, which is the reason GitLab recommends fronting production with the Unleash Proxy.

## Related

- For what each construct becomes on the Unleash side: `concept-mapping.md`
- For recreating the definitions on the target: `provisioning.md`
- For the per-stack SDK rewrite: `sdk-cheatsheet.md`
