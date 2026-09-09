---
name: asana-mcp-troubleshooting
description: Diagnose and fix Asana MCP connection issues. Run when the user reports Asana tools are not working, the connection is failing, or they are stuck during setup.
---

# Asana MCP Troubleshooting

## When to use this skill

Use this skill when:
- The user says Asana tools are not available or not showing up in Cursor
- The user reports an authentication error when using Asana tools
- The user says "I'm stuck" or "it's not working" after installing the plugin
- Any Asana MCP tool call fails with a connection or auth error

## Diagnosis flow

Work through these checks in order. Stop at the first one that fails and resolve it before continuing.

### Check 1: Are the environment variables set?

Run:

```bash
echo "CLIENT_ID: $ASANA_CLIENT_ID"
echo "CLIENT_SECRET: $ASANA_CLIENT_SECRET"
```

If either prints empty or the literal string `$ASANA_CLIENT_ID`: The env vars are not set. This is the most common cause of failure.

Tell the user:

> The Asana plugin needs two environment variables to authenticate. You'll need to create an Asana OAuth app to get them.

**Step 1: Create an Asana OAuth app**

1. Go to https://app.asana.com/0/my-apps
2. Click **Create new app** and select "MCP App" as the app type
3. Name it anything (e.g. "Cursor MCP")
4. Under **OAuth**, add this exact redirect URI: `cursor://anysphere.cursor-mcp/oauth/callback`
5. Copy your **Client ID** and **Client Secret**

**Step 2: Set environment variables**

Add these lines to your shell profile and save the file:
- macOS/zsh → `~/.zshrc`
- Linux/bash → `~/.bashrc`
- Windows WSL → `~/.bashrc`

```bash
export ASANA_CLIENT_ID="paste_your_client_id_here"
export ASANA_CLIENT_SECRET="paste_your_client_secret_here"
```

**Step 3: Apply and restart**

```bash
source ~/.zshrc   # use ~/.bashrc if on bash
```

Then fully quit and restart Cursor.

After the user confirms they've done this, re-run Check 1.

---

### Check 2: Is the redirect URI registered correctly?

If env vars are set but auth still fails, the redirect URI may be missing or wrong.

Tell the user to go back to https://app.asana.com/0/my-apps, open their app, and confirm this exact URI is listed under OAuth redirect URIs:

```
cursor://anysphere.cursor-mcp/oauth/callback
```

Common mistakes:
- Trailing slash added (`cursor://anysphere.cursor-mcp/oauth/callback/`)
- HTTP instead of the `cursor://` scheme
- URI not saved after adding

---

### Check 3: Did Cursor load the updated environment?

Environment variables set in a shell profile are only available to processes started after that profile was sourced. If the user set the vars but didn't restart Cursor, the plugin won't see them.

Confirm the user fully quit Cursor (not just closed the window) and reopened it after running `source`.

On macOS, "quit" means **Cmd+Q**, not just closing the window.

---

### Check 4: Is the MCP server reachable?

If all of the above look correct, test whether the Asana MCP server is reachable:

```bash
curl -I https://mcp.asana.com/v2/mcp
```

A 4xx response (like 401 or 405) means the server is up and rejecting unauthenticated requests — that's expected and means connectivity is fine. A timeout or DNS failure means a network issue on the user's side.

---

### Check 5: Plugin not showing MCP tools in Cursor

If the plugin is installed but Asana tools don't appear in the agent's tool list:

1. Go to **Cursor Settings → Features** → make sure **Include third-party Plugins, Skills, and other configs** is enabled
2. Go to **Cursor Settings → Tools & MCP** — check if "asana" appears and is toggled on
3. If not listed, the plugin may not have installed correctly — ask the user to reinstall from the Marketplace

---

## Escalation

If none of the above resolves the issue, direct the user to:

- Asana developer docs: https://developers.asana.com/docs/connecting-mcp-clients-to-asanas-v2-server
- Asana developer forum: https://forum.asana.com/c/forum-en/api/24 
