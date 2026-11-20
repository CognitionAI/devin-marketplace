---
name: mrscraper
description: |
  Connect, authenticate, route, and troubleshoot MrScraper MCP, and check account usage with the status tool. For a known public URL, retrieve HTML, Markdown, a screenshot, brand data, or structured JSON with mrscraper-fetch; use mrscraper-serp for query-first discovery through web search.
---

# MrScraper MCP

Use this skill for connection and authentication checks, tool selection, shared
response handling, account status, and troubleshooting. Load the focused fetch
or SERP skill for page retrieval and web search.

MrScraper MCP has six scraping and search tools, plus account status:

| Tool | Description |
| --- | --- |
| status | Return the raw account status API response without summarizing, redacting body fields, or adding calculated fields. |
| scrapeHtml | Retrieve the raw HTML of a page. Browser rendering is optional. |
| scrapeMarkdown | Retrieve a page as Markdown. Including HTML also enables browser rendering and returns both outputs as JSON. |
| getScreenshot | Capture a base64 screenshot of the full page or top viewport. Browser rendering is always enabled. |
| scrapeBrand | Extract a website's colors, typography, logos, and social links as JSON. |
| scrapeJson | Extract structured JSON from a page using a natural-language prompt. Append Json Schema: and a JSON schema to shape the output. |
| webSearch | Search the web and return ranked results with titles, URLs, descriptions, and sources. |

## Step 1 — Verify or Connect MrScraper MCP

Check whether the current client exposes these seven tools from the MrScraper
MCP provider:

    status  scrapeHtml  scrapeMarkdown  getScreenshot  scrapeBrand  scrapeJson  webSearch

The client may display server-qualified names. Match the provider and
unqualified tool name; do not assume a fixed namespace.

If the tools are already available, use the existing connection. If they are
missing, ask the user to enable the existing MrScraper connection or configure
the managed Streamable HTTP endpoint:

    https://mcp.mrscraper.com/mcp

A self-managed deployment may expose the same tools over Streamable HTTP or
stdio. Connection setup belongs to the MCP client. After setup or reconnection,
list the available tools and confirm all seven names before claiming the
integration is ready. A client that still lists scraperAPI has cached the
previous tool list; start a new session or reconnect so it loads the current
tools.

## Step 2 — Authenticate

MrScraper MCP authenticates through OAuth 2.1. Authentication belongs to the
MCP connection and is never a tool argument.

When the connection is not authorized, start the MCP client's authorization
flow. Let the client discover the authorization metadata, open the MrScraper
consent page, complete authorization, store the resulting credentials, and
refresh access tokens. The user may need to approve access in a browser, but
must not paste an authorization code, access token, refresh token, API key, or
other credential into the conversation.

Never place credentials in tool arguments, print them, write them into project
artifacts, or manually reproduce the OAuth exchange. Do not configure an
API-key or bearer-token fallback from these skills.

The connection uses two scopes: scraper:read for the six scraping and search
tools, and account:read for status. A tool called without its scope returns
403 insufficient_scope; reauthorize the connection so the client requests it.
Connections authorized with the older scrape:read and scrape:write scopes must
be authorized again.

Verify end-to-end access with status, which reads the account without
retrieving a page:

    {}

A successful response confirms that the connection can authenticate and reach
MrScraper. If it fails, report the error and do not claim setup is complete.

## Step 3 — Route the Request

| User outcome | MCP tool or skill |
| --- | --- |
| Read, summarize, or preserve a known public page | [mrscraper-fetch](../mrscraper-fetch/SKILL.md) with scrapeMarkdown, or scrapeHtml when the page structure matters |
| Capture what a page looks like | [mrscraper-fetch](../mrscraper-fetch/SKILL.md) with getScreenshot |
| Extract specific fields from a page as JSON | [mrscraper-fetch](../mrscraper-fetch/SKILL.md) with scrapeJson, or local extraction from retrieved content |
| Get a website's colors, typography, logos, and social links | [mrscraper-fetch](../mrscraper-fetch/SKILL.md) with scrapeBrand |
| Discover relevant pages from a web search query | [mrscraper-serp](../mrscraper-serp/SKILL.md) with webSearch, then retrieve selected pages |
| Check the plan, token usage, or remaining tokens | status |

### Retrieve first, extract locally

scrapeHtml and scrapeMarkdown return raw page content. Produce summaries,
tables, JSON, and other structured output from that content with local analysis
or extraction logic. The raw response preserves complete page context for later
questions, validation, and changes to the requested schema.

Use scrapeJson when the user asks MrScraper to extract the data, or when a
prompt-driven extraction is clearly simpler than local logic. Keep the raw page
as well when later questions may need details that the extraction leaves out.

Prefer this workflow for pages with a shared layout:

1. Retrieve representative pages and inspect their content.
2. Understand the shared page structure and required fields.
3. Define a stable output schema and reusable local extractor.
4. Retrieve the remaining pages, in parallel when safe.
5. Apply the same extractor to every saved response.

Request Markdown when readable text is enough and HTML when an extractor needs
the page structure.

For discovery-first work, call webSearch, select relevant URLs, and retrieve
the pages whose content will inform the answer.

MrScraper MCP does not create AI scrapers, rerun saved scrapers, or list stored
results. Point the user to the MrScraper dashboard at https://app.mrscraper.com
for those.

## Step 4 — Handle Output and Artifacts

Every tool returns the same response envelope in MCP structuredContent and in a
formatted JSON text block:

    {
      "status_code": 200,
      "data": {},
      "headers": {}
    }

data holds the API response body: HTML or Markdown text from scrapeHtml and
scrapeMarkdown, and JSON from the other tools. Prefer structuredContent when
available. An HTTP or network failure adds error and sets the MCP result's
isError flag; a network failure has status_code null. Invalid inputs are
rejected before any request is sent. Check those signals before trusting data.
Credential-bearing response headers are removed.

MrScraper tools do not accept output paths. When the user requests an artifact,
wait for a successful tool result, select the requested value, and save it with
the environment's local file-writing capability. A screenshot is base64 image
data in data.screenshot; decode it before saving an image.

Save substantial intermediate artifacts under the current project's
.mrscraper directory unless the user specifies another location. This project
artifact directory is unrelated to MCP connection credentials. Keep artifacts
out of version control unless the user asks to commit them.

saveResult defaults to false. Set it to true only when the user wants a
scraping result kept in the MrScraper dashboard Result tab.

## Step 5 — Review Account Usage

Call status with an empty object:

    {}

data is the raw account status response, without summaries or calculated
fields. Account details are in data.data, including tokenLimit, tokenUsage,
subscriptionItem, and scraperAllowance:

    {
      "status_code": 200,
      "data": {
        "message": "...",
        "data": {
          "tokenLimit": 100000,
          "tokenUsage": 2500,
          "stripeStatus": "active",
          "subscriptionItem": {
            "name": "...",
            "tokenLimit": 100000
          },
          "scraperAllowance": {
            "remaining": 97500
          }
        }
      },
      "headers": {}
    }

Report the fields the user asked about. The response also carries account
identity and billing identifiers; do not repeat them unless the user asks.
Check remaining tokens before a large batch of page retrievals. status reports
account usage, not the progress of a request.

## Step 6 — Troubleshoot

- Missing tools: enable or reconnect the MrScraper MCP connection, then confirm
  all seven tools are exposed.
- Unauthorized or expired authorization: reauthorize the OAuth 2.1 connection
  through the MCP client.
- 403 insufficient_scope: reauthorize so the client requests scraper:read for
  scraping and search, or account:read for status.
- Input-contract error: inspect the tool schema and omit inputs that do not
  apply. scraperAPI was replaced by scrapeHtml, scrapeMarkdown, and
  getScreenshot; brand and JSON extraction are scrapeBrand and scrapeJson; and
  webSearch takes query, country, and numResults.
- Page incomplete or missing dynamic content: load mrscraper-fetch and revise
  page-loading inputs deliberately.
- Search results weak: load mrscraper-serp and refine the query, country, or
  number of results.

## Limits

Use another tool for:

- Clicking controls, completing forms, or authenticated browser sessions.
- Parsing local PDFs, documents, spreadsheets, or other files.
- Recurring monitoring, notifications, or scheduling.

Explain the boundary and continue with any supported portion of the task.
