---
name: revyl-workspace
description: Use Revyl's hosted tools to find an app and its builds, follow the build a pull request produced, start, act on, screenshot and stop a device or browser session, explore an app, or answer from its Atlas screen map, for work the user asked for.
---

# Revyl workspace

Use this plugin's hosted `revyl` MCP tools. Check which tools are actually
available; never invent one. If the connection is missing or expired, ask the
user to connect Revyl (in Devin Cloud, **Customize → MCPs**; in the Devin CLI,
`devin mcp login`). Never ask for API keys, passwords or login codes in chat.
These tools don't build, upload or run a dev loop; for that, use the
`revyl-dev-loop` skill and the Revyl CLI.

## Find the app

Call `list_apps` to resolve an app the user names to its `app_id`, filtering
with `platform` or `search` when the list is long. If several match, ask which
one; never guess an ID.

## Answer from Atlas

`atlas_graph` summarizes an app's screens and flows, and `atlas_search` finds
screens by name or description. Both start nothing. Use them to answer how the
app works before starting a device, and link the `atlas_url` they return.
`open_revyl_workspace` with `view="atlas"` and the `app_id` returns a
`workspace_url`; give it to the user as a link, since Devin doesn't show
Revyl's embedded views.

## Follow a pull request's build

Revyl builds a pull request after each push when its project has pull-request
builds set up.

1. Call `list_builds` with the `app_id` and the pull request's head branch.
   Each build says its `status`, commit, `pr_number` and `source`.
2. Follow an unfinished build with `get_build` and `wait_seconds` (at most 45)
   while it is `queued` or `running`, and tell the user it is still building
   rather than waiting silently. Pass on a failed build's `failure_reason`.
3. When `ready_for_device_session` is true and the user asked for a session,
   start it with that build's `build_id`.

When nothing is found, relay the next steps the tool's message gives. When a
message says the organization has no GitHub connection, offer to connect it,
and call `connect_github` only after the user agrees. It returns a single-use
`install_url` for the user to open themselves; don't share it anywhere else.

## Start a session only when asked

A session uses the organization's device time. Call `start_device_session`
only when the user asks, with an explicit `platform`: `ios` or `android` with
`app_id` or `build_id`, `web` with `app_id`, or `macos` for a bare cloud Mac
computer (give the user its `computer_url`; Computers must be enabled for the
organization). Record the `session_id`, give the user `viewer_url` as a link,
and check `list_device_sessions` before considering another start.

## Act on and check a session

`device_instruction` carries out one plain-language step and
`device_validation` checks one statement against the screen, one per call,
with the `session_id`. A `running` result carries a `step_id`: wait with
`get_device_step` instead of resending. Treat `passed=false` or a missing
`passed` as not done. Use `screenshot` to see the screen, and look at the
image before describing it.

## Explore an app only when asked

`start_exploration` sends explorer agents through an app, each on its own
cloud device for several minutes, and adds what they find to Atlas. Start one
only when the user asks, with one explorer unless they ask for more (at most
three), and pass `focus` when they name an area. Check it with
`get_exploration`, and cancel with `cancel_exploration` only when asked.

## Clean up

When the work is done, stop only the sessions you started with
`stop_device_session`. If the result says `stopped: false`, call it once more,
then report whether the session ended. Don't create, change or share tests,
builds or workflows from this skill, and keep signed URLs, credentials and
customer content out of public artifacts.

Docs: https://docs.revyl.com/agents/mcp
