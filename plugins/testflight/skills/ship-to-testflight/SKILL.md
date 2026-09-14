---
name: ship-to-testflight
description: Archive an iOS/macOS app, upload it to TestFlight, and hand back a public tester link. Use when asked to ship a build to TestFlight, cut a beta, send a build to testers, or produce a TestFlight link.
---

Ship a build of an Apple app to TestFlight and return a link a human can tap.

This runs only on a macOS machine with Xcode installed (a macOS Devin machine,
or your own Mac through the CLI). Authentication comes from the App Store
Connect API key supplied when this plugin was installed, reachable through the
`testflight` MCP server — never ask the user to paste a key into the session,
and never print key contents.

## 1. Check the ground

- `xcodebuild -version` — Xcode must be present.
- Find the workspace/project and the scheme you are shipping
  (`xcodebuild -list`), and the bundle id of that scheme's Release build.
- `list_apps` confirms the key can see that bundle id. An empty result means
  the key belongs to a different team or lacks App Manager rights — say so
  instead of guessing another bundle id.

If the repo already has a release script or Makefile target (`make testflight`,
`fastlane pilot`, `scripts/testflight.sh`), use it and pass it the credentials
from step 2 rather than writing new build commands.

## 2. Get the credentials onto disk

Call `prepare_signing_key`. It writes the `.p8` key as a mode-0600 file and
returns `key_id`, `issuer_id`, `key_path`, and the matching
`xcodebuild_args`. Everything below uses those; `fastlane` equivalents are
`--api_key_path` / `APP_STORE_CONNECT_API_KEY_*`, and `xcrun altool` takes
`--apiKey <key_id> --apiIssuer <issuer_id>` with the file in
`~/.appstoreconnect/private_keys/`.

## 3. Pick a build number

TestFlight rejects a build number it has already seen for that version. Read
the last one with `list_builds` and go above it; a UTC timestamp
(`date -u +%Y%m%d%H%M`) is a safe default when the project has no scheme of
its own. Pass it as `CURRENT_PROJECT_VERSION` so you do not have to commit a
change to ship.

## 4. Archive and upload

```bash
xcodebuild -workspace <App>.xcworkspace -scheme <Scheme> \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath build/<Scheme>-<build-number>.xcarchive \
  CODE_SIGNING_ALLOWED=NO CURRENT_PROJECT_VERSION=<build-number> archive

xcodebuild -exportArchive -archivePath build/<Scheme>-<build-number>.xcarchive \
  -exportOptionsPlist ExportOptions.plist <xcodebuild_args from step 2>
```

Archive unsigned and sign during export, with `destination: upload` in the
export options plist, so one export both signs and uploads:

```xml
<dict>
  <key>method</key><string>app-store-connect</string>
  <key>destination</key><string>upload</string>
  <key>teamID</key><string>YOUR_TEAM_ID</string>
  <key>signingStyle</key><string>automatic</string>
</dict>
```

`-allowProvisioningUpdates` (included in `xcodebuild_args`) lets Xcode mint the
distribution certificate and profile from the API key, so a machine with no
signing assets can still ship. Signing failures are almost always a missing
team id or a key without App Manager rights — report the xcodebuild error
rather than disabling signing checks.

## 5. Publish the build

Uploading only puts the build in App Store Connect; it reaches testers once it
has processed and joined a group.

1. `wait_for_build` with the bundle id and build number. Processing usually
   takes 5–20 minutes.
2. `set_whats_new` with a short, concrete note — what changed in this build,
   not the release process.
3. `list_beta_groups`, then `add_build_to_group`. External groups are
   submitted for beta app review automatically; review is typically hours, and
   the build is not installable until it passes.
4. `testflight_public_link` returns the tap-to-install link. Pass
   `enable: true` only when the group has no public link yet and the user
   wants one — it makes the build installable by anyone with the URL.

## 6. Report back

Give the user the public link, the build number, the group it went to, and —
for an external group — that beta review is pending. Attach nothing else: the
link is the deliverable.

## Failure notes

- "No profiles for '<bundle id>' were found" — the key's team does not own that
  bundle id, or the app record does not exist yet in App Store Connect.
- "The provided entity includes an attribute with a value that has already been
  used" on upload — the build number is taken; pick a higher one.
- A build stuck in `PROCESSING` past `wait_minutes` is Apple-side; report it
  with the build number rather than re-uploading.
- `ASC_*` missing means the plugin was installed without credentials —
  reinstall it from Settings and supply the Issuer ID, Key ID, and `.p8`
  contents.
