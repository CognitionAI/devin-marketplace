# Black Duck

Connect Devin to [Black Duck Signal](https://www.blackduck.com/signal-ai-appsec.html)
to scan code changes or selected files and review actionable security findings.

## Setup

Install the Black Duck plugin from Devin's marketplace and supply
`BLACKDUCK_MCP_GATEWAY_KEY` through the installation's credentials.
You need a [Signal license and API key](https://www.blackduck.com/signal-ai-appsec/early-access.html)
and Node.js **24.0.0 or newer**, including `npx`, on the machine running the server.
The stdio server must run on the machine containing the source code to scan.

The plugin runs `npx -y @black-duck/mcp-server@1.1.8`, pinned to the version
in the supplied upstream MCP registry metadata. The registry metadata package
`@blackducksoftware/mcp-server-registry` is not the executable server.

Allow outbound HTTPS to `registry.npmjs.org` for package installation and to
`repo.blackduck.com` and `llm.core.blackduck.com` for scanning. Source code in the
selected scan scope is sent to Black Duck for analysis.

## Use

The `blackduck-security-scan` skill selects the appropriate scan and guides
review and remediation of the returned findings. Example requests:

- "Use Black Duck to scan my staged and unstaged changes."
- "Use Black Duck to scan this branch's changes relative to main."
- "Use Black Duck to scan all files under the src/auth directory."

`run_changes_security_scan` supports uncommitted changes or comparison with a
reference branch in a Git repository. `run_security_scan` accepts specific files
and directories, including projects without Git. Both return scan status,
severity counts, a SARIF report path, MCP resource URIs, and analysis guidance.

## Troubleshooting

Check the Node.js version, saved gateway key, Signal license, and network access
if the server cannot start or a scan fails. A failed or timed-out scan does not
mean the code has no vulnerabilities.

Upstream supports these optional server environment settings; they are left at
their defaults by this plugin:

| Variable | Default | Purpose |
| --- | --- | --- |
| `BLACKDUCK_HOME` | User's home directory | Override the default `.blackduck` folder location |
| `BLACKDUCK_MCP_TOOL_TIMEOUT` | `1800000` | Scan timeout in milliseconds (30 minutes) |
| `BLACKDUCK_MCP_LOG_LEVEL` | `info` | `error`, `warn`, `info`, or `debug` logging |

See the [upstream README](https://github.com/blackducksoftware/mcp-server#readme)
and [Signal documentation](https://documentation.blackduck.com/bundle/signal/page/topics/c_signal_overview.html)
for configuration and troubleshooting details.

The bundled logo is the [Black Duck Software GitHub organization avatar](https://avatars.githubusercontent.com/u/431461?v=4).
