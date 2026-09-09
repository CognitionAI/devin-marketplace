---
name: asana-setup
description: Detect and configure Asana MCP credentials. Run this before using any Asana tools.
---

# Asana MCP Setup

## Purpose

This skill ensures the Asana MCP server is correctly authenticated before any Asana tools are used.

The Asana MCP connection requires two credentials from a registered Asana OAuth app:
- `ASANA_CLIENT_ID`
- `ASANA_CLIENT_SECRET`

These must be set as environment variables in the user's shell profile.

## When to run this skill

Run this skill automatically if:
- The user asks to connect to Asana
- The user asks to use any Asana tool and the MCP connection fails
- The user says something like "set up Asana" or "configure Asana"

## Steps

### 1. Check if credentials are set

Check whether `ASANA_CLIENT_ID` and `ASANA_CLIENT_SECRET` are set in the user's environment. You can do this by running:

```bash
echo $ASANA_CLIENT_ID
echo $ASANA_CLIENT_SECRET
```

If both return non-empty values, skip to Step 4.

### 2. Guide the user to create an Asana OAuth app

If credentials are missing, tell the user:

> To connect Cursor to Asana, you need to register an OAuth app in Asana's developer console. Here's how:
>
> 1. Go to https://app.asana.com/0/my-apps
> 2. Click **Create new app** and select "MCP App" as the app type
> 3. Give it a name (e.g. "Cursor MCP")
> 4. Under **OAuth**, add this redirect URI: `cursor://anysphere.cursor-mcp/oauth/callback`
> 5. Copy your **Client ID** and **Client Secret**

### 3. Help the user set environment variables

Once the user has their credentials, instruct them to add these lines to their shell profile:

**For zsh (macOS default)** — add to `~/.zshrc`:

```bash
export ASANA_CLIENT_ID="your_client_id_here"
export ASANA_CLIENT_SECRET="your_client_secret_here"
```

**For bash** — add to `~/.bashrc` or `~/.bash_profile`:

```bash
export ASANA_CLIENT_ID="your_client_id_here"
export ASANA_CLIENT_SECRET="your_client_secret_here"
```

**For Windows (WSL)** — add to `~/.bashrc`:

```bash
export ASANA_CLIENT_ID="your_client_id_here"
export ASANA_CLIENT_SECRET="your_client_secret_here"
```

After saving, tell the user to run:

```bash
source ~/.zshrc   # or ~/.bashrc depending on their shell
```

Then restart Cursor.

### 4. Verify the connection

After credentials are set, confirm the MCP server is reachable by attempting to call an Asana tool (e.g. list workspaces). If it succeeds, confirm to the user that setup is complete.

If it fails, ask the user to verify:
- The redirect URI `cursor://anysphere.cursor-mcp/oauth/callback` is registered in their Asana app
- The Client ID and Client Secret were copied correctly (no extra spaces)
- They restarted Cursor after setting the environment variables
