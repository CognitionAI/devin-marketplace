# AthenaHQ for Devin

Connect Devin to AthenaHQ to analyze brand visibility, share of voice, mentions,
citations, rankings, and competitors across AI search platforms.

## Connection

The plugin connects to AthenaHQ's hosted MCP server:

```text
https://api.athenahq.ai/api/mcp
```

In Devin Cloud, open the installed plugin's **athenahq** MCP settings and choose
**Connect MCP**. Sign in with your AthenaHQ account, choose your organization, and
approve the connection before starting a session.

The manifest includes a public OAuth client ID registered for Devin Cloud at
`app.devin.ai`, with callback `https://api.devin.ai/mcp/oauth/callback`. It is not a
secret and grants no account access without your authorization. No API key or
client secret belongs in the manifest. Dedicated Devin deployments and local CLI
clients need an OAuth client registered for their own callback URL.

Account analytics and write tools follow your existing access and role
permissions. Writes use the dashboard's validation and audit logging, and
some actions consume credits or permanently delete data.

See the [MCP documentation](https://docs.athenahq.ai/api-reference/mcp) for available
tools, permissions, and API-key setup for clients that require it.

## Try it

- "Use AthenaHQ to list the websites I can access."
- "Compare our share of voice with competitors over the latest available month."
- "Which sources are AI assistants citing about our brand?"

## Install before marketplace publication

In Devin Cloud, open **Customize → Plugins → Add plugin → Upload .zip** and upload
a zip containing this directory's contents, including `.devin-plugin/plugin.json`.
Wait for indexing to finish, choose **Connect MCP**, and complete OAuth. Start a
new session and ask Devin to list your websites. Confirm that it calls
`list_websites` successfully.

## Marketplace contribution

This directory is the distribution package for
[CognitionAI/devin-marketplace](https://github.com/CognitionAI/devin-marketplace).
Copy its contents to `plugins/athenahq/` in a checkout of that repository, then add
`"./plugins/athenahq"` to `optionalPlugins` in the marketplace's
`.devin-plugin/plugin.json`.

Run the marketplace's checks:

```bash
python3 scripts/validate.py --fix
python3 scripts/validate.py --fetch
```

Before submitting, complete the Devin installation and `list_websites` tool call
above, as required by the marketplace's
[contribution guide](https://github.com/CognitionAI/devin-marketplace/blob/main/.agents/skills/adding-a-plugin/SKILL.md).
Opening a pull request accepts the marketplace's
[Contributor License Agreement](https://github.com/CognitionAI/devin-marketplace/blob/main/CLA.md).
