---
trigger: always_on
---

# Using Claude Code as a subagent

## When to delegate

The user installed this plugin so that Claude Code does their coding work. Hand coding tasks to it by default, without asking first: you scope the task, Claude Code does it, and you check the result.

- Implementation, bug fixes, refactors, and test writing that take more than a couple of edits.
- Investigating or explaining code you haven't read yet.
- A second opinion on a plan or a change.
- Work that can run in parallel with what you are doing.

Do the work yourself only when handing it off would cost more than doing it: an edit you can finish in a command or two, non-coding tasks, and anything that depends on context or tools only you have.

The tools are on the `claude-code` MCP server. Depending on the session they are either individual tools named `mcp__claude-code__<tool>` (load `mcp__claude-code__run_claude_code` with tool search) or reached through `mcp_call_tool` with server `claude-code` (list them once with `mcp_list_tools`). If the server isn't connected yet, call `mcp_list_tools` for `claude-code` again after a few seconds; don't look for the tools any other way.

## Writing the prompt

Claude Code cannot see this conversation. Include the goal, the relevant files, constraints, how to verify the work, and what to report back. Set `cwd` to the absolute path of the repository or directory it should work in.

## Choosing a model

- Use the model the user named. Pass an alias or a full model name in `model`.
- If the user did not name one, omit `model` for typical coding so Claude Code uses the account's default.
- Set `model` when the task clearly calls for it: `haiku` for small mechanical edits, `opus` for hard debugging or design work, and `fable` for the hardest, longest-running tasks if the account has it.
- When a model is rejected or unavailable on the account, tell the user which one failed before trying another. Do not switch models silently.

## Limiting what it can do

- By default Claude Code runs with its permission checks off (`bypassPermissions`), because Devin's machine is already a sandbox: it can edit files and run any command the task needs, including tests in one compound command. Leave `permission_mode` and `allowed_tools` unset for ordinary coding work.
- It can do anything you can do on this machine, so the prompt is the limit. Say what it must not touch (pushing, deploying, other repositories, credentials), and do not delegate a task you would not run yourself.
- Use `plan` for read-only analysis. To restrict a run further, set `permission_mode` to `acceptEdits`: edits are allowed, and any other tool that would ask for permission is denied unless `allowed_tools` allows it, such as `Bash(npm test:*)`.
- In those narrower modes Claude Code checks every part of a command joined with `;`, `&&`, `||` or `|` against the rules, and one unmatched part denies the whole command. Give each command the task runs its own rule, for example `Bash(python3 -m unittest:*)` and `Bash(python3 fib.py:*)`. `Bash(echo:*)` is added for you when you allow a Bash command outside `plan` mode, so `npm test; echo "exit=$?"` runs in one command. No rule allows `$(...)`, `${...}`, or `cd` outside `cwd`.
- If `permission_denials` lists a tool the task needs, `denied_commands` shows the Bash commands that were refused. Resume the session with a specific rule for it, or without `permission_mode`.
- Set `max_turns` or `max_budget_usd` for open-ended work. `max_budget_usd` limits estimated spend.

## Long-running jobs

- A `running` status with a `job_id` means the work is still going. Poll with `get_claude_code_job`; do not start the same task again.
- Stop a job you no longer need with `cancel_claude_code_job`.
- Jobs end when the MCP server process ends. If a job is unknown, continue it by passing its `session_id` as `resume_session_id`.
- Use `resume_session_id` for follow-ups on the same task, rather than a new run that has to rebuild the context.
- Do not edit files in `cwd` while a job is running there, and do not run two jobs that edit the same checkout at once.

## Checking the result

Treat the result as a report, not as proof. Read the diff and run the relevant checks yourself before telling the user the work is done.

## Talking to the user

Report the work and its outcome, not the mechanics of delegating it.

- Say "Claude Code is fixing the failing test", not that you are calling a tool, starting a job, or polling.
- Do not mention tool names, job IDs, session IDs, wait times, CLI flags, permission modes, or how Claude Code was installed or launched.
- Do not narrate checks that passed, such as authentication or setup.
- Give cost, model, or technical details only when the user asks, or when they change a decision the user has to make.
- When something needs the user, such as a failed login or a denied tool, say what they need to do in plain words.

## Authentication

- If a run fails on authentication and the user asked for Claude Code, call `claude_code_auth_status` and give them the returned `setup_help`.
- If you chose to delegate on your own, do the work yourself and tell the user once, briefly, that Claude Code isn't connected.
- Never ask the user to paste a token or API key into chat. Credentials go in the plugin's connection in Customize > Plugins.
- Never print, log, or read Claude Code's token, API key, or credential files.
