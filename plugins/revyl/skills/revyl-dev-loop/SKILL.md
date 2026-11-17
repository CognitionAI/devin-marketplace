---
name: revyl-dev-loop
description: Run, preview, debug and verify mobile app changes on a Revyl cloud iOS or Android device with the Revyl CLI. Use after changing iOS, Android, Expo, React Native, Flutter or other mobile app code, before reporting the work done, to offer an on-device check; also use when asked to run, preview or screenshot the app on a device.
---

# Revyl dev loop

Run the app the user is working on, from its current source, on a Revyl cloud
device, and check the change there. Devin's machine has no iOS or Android
simulator, so the device is Revyl's and the viewer link is how the user
watches it.

Installing this plugin changes nothing in the app. Change app source or
`.revyl/config.yaml` only when the task requires it and the user agrees.

## Revyl CLI

Run every Revyl command from the app directory, the one holding
`.revyl/config.yaml`, never from the plugin's folder: the CLI reads the current
directory's Git branch, commit and config, so a command run elsewhere resolves
the wrong project or build. In the shell you use for Revyl, run
`export REVYL_AGENT=devin` once so Revyl attributes the commands to Devin.

If `revyl --version` fails and this task needs the CLI, install Revyl's
official CLI and put it on `PATH`:

```sh
curl -fsSL https://revyl.com/install.sh | sh
export PATH="$HOME/.revyl/bin:$PATH"
```

Check sign-in with `revyl auth status --json`. When `REVYL_API_KEY` is in the
environment (a Devin secret), the CLI already uses it: never print it, pass it
as an argument, or write it to a file. Otherwise run `revyl auth login` in its
own shell. It prints an approval URL and a short code, then waits. Give the
user that URL as a link and wait for them to approve it. Never approve a Revyl
sign-in yourself in Devin's browser, and never ask for a password, code or key
in chat.

Give the user every sign-in, viewer and report URL as a link as soon as you
have it, and never claim that anyone has seen a device.

## Hosted Revyl tools

This plugin's `revyl` MCP server is Revyl's hosted workspace. Its tools find
apps and builds, start, act on, screenshot and stop device sessions, and read
Atlas. It signs in with Revyl's OAuth page, separately from the CLI: in Devin
Cloud, connect it from **Customize → MCPs**; in the Devin CLI, use
`devin mcp login`. Mention signing in only when the user wants something those
tools do; every step below also has a CLI command. Check which tools are
actually available before naming one.

The hosted tools can act on a session the CLI started, by its returned
`session_id`. If they can't see it, the two sign-ins point at different
accounts or organizations: say so, and never start another device to work
around it.

## Offer a device check before calling mobile work done

When this task changed mobile app code (screens, components, navigation,
styles, native modules or app configuration) and you are about to report it
done, offer once to check it on a Revyl device. Name the app directory and the
platform, and say it uses the organization's device time, for example: "Want me
to check this on a Revyl iOS cloud device before I wrap up? It uses your org's
device time."

Start nothing that uses device or build time until the user says yes. If they
decline, finish without the check and don't ask again for the same change. Skip
the offer when the change can't affect the running app, such as docs, tests or
CI configuration only.

## Authorization and selection

A build, a device session and a dev loop each use the organization's build
minutes or device time. Start one only after the user authorizes it, naming the
app, platform and what it will run; a yes to the offer above counts. Resolve
the exact build profile and platform from `.revyl/config.yaml`, the repository
and the task without changing them, and ask only when they stay ambiguous.

If the CLI reports a legacy configuration format, run
`revyl config migrate --check --json` and summarize the fields it would drop.
Migrating rewrites `.revyl/config.yaml` (keeping a backup), so ask before
`revyl config migrate --write`, and never hand-edit the file to get past the
error.

## Start the loop

Start it detached, with explicit selection, and without opening a browser.
Pick the mode from the app's stack:

- **Native or rebuild-first** apps (Swift, Kotlin, Flutter, KMP, Bazel, or any
  profile without a dev server) build on a Revyl runner:

  ```sh
  revyl dev --profile <profile> --platform <ios-or-android> --remote --detach --json --no-open
  ```

- **Expo and React Native** profiles whose development client loads JavaScript
  from Metro use the hot-reload loop. Omit `--remote`: the remote loop skips
  Metro and its relay, so such a client can't load the app.

  ```sh
  revyl dev --profile <profile> --platform <ios-or-android> --detach --json --no-open
  ```

Give the user the handshake's `viewer_url` at once, and record its context and
`session_id`. A viewer only means the session exists, not that the current
build succeeded: wait for the build to reach its terminal success state before
claiming a build result.

Never call the hosted `start_device_session` for a session the CLI already
created, and never start a second device for it. The hosted `screenshot` tool
with that `session_id` returns the current screen as an image.

## Iterate and check

Use short commands, each in its own call, and target the returned context:

```sh
revyl dev status --context <context>
revyl dev rebuild --context <context> --wait --timeout 600 --json
revyl device instruction "<one plain-language step>" --session-id <session-id> --json
revyl device validation "<one statement about the screen>" --session-id <session-id> --json
revyl device screenshot --session-id <session-id> --out <file>.png --json
```

Rebuild after native changes; JavaScript changes reach a hot-reload loop on
their own. Target every device command at the returned session. Open each
screenshot before describing it. A false or missing validation verdict is a
failed check. Bound every wait by the build timeout; when it passes, report a
timeout and stop the loop instead of polling on.

## Clean up

When the work ends or fails, stop only what this task started:

```sh
revyl dev stop <context> --json
```

A stop is done only when its JSON says the session stopped. Otherwise, while
`revyl device list --json` still lists it, wait about ten seconds and stop it
once more with `revyl device stop --session-id <session-id> --json`. Never use
`--all`.

## Report

Say what ran (app, platform, build), each validation verdict, and attach only
screenshots you took and opened. Commit `.revyl/config.yaml` and
`.revyl/tests/` only, never screenshots, reports or logs. If Revyl itself got
in the way, describe the problem in your report.

Docs: https://docs.revyl.com/dev-loop
