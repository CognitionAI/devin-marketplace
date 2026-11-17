---
name: revyl-proof
description: Prove a pull request on a Revyl cloud device using the build of its exact head commit, from Revyl's GitHub App preview build or a CI upload, without rebuilding, and draft the proof for the pull request. Use when asked to prove, verify or test a pull request on a device.
argument-hint: "[pull request number or URL] [ios|android|web]"
---

# Revyl proof

Prove a pull request with a build of its exact head commit and draft the
evidence. This skill never builds or uploads: the proof is about the artifact
the pull request produced. To check unpushed work, use `revyl-dev-loop`.

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

## Resolve (free, read-only)

- The pull request: the one the user named, otherwise the current branch's. Get
  its head branch and **full** 40-character head SHA, for example with
  `gh pr view <pr> --json number,headRefName,headRefOid,files` or
  `git rev-parse`. A short SHA, branch name or version label never matches.
- The app and platform from the changed files and the nearest
  `.revyl/config.yaml` (its `app_id`), or `revyl app list --platform <platform> --json`.
  Ask only when ambiguous.

## Find the build of the head commit (free)

1. **Preview build, hosted tools.** Call `list_builds` with the app's `app_id`
   and the head branch, and take the build whose `commit_sha` equals the head
   SHA. Trust that match when its `source` is `pull_request` or
   `remote_build`. Follow a `queued` or `running` build with `get_build`
   (`wait_seconds` 45) for up to 20 minutes or the user's limit, telling the user
   every few minutes that it is still building. A `failed` build: report its
   `failure_reason` and stop.
2. **CLI.** When the hosted tools are missing or not signed in, or for a CI
   upload, read builds a page at a time, newest first:

   ```sh
   revyl build list --app <app-id> --branch <head-branch> --limit 100 --page 1 --json
   ```

   A build's commit is in `metadata.scm_head_sha`, `metadata.commit_sha`,
   `metadata.source_metadata.commit_sha` or `metadata.git.commit`. Skip any
   build whose `metadata.git.dirty` is true. Follow `has_next` for at most five
   pages, then repeat without `--branch` (every branch, five pages), since a CI
   upload can record another branch name such as `HEAD`. If that search still
   has more pages, report **proof not run: build lookup incomplete**.

No build of the head SHA means **proof not run**: say which lookups ran, and
that pull-request builds or a CI upload step would produce one. Never fall back
to another commit's build, and never start a build.

## Confirm once, then prove

Ask once, naming the pull request, app, platform and build, and that it uses
the organization's device time. After the user agrees:

1. Start a session on that exact build: hosted `start_device_session` with
   `platform` and `build_id` (plus `app_id` for web), or
   `revyl device start --build-version-id <build-id> --json`. Record its
   `session_id` and give the user `viewer_url` at once.
2. Exercise only the changed behavior, one step per call: hosted
   `device_instruction` and `device_validation` (wait on a `running` result's
   `step_id` with `get_device_step` instead of resending), or
   `revyl device instruction` and `revyl device validation` with
   `--session-id`. A false or missing `passed` is a failed check.
3. Capture screenshots (hosted `screenshot`, or
   `revyl device screenshot --session-id <id> --out <file>.png --json`) and
   look at each one before describing it.
4. Stop the session even when a check fails: hosted `stop_device_session`, or
   `revyl device stop --session-id <id> --json`. When it doesn't confirm the
   stop, wait about ten seconds and stop it once more, then report whether it
   ended. Never stop sessions you didn't start.

`revyl device report --session-id <id> --json` returns the session's step
results for the draft.

## Draft and publish

Return a draft headed `## Revyl device proof` with the full SHA, the build ID
and where it came from, each validation verdict, and only evidence you
collected. Posting it to the pull request, `revyl session share` and
`revyl session publish` are separate external actions: ask first and name the
audience. Never include credentials, launch-variable values or signed URLs.

When the project has Revyl's Proof of Changes on, the Revyl GitHub App also
posts its own proof on each push, and a reviewer reruns it by commenting
`@revyl rerun [ios|android|web] [guidance]` on the pull request. Suggest that
comment rather than posting it.
