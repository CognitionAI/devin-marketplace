---
name: asana-usage
description: Best practices for using Asana MCP tools in Cursor. Use when working with tasks, projects, or portfolios.
---

# Asana Usage Best Practices

## Before using Asana tools

Always verify the MCP connection is active. If tools are unavailable, run the `asana-setup` skill first.

## Working with tasks

- When creating tasks, always confirm the target project with the user before creating
- When searching, prefer specific project or section filters over broad workspace searches
- Always show the user a summary of what will be created or modified before taking action
- For bulk operations (creating multiple tasks), list them all first and ask for confirmation

## Working with projects

- Never delete a project without explicit user confirmation
- When duplicating a project, confirm the new name before proceeding
- Section names matter — confirm with the user before moving tasks between sections

## Handling ambiguity

- If the user references "my project" or "the team" without being specific, ask which project they mean before taking action
- If multiple workspaces exist, ask the user which one to use before searching or creating

## Error handling

- If an MCP tool call fails with an auth error, run the `asana-setup` skill
- If a task or project GID is not found, do not guess — ask the user to verify the resource exists
- Rate limit errors: wait 10 seconds and retry once before reporting the error to the user
