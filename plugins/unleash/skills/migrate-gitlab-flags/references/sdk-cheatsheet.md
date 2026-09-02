# SDK cheatsheet — before → after per stack

Config deltas applied in Phase 5. Each section: the GitLab-pointed *before* shape to recognize, the Unleash v8 *after* shape to produce, and gotchas.

## Universal conventions (read first)

These apply to every backend section below; sections only note deviations.

- **URL**: `UNLEASH_URL` pointing at `https://<host>/api` (the SDK appends `/client/features` etc.). Browsers use `<host>/api/frontend` instead.
- **Auth**: `Authorization: <token>` header — backend token for server SDKs, frontend token for browser SDKs, raw token value with no `Bearer` prefix. Least privilege: the token is scoped to this app's project + one environment (`{projects}:{environment}.{hash}`), one per app per environment — never a shared `*:*` or admin token. Every instance-id knob (`instanceId`, `instance_id`, `InstanceTag`, `UNLEASH-INSTANCEID` headers) is deleted, not just emptied. Alias warning: docs/SDKs often say **"client" token** for the backend token and **"frontend proxy" token** for the frontend token — same things; don't cross them (backend/client token never ships to a browser).
- **appName**: goes back to identifying the *application* (e.g. the service name). The environment is selected by the token's scope, never by appName. Beware a legacy env var (e.g. `UNLEASH_APP_NAME=production`) still carrying the GitLab environment name — keeping that read silently resurrects the trick; set the application name explicitly.
- **Keep** refresh/metrics intervals, event handlers, health-check wiring, and the app's abstraction style exactly as they were.
- **Env hygiene**: the app must configure itself from `UNLEASH_URL` + `UNLEASH_CLIENT_TOKEN` (and `UNLEASH_FRONTEND_TOKEN` where applicable) with every `GITLAB_*` variable unset.

## Node — direct (`unleash-client`)

**Before** — v5 pin (`instanceId` option) or v6 with the header hack:
```js
const unleash = initialize({
  url: process.env.GITLAB_UNLEASH_URL,
  appName,                                   // GitLab environment name
  instanceId,                                // v5 form
  // v6 form: customHeaders: { 'UNLEASH-INSTANCEID': instanceId },
  refreshInterval: 15000, metricsInterval: 60000,
});
```
**After** — upgrade to current `unleash-client` (≥6; the pin existed only for instance-id auth):
```js
const unleash = initialize({
  url: process.env.UNLEASH_URL,
  appName: 'my-service',
  customHeaders: { Authorization: process.env.UNLEASH_CLIENT_TOKEN },
  refreshInterval: 15000, metricsInterval: 60000,
});
```
**Gotchas** — a v6 `customHeaders: {'UNLEASH-INSTANCEID': …}` hack must not survive as dead config; the `synchronized`/`error` event wiring carries over unchanged.

## Node — OpenFeature provider

**Before**: a hand-written `Provider` wrapping `unleash-client` v5 pointed at GitLab (`targetingKey` → `userId`; boolean resolver only, other types return `defaultValue`).

**After** — default: keep the provider's *role* and rewrite only its internals — the wrapped `initialize({...})` gets the Node-direct "after" config above. Call sites (`OpenFeature.setProviderAndWait`, `client.getBooleanValue`) do not change. A provider class/file literally named after GitLab (e.g. `GitLabUnleashProvider`) is GitLab-claiming metadata — rename it (touches only the call-site import); preserve its context mapping and fallback semantics, not its branding. Escape hatch: swap in an official Unleash OpenFeature provider if one now covers your SDK generation — verify its context mapping (`targetingKey` → `userId`) matches the hand-written one first.

**Gotchas** — preserve the provider's timeout-and-serve-false fallback semantics; a provider that throws where the old one returned `false` changes worker behavior.

## Browser — SPA behind Unleash Proxy

**Before**: `@unleash/proxy-client-react` `FlagProvider` → Unleash Proxy (pinned 1.4.0 — later versions bundle client v6 and get 401 from GitLab) → GitLab. The proxy runs as a container configured with `UNLEASH_URL` (GitLab), `UNLEASH_INSTANCE_ID`, `UNLEASH_PROXY_SECRETS`, and a dummy `UNLEASH_API_TOKEN`.

**After** — delete the proxy entirely; the browser talks to Unleash directly:
```tsx
const config = {
  url: `${UNLEASH_HOST}/api/frontend`,
  clientKey: UNLEASH_FRONTEND_TOKEN,       // frontend token, NEVER the client token
  appName: 'my-spa',
  refreshInterval: 15,
};
<FlagProvider config={config}>...</FlagProvider>
```
**Gotchas** — remove the proxy's compose service/container and its secrets, not just the reference; `useFlag`/`useUnleashContext` call sites are unchanged. A client (backend) token in the browser is a secret leak — the frontend token is the only one that may ship to browsers. For high-traffic production, Unleash Edge takes the proxy's old place. Browser apps take config at build/dev-server time (e.g. Vite `VITE_*` vars) — mirror the app's existing variable pattern rather than inventing server-style names. Replace hardcoded proxy fallbacks with a fail-closed default (empty `clientKey`, not a baked-in secret). Note the current SDK package names literally contain "proxy" (`unleash-proxy-client`, `@unleash/proxy-client-react`) — don't let a proxy-remnant grep flag the SDK itself; if the direct `unleash-proxy-client` dep is only a peer of the React SDK, drop it and let peer resolution supply it.

## Browser — BFF pattern

**Before**: server evaluates flags with a backend SDK and exposes plain JSON (e.g. `GET /api/flags?sessionId=…`); the browser polls that endpoint with no Unleash SDK at all.

**After** — default: keep the BFF shape and apply the Node-direct "after" config server-side; the browser code does not change at all. Escape hatch: retire the BFF's flag role and point a browser SDK at `/api/frontend` with a frontend token — only worth it if the BFF exists solely for flags.

**Gotchas** — the BFF's response shape is public API for its frontend; keep it byte-compatible.

## Next.js — SSR (`@unleash/nextjs`)

**Before**: `getDefinitions({ url: `${gitlabUrl}/client/features`, appName, instanceId })` then in-process `evaluateFlags` + `flagsClient`.

**After** — the package supports Unleash natively via env vars:
```
UNLEASH_SERVER_API_URL=https://<host>/api
UNLEASH_SERVER_API_TOKEN=<client token>
```
```ts
definitions = await getDefinitions({ fetchOptions: { next: { revalidate: 15 } } });
const { toggles } = evaluateFlags(definitions, { userId, sessionId });
```
**Gotchas** — the env vars are just defaults for `getDefinitions`' first-class `url`/`token` options; pass those explicitly when the org standardizes on different variable names. `getDefaultConfig()` also silently reads `UNLEASH_APP_NAME` — the legacy-env-var trap from the universal conventions applies with force here; set `appName` explicitly. Drop `appName` from the evaluation context if it was only carrying the GitLab environment; keep the empty-definitions fallback (`{ version: 1, features: [] }`) so fetch failures still fail closed. `getDefinitions` returns the error JSON body instead of throwing on non-2xx, so a connectivity check keyed on "did it return" misses 401s — validate the response shape (a `features` array) before trusting it. It also logs a spurious "Using fallback Unleash API URL" warning whenever the configured URL string equals its built-in default — harmless, common on local targets. Verify both server-rendered and client-side paths after the swap.

## Python (`UnleashClient`)

**Before**
```python
UnleashClient(url=URL, app_name=APP_NAME, instance_id=INSTANCE_ID,
              refresh_interval=15, metrics_interval=60)
```
**After** — no SDK swap needed (`UnleashClient` 6.x already speaks modern Unleash — this is often a config-only migration):
```python
UnleashClient(
    url=os.environ["UNLEASH_URL"],
    app_name="my-service",
    custom_headers={"Authorization": os.environ["UNLEASH_CLIENT_TOKEN"]},
    refresh_interval=15, metrics_interval=60,
)
```
**Gotchas** — the Python SDK **kept** `instance_id` across all majors, so nothing forces its removal: grep for it explicitly. Health checks that gate on `is_initialized` alone pass even when auth fails — keep (or add) the `feature_definitions()` non-empty check. The SDK's local cache (fcache-based, not `unleash-backup-*.json`) is keyed by appName — the appName rename gives a fresh cache namespace, so a stale-cache false-positive is unlikely but a cold first fetch is guaranteed.

## Go — direct (`unleash-client-go`)

**Before**
```go
unleash.Initialize(
    unleash.WithUrl(url), unleash.WithInstanceId(instanceID),
    unleash.WithAppName(appName),
    unleash.WithRefreshInterval(15*time.Second),
)
```
**After** — default: move to the renamed current module (`github.com/Unleash/unleash-go-sdk`; v5 renamed it from `unleash-client-go`), token auth via header:
```go
unleash.Initialize(
    unleash.WithUrl(os.Getenv("UNLEASH_URL")),
    unleash.WithAppName("my-service"),
    unleash.WithCustomHeaders(http.Header{"Authorization": {os.Getenv("UNLEASH_CLIENT_TOKEN")}}),
    unleash.WithRefreshInterval(15*time.Second),
)
```
Escape hatch: v3/v4 with `WithCustomHeaders` works against Unleash unchanged, but the module is frozen — prefer the rename unless the diff must stay minimal.

**Gotchas** — update the module path in `go.mod` *and* imports. The rename also changes the evaluation API: `unleash.IsEnabled(name, unleash.WithContext(ctx))` no longer compiles — it becomes `unleash.IsEnabled(name, unleash.FeatureOptions{Ctx: ctx})` (variants take `unleash.VariantOptions`). Custom listeners (`WithListener`) carry over, but `RepositoryListener` gained a required `OnUpdate()` method — a legacy listener implementing only `OnReady()` silently fails the interface assertion, so readiness never fires (flags evaluate fine; health/ready reporting breaks): add a no-op `OnUpdate()`. The old trailing-slash trap on the API URL is gone — current majors normalize the URL either way.

## Go — OpenFeature provider

**Before**: community `go-sdk-contrib/providers/unleash` whose `ProviderConfig.Options` pass `unleash.WithInstanceId(...)` through to `unleash-client-go` v4.

**After** — same provider; swap only the wrapped options: replace `WithInstanceId` with `WithUrl($UNLEASH_URL)` + `WithCustomHeaders(Authorization)` as in Go-direct. `openfeature.SetProviderAndWait` and every `flags.BooleanValue` call site stay untouched.

**Gotchas** — the provider is alpha-grade: after upgrading it, re-verify the context mapping (targeting key → `UserId`) before trusting parity. Readiness race: the provider reports Ready without awaiting the wrapped client's first fetch, so one-shot/short-lived workers evaluate defaults — the before-state often masked this with a warm backup file keyed to the old shared appName, which the appName rename removes. Add a bounded ready-wait (e.g. via the client listener, ~10s, fail closed on timeout); a first sweep that returns all-defaults is this race, not a provisioning error.

## Ruby (`unleash` gem)

**Before**
```ruby
Unleash.configure do |config|
  config.url = ENV["GITLAB_UNLEASH_URL"]
  config.app_name = app_name          # GitLab environment name
  config.instance_id = instance_id
end
```
**After** — upgrade the gem to the current line and use header auth:
```ruby
Unleash.configure do |config|
  config.url = ENV["UNLEASH_URL"]
  config.app_name = "my-service"
  config.custom_http_headers = { "Authorization" => ENV["UNLEASH_CLIENT_TOKEN"] }
end
```
**Gotchas** — Rails DI wiring (initializer + service object, `config.x.feature_flags`) stays; only the `configure` block changes. Connectivity checks based on `Unleash.toggles.present?` break on the 6.x line — the accessor was removed when state moved into the Yggdrasil engine; use `Unleash.engine&.list_known_toggles.present?` for the same "definitions fetched" semantic.

## Java (`no.finn.unleash` → `io.getunleash`)

**Before** — `no.finn.unleash:unleash-client-java:4.4.1` (pre-rename pin):
```java
UnleashConfig.builder()
    .appName(appName).instanceId(instanceId).unleashAPI(url)
    .fetchTogglesInterval(15).sendMetricsInterval(60)
    .backupFile(tmpdir + "/unleash-backup-app-" + appName + ".json") // collision mitigation
    .build();
```
**After** — rename coordinates to `io.getunleash:unleash-client-java` (current release), imports from `no.finn.unleash.*` to `io.getunleash.*`, and:
```java
UnleashConfig.builder()
    .appName("my-service")
    .unleashAPI(System.getenv("UNLEASH_URL"))
    .apiKey(System.getenv("UNLEASH_CLIENT_TOKEN"))
    .fetchTogglesInterval(15).sendMetricsInterval(60)
    .build();
```
**Gotchas** — pick the newest `io.getunleash` release whose class-file target is ≤ the app's JDK (verify the artifact's bytecode major version, don't assume — recent releases have targeted Java 8 despite newer-JDK builds); framework upgrades stay out of scope. Keep the app's fail-fast config validation (required-env checks) with the renamed variables. Drop any explicit `.backupFile(...)` collision mitigation: it existed because GitLab forced appName = environment name, and unique appNames dissolve the shared `unleash-backup-<appName>.json` hazard. Clear stale backup files from tmp before verifying. The SDK rename does not require touching the framework (e.g. Spring Boot version) — keep framework upgrades out of scope.

## PHP (`unleash/client`)

**Before**
```php
UnleashBuilder::create()
    ->withAppName($appName)->withAppUrl($gitlabUrl)
    ->withInstanceId($instanceId)
    ->withMetricsEnabled(false)
    ->withBootstrap(['features' => []]);   // fail-closed when server is down
```
**After** — trap: the current PHP SDK (`unleash/client` 2.x) **hard-requires an instance ID whenever fetching is enabled** — `UnleashBuilder` without `withInstanceId()` throws `InvalidValueException` at runtime. Two sanctioned shapes; default to the first (keeps remnant greps clean):

```php
// construct the configuration manually — no instance-id requirement
$config = new UnleashConfiguration($url, $appName, /* instanceId */ $appName);
$config->setHeaders(['Authorization' => getenv('UNLEASH_CLIENT_TOKEN')])
    ->setMetricsEnabled(false)
    ->setBootstrapProvider(new JsonSerializableBootstrapProvider(['features' => []]));
$unleash = new DefaultUnleash(/* same strategy list the builder registers */, $config, …);
```

or keep the builder and bless `->withInstanceId('<app-name>')` as pure telemetry (Unleash ignores it for auth) — then document that exemption wherever the migration's remnant grep is defined, or it will flag it.

**Gotchas** — keep the empty bootstrap (it is the fail-closed mechanism — the PHP SDK fetches synchronously per request) and the metrics setting as found. Preserve `default` stickiness semantics on rollouts: anonymous traffic falls through userId → sessionId → random, and "fixing" it to userId-only changes behavior. When constructing manually, mirror the builder's defaults and verify them against the installed SDK version's source, not from memory: besides the full strategy-handler list, `DefaultUnleash` requires a `RegistrationService`, a `MetricsHandler` (which needs a `MetricsSender` even with metrics disabled), and a `VariantHandler`, plus explicit PSR-18/PSR-17 objects; the default cache discovery is `@internal`, so reconstruct the cache explicitly (e.g. `new Psr16Cache(new FilesystemAdapter('', 0, sys_get_temp_dir() . '/unleash-default-cache'))`).

## .NET (`Unleash.Client`)

**Before**
```csharp
new UnleashSettings {
    AppName = appName, InstanceTag = instanceId,
    UnleashApi = new Uri(url),
    FetchTogglesInterval = TimeSpan.FromSeconds(15),
}
```
**After**
```csharp
var settings = new UnleashSettings {
    AppName = "my-service",
    UnleashApi = new Uri(Environment.GetEnvironmentVariable("UNLEASH_URL")!),
    FetchTogglesInterval = TimeSpan.FromSeconds(15),
};
settings.CustomHttpHeaders.Add("Authorization",
    Environment.GetEnvironmentVariable("UNLEASH_CLIENT_TOKEN")!);
builder.Services.AddSingleton<IUnleash>(_ => new DefaultUnleash(settings));
```
**Gotchas** — `InstanceTag` is the .NET spelling of the instance-id trap; delete it. DI registration (`AddSingleton<IUnleash>`) stays. Health checks via `ListKnownToggles().Any()` keep working. The 5.x `DefaultUnleash(settings)` constructor carries a CS0618 obsoletion warning ahead of the v6 API change — if it pre-existed, keep the version (minimal diff) and note the v6 upgrade as follow-up; don't bundle it. The SDK's temp-dir toggle cache is not the Node/Java `unleash-backup-<appName>.json` file, but it is also appName-keyed — the rename gives a fresh cache namespace, so prove connectivity live rather than hunting cache files.

## Shell / REST ops scripts

**Before**: `curl` against the GitLab management API — `-H "PRIVATE-TOKEN: $GITLAB_API_TOKEN"` on `$GITLAB_API_URL/projects/$PROJECT_ID/feature_flags[...]`, flags created with `version: "new_version_flag"`, global on/off via `PUT {"active": bool}`, user-list edits via `feature_flags_user_lists/:iid`.

**After** — rewrite against the Unleash Admin API (recipes and idempotency rules in [provisioning.md](provisioning.md)), preserving each script's CLI contract:

| Old operation | New call |
|---|---|
| list flags | `GET /api/admin/projects/<project>/features` |
| create flag (+ default strategy) | `POST …/features`, then `POST …/environments/<env>/strategies` |
| delete flag | `DELETE …/features/<flag>` (then purge from archive if hard delete is wanted) |
| toggle `active` bit | `POST …/environments/<env>/on\|off` — **per environment**; decide and document which environment(s) the script targets, a global bit no longer exists |
| set rollout % | `GET …/environments/<env>/strategies`, find the rollout strategy, `PUT …/strategies/<id>` with updated `parameters.rollout` |
| add user to list | `GET /api/admin/segments` → find segment by name → `PUT /api/admin/segments/<id>` with the extended constraint values |

**Gotchas** — auth header becomes `Authorization: $UNLEASH_ADMIN_TOKEN`; drop the `version: "new_version_flag"` relic; `parameters` values stay strings when PUT-ing strategies; keep list-edit scripts idempotent (skip if the value is already present).

## Related

- For the instance-id trap table and the before-state model: `gitlab-flags-primer.md`
- For token provisioning (least privilege): `provisioning.md`
- For proving the rewrite preserved behavior: `verification.md`
