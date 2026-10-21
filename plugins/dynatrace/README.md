# Dynatrace

Dynatrace's hosted MCP server plus Dynatrace's official Agent Skills and
workflow prompts, so Devin writes valid DQL and follows Dynatrace's own
investigation steps.

## Connecting

| Name | What to enter |
| --- | --- |
| `DYNATRACE_ENVIRONMENT_HOST` | The host of your Dynatrace environment, e.g. `abc12345.apps.dynatrace.com`. Host only: no `https://`, no path, no trailing slash. |
| `DYNATRACE_PLATFORM_TOKEN` | A Dynatrace platform token with the scopes below. |

Any Dynatrace domain works, e.g. `abc12345.live.dynatrace.com` or a
`dynatracelabs.com` host, not only `apps.dynatrace.com`.

Dynatrace's own plugin takes the full URL in `DT_ENVIRONMENT`
(`https://abc12345.apps.dynatrace.com`). Devin only accepts a host name in a
server URL, so here the `https://` is fixed in the manifest and the value is
the host. Do not paste the URL from Dynatrace's instructions as is.

### Platform token scopes

The token needs the MCP gateway scopes and the scopes of the data Devin should
read. Dynatrace maintains the list in its
[MCP server documentation](https://docs.dynatrace.com/docs/shortlink/dynatrace-mcp-server).

The server also receives a `Dt-External-Source: dynatrace-for-ai/<version>`
header, the value Dynatrace's plugin sends, so Dynatrace can attribute the
traffic. Keep `<version>` equal to the upstream plugin version below.

## Upstream content

`skills/` comes from https://github.com/Dynatrace/dynatrace-for-ai at commit
`4f9aa71f9802aa6db0a4069ae5619eb3392ff411` (plugin version 8.0.1, Apache-2.0;
see `NOTICE` and `LICENSE`):

* The `dt-daily-standup`, `dt-health-check`, `dt-incident-response`,
  `dt-investigate-error`, `dt-performance-regression` and
  `dt-troubleshoot-problem` skills are upstream's `prompts/<name>.prompt.md`
  turned into skills: the body is unchanged, and the front matter is replaced
  by `name`, upstream's `description` followed by "Runs against Dynatrace
  through the Dynatrace MCP server.", and `license`.
* Every other directory is an unmodified copy of upstream's `skills/<name>`.

To update: replace those directories from a newer upstream commit, convert
`prompts/` the same way, then update the commit here and in `NOTICE` and the
version in the `Dt-External-Source` header.
