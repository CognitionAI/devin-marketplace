---
name: hex-notebook-authoring
description: Use when the user wants to create, inspect, edit, run, stage, publish, or repair CLI access for a Hex notebook or project through a local-first Hex CLI workflow.
---

# Hex Notebook Authoring

Use this skill for local-first Hex notebook and project authoring. This includes creating notebooks, editing cells, staging local changes, pushing changes back to Hex, running notebooks, reviewing notebook/project state from the command line, and repairing Hex CLI installation or auth when it blocks the workflow.

Do not use this skill for pure discovery or business-question answering unless the user explicitly wants to modify a Hex project. Use `hex-business-analytics-question` for analytics Q&A.

## Workflow

1. Clarify the target project only when the user has not provided enough context to identify it.
2. Check that the Hex CLI works before relying on it:
   - Run `command -v hex` or `hex --version`.
   - Run `hex auth status --json --no-color` when auth state matters.
   - If the CLI is missing, unauthenticated, or pointed at the wrong workspace/profile, use the CLI setup recovery steps below, then retry the intended command.
3. Install and read the CLI-provided Cursor skill before choosing exact commands:
   - Prefer `hex install agent-skill --cursor --global`, then read `~/.cursor/skills/hex/SKILL.md`.
   - Use `hex install agent-skill --cursor`, then read `.cursor/skills/hex/SKILL.md`, only when a workspace-local skill is preferred.
4. Inspect the current project state before editing. Prefer JSON and no-color output where supported.
5. Make the smallest local change that satisfies the request. Preserve existing notebook structure, cell order, naming, and data connection choices unless the user asks to change them.
6. Validate the notebook/project after edits using the CLI-provided workflow. Run only the minimum necessary project or cell execution to verify the change unless the user asks for a full run.
7. Show the user what changed, any run results or validation output, and whether anything still needs to be published or reviewed in Hex.

## Authoring Rules

- Treat the CLI-installed skill as the source of truth for command names, flags, file formats, and safety guidance.
- Keep SQL, Python, markdown, and chart edits in the idioms already used by the project.
- Do not invent data connection IDs, project IDs, cell IDs, or schema names. Discover them from Hex or ask the user.
- Do not publish destructive changes, delete cells, or overwrite shared project content unless the user explicitly requested that action.
- Do not expose secrets, tokens, connection strings, or private query results in summaries.

## CLI Setup Recovery

Use these steps only when CLI installation, auth, workspace, or profile state blocks the authoring workflow.

1. Detect the blocker:
   - Check installation with `command -v hex` or `hex --version`.
   - Check auth with `hex auth status --json --no-color` if `hex` is installed.
   - Check profile/workspace when an error suggests the wrong account, workspace, or permissions.
2. Install the CLI only if it is missing:
   - Prefer the shell installer: `curl -fsSL https://hex.tech/install.sh | bash`.
   - Homebrew is also supported: `brew install hex-inc/hex-cli/hex`.
   - Request command approval when sandbox policy requires it.
3. Verify installation with `hex --version`.
4. Authenticate only if auth is missing or the selected workspace/profile is wrong:
   - Run `hex auth login` for the default Hex workspace flow.
   - For custom or regional Hex URLs, run `hex auth login -H <hex-base-url>` after asking the user for the correct URL if it is not known.
   - Explain that Hex CLI auth is separate from the Hex app/MCP connection.
   - Wait for the user to complete browser or device login, then retry `hex auth status --json --no-color`.
5. If the user has multiple profiles, use `hex auth switch <profile_name>` only after confirming the intended profile.
6. Retry the original Hex CLI command that failed once setup is complete.

## Setup Safety Rules

- Do not ask the user for raw API tokens unless they explicitly request a CI/non-interactive setup.
- Do not print tokens, credentials, keychain paths, or auth artifacts.
- Do not assume Hex app/MCP auth means CLI auth is configured.
- Do not reinstall the CLI if `hex --version` works.
- Do not switch profiles or workspaces without confirming the intended target when multiple options are present.

## References

- Hex CLI repository: `https://github.com/hex-inc/hex-cli`
- Hex CLI docs: `https://learn.hex.tech/docs/api-integrations/cli`

## Common Triggers

- "Edit this Hex notebook locally."
- "Add a cell to a Hex project."
- "Run this Hex project from Cursor."
- "Stage and push my Hex notebook changes."
- "Use the Hex CLI to update a dashboard/notebook."
- `hex: command not found`
- `command not found: hex`
- Hex CLI auth status reports unauthenticated.
- A Hex CLI command fails because there is no active workspace/profile.
