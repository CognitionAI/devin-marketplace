# Listings API

Manage local citations and submit business data to 50+ sites. Keep names, addresses, phone numbers and hours consistent across locations; manage listings, reviews, posts and analytics through Listings API.

Try a free 24-hour Day Pass for up to 2 locations, with no credit card required. Watch your agents seamlessly integrate with Listings API and publish data to the demo sites!

- [Website](https://www.listingsapi.com/)
- [MCP documentation](https://listingsapi.com/guides/connect-an-ai-agent-with-mcp)
- [Day Pass guide and current limits](https://listingsapi.com/docs/day-pass.md)
- [Day Pass signup](https://listingsapi.com/signup?plan=day-pass&campaign=daypass)
- [Source repository](https://github.com/listings-api/listingsapi-mcp)
- Support: support@listingsapi.com

## Connect in Devin CLI

**Compatibility status:** Local installation and OAuth login succeeded in Devin CLI `3000.11.3`. Its generated request includes `read write` despite `--scopes read`; verify the intended account and actual permissions before approving.

Install the [official Devin CLI](https://docs.devin.ai/cli), sign in to your Devin account, then run these commands from the marketplace checkout:

```bash
devin plugins install --local ./plugins/listingsapi
devin mcp login listingsapi --scopes read
```

For a standalone copy, pass its plugin directory to `devin plugins install --local` instead. Complete the Listings API OAuth flow with the account you want Devin to read. The endpoint is `https://listingsapi.com/mcp` and uses Streamable HTTP. No local server or API key is bundled.

Start a new Devin session and ask it to call `whoami` through this MCP server. Verify the actual tool result. Authorize `locations_all` separately if you also want Devin to inspect location records. Plugin installation alone does not authorize the service or activate a Day Pass. Use read access for inspection; write operations require an authorized task and appropriate service access. The included [workflow skill](skills/listingsapi/SKILL.md) documents authentication and account workflows.

The plugin manifest and logo come from the Listings API repository under MIT. The workflow skill is MIT-0, as stated in [its license](skills/listingsapi/LICENSE).
