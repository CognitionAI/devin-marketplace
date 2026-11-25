# CodeRabbit

CodeRabbit is the governance and control layer for agentic software development helping developers trust AI written code.

This Devin marketplace package connects to CodeRabbit's hosted MCP service.
It uses the product description, homepage, repository, and brand mark from the
[canonical Claude plugin](https://github.com/coderabbitai/skills/blob/main/.claude-plugin/plugin.json).

Connect with a CodeRabbit account that has access to the relevant organization
and repositories. Available tools depend on the OAuth grant, account permissions,
and product entitlements. The default endpoint is the US service.

The [MCP guide](https://github.com/coderabbitai/skills/blob/main/docs/mcp.md)
explains hosted account, usage, pull-request, and CodeRabbit Secure workflows,
plus the separate CLI path for local code reviews. This hosted connector cannot
read unsynced files from a local checkout. Local CLI reviews require their own
installation and sign-in. This package does not bundle the portable skills or
promise an interactive MCP Apps interface in Devin.

Devin uses its native OAuth discovery for this server. The Claude manifest's
explicit scope string is reference metadata, not an assertion that Devin requests
the same scopes. Devin's documented explicit-scope field requires a registered
OAuth client ID; this package does not invent one or supply credentials.

- [Documentation](https://docs.coderabbit.ai/api/platform-api#use-hosted-mcp)
- [Support](https://www.coderabbit.ai/contact-us/support)
- [Privacy](https://www.coderabbit.ai/privacy-policy)
- [Terms](https://www.coderabbit.ai/terms-of-service)
- [Canonical skills and plugins](https://github.com/coderabbitai/skills)

The bundled logo is the same asset referenced by the Claude plugin. CodeRabbit
branding and trademark rights remain with CodeRabbit.
