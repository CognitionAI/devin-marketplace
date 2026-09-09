---
name: setup-metabase-mcp
description: Read these instructions before using Metabase MCP tools. Setup is needed to connect to Metabase instances via the built-in MCP server.
---

Read these mandatory configuration steps for using the Metabase MCP server before querying data, dashboards, questions, and related resources.

**Location**: The MCP configuration file is `../../mcp.json` relative to this SKILL.md file — two directories up, in the same folder that contains the `skills/` directory. Always resolve this path relative to this SKILL.md file, never relative to the user's open project.

**Important Requirement**: The `url` field in that file may contain `{METABASE_INSTANCE_PLACEHOLDER}` as the base URL (e.g. `"{METABASE_INSTANCE_PLACEHOLDER}/api/mcp"`). If so, it must be replaced with the user's actual Metabase instance URL before the MCP can work.

## Valid Instance URL Formats

- Local development: `http://localhost:3000`
- Metabase Cloud: `https://yourcompany.metabaseapp.com`
- Self-hosted: `https://metabase.yourcompany.com`

## Required Actions

1. Read `../../mcp.json` relative to this SKILL.md file.

2. Check whether the `url` field contains `{METABASE_INSTANCE_PLACEHOLDER}`.
   - **If it does NOT contain `{METABASE_INSTANCE_PLACEHOLDER}`**: the MCP is already configured. **Immediately proceed with using the Metabase MCP. Do not ask the user for a URL under any circumstances.**
   - **If it does contain `{METABASE_INSTANCE_PLACEHOLDER}`**: continue with the steps below.

3. **Stop all other exploration immediately** and ask the user for their Metabase instance URL. Do not search for tool schemas, read other files, or do anything else first.

   **Never mention `{METABASE_INSTANCE_PLACEHOLDER}` or any placeholder to the user**. Simply say the MCP needs their Metabase URL to connect.

   Ask the user: "Do you have a Metabase instance URL, or would you like to set up a local instance?"
   - **If they provide a URL**: Continue with step 4.
   - **If they don't have one and want to set up a local instance**: Invoke the `setup-metabase-instance` skill. Once the local instance is running, return here and use `http://localhost:3000` (or whatever port was chosen) as the instance URL.

4. Once the user provides the URL, run **exactly this command and no other** — do not try alternative endpoints or approaches:

   ```bash
   curl -s <INSTANCE_URL>/api/session/properties | grep -o '"tag":"[^"]*"'
   ```

   This returns something like `"tag":"v1.60.0"`. Extract the major version number (e.g. `60` from `v1.60.0`). If it is below 60, tell the user they need to upgrade and stop — do not update `mcp.json`.

5. Replace the placeholder in `../../mcp.json` relative to this SKILL.md with the user's instance URL. Strip any trailing slash before saving — do not mention this to the user.

6. Only after updating the file, tell the user they need to reload the window.

   Use the user's current OS to show the right shortcut: open the Command Palette (⌘⇧P on Mac or Ctrl+Shift+P on Windows/Linux) and run **"Reload Window"**. Ask them to confirm once reloaded before continuing.

7. Once the user confirms the window has been reloaded, call the `mcp_auth` tool for the Metabase MCP server to authenticate. This will prompt the user to log in to their Metabase instance.

8. Proceed with using the Metabase MCP

**Important**: Do not attempt to access MCP tools or schemas until the authentication is complete. Never reveal `{METABASE_INSTANCE_PLACEHOLDER}` or any internal placeholder names to the user.
