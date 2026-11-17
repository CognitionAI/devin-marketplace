---
name: headless
description: Revyl conventions for Devin sessions nobody is watching live, such as scheduled, API-started or Slack-started sessions and CI jobs. Covers CLI sign-in with REVYL_API_KEY, finding or making builds without Xcode, bounded waits, device evidence and always stopping sessions. Use whenever Devin works with Revyl without a user who can answer in time.
---

# Revyl in unattended sessions

Use this skill when nobody is following the session: a scheduled Devin
session, one started from the API or Slack and left to run, or a CI job. The
CLI works the same there, but nobody can answer a question, approve a sign-in
or watch a device, and devices keep running after the session ends.

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

## Authorization comes from the task

An unattended session can't ask before spending. Start a device or a build only
when the task itself authorizes it, for example "prove this pull request on an
iOS device". Otherwise do the free parts (resolve the app, find builds, check
the config) and report what you would run and what it would use.

## Sign-in

- The CLI needs `REVYL_API_KEY` as a Devin secret here. Check with
  `revyl auth status --json`.
- Without it, `revyl auth login` would print an approval link that nobody will
  open. Report that the session needs a `REVYL_API_KEY` secret and stop.
- The hosted `revyl` tools use the OAuth connection made in Devin. When it
  isn't connected, use the CLI for every step rather than asking for a
  sign-in.

## Builds

- Look for an existing build of the exact commit first, as the `/revyl:proof`
  skill describes: a pull-request preview or a CI upload costs nothing.
- Devin's Linux machine has no Xcode, so iOS builds run on Revyl's runners:
  `revyl build --profile <profile> --platform ios --detach --json`, then
  `revyl build status <build-job-id> --json` until it finishes. Treat Android
  the same unless this machine has the Android SDK.
- For a development loop of a native or standalone build, use
  `revyl dev --remote --detach --json --no-open`. Expo and React Native
  development clients load JavaScript through Metro, which `--remote` doesn't
  start: use `revyl dev --detach --json --no-open` for them. Never start the
  interactive `revyl dev` interface.

## Bounded waits

Every wait has a limit. Use `revyl dev status` for snapshots,
`revyl dev rebuild --wait --timeout <seconds> --json` after native changes, and
`revyl build status` polls with a deadline. When a deadline passes, report
where things stand instead of waiting longer.

## Sessions outlive the run

- Before starting a device, `revyl dev list` and `revyl device list --json`
  show sessions this run may reuse. Don't stack a new device on a stale one.
- Record each `session_id` you start. Before the session ends, on success or
  failure, stop exactly those: `revyl dev stop <context> --json` or
  `revyl device stop --session-id <id> --json`. Never `--all`.
- A stop is finished only when its JSON says the session stopped. Otherwise,
  while `revyl device list --json` still lists it, wait about ten seconds and
  stop it once more, then record whether it ended.

## Evidence

- Report `viewer_url` as soon as `--json` output returns it.
- `revyl device screenshot --session-id <id> --out <file>.png --json` and
  `revyl device report --session-id <id> --json` are the evidence. Put their
  results, not claims, in the summary or pull-request comment.

## Launch variables and secrets

Selected launch configurations apply to new sessions on their own; don't fetch
or repeat their values. If the app shows a signed-out state mid-session,
`revyl dev auth refresh --json` re-sends the sign-in; if the token itself
expired, stop the session and start a new one. Never put tokens, launch
variable values or API keys in code, logs, screenshots or pull requests.

## Repository hygiene

Commit `.revyl/config.yaml` and `.revyl/tests/` only. Confirm
`.revyl/.gitignore` exists before committing, and never commit screenshots,
reports, logs or launch-variable files the run produced.
