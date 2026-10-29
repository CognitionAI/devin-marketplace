---
name: mrscraper-serp
description: |
  Discover public pages through web search with MrScraper's webSearch tool using a search query or a search results URL. Use when no target URL is known or the user asks to inspect web search results. After discovery, retrieve selected pages with mrscraper-fetch.
---

# Discover Pages with MrScraper MCP Web Search

Use the webSearch tool supplied by the MrScraper MCP server when a task begins
with a search query rather than a known target URL. Use
[mrscraper](../mrscraper/SKILL.md) for connection troubleshooting, account
status, or broader routing.

## Step 1 — Build the Query

Include the important entity, attribute, location, or date in url, and set
raw=false to receive parsed results:

    {
      "url": "web scraping best practices",
      "raw": false
    }

The input can also be a complete search results URL:

    {
      "url": "https://www.google.com/search?q=web+scraping&gl=us&hl=en&start=20",
      "raw": false
    }

For a search results URL, the tool reads q, gl, hl, and start. Explicit region,
language, and page inputs take precedence.

## Step 2 — Set Locale and Pagination

Set both country and language when results must match a locale:

    {
      "url": "running shoes",
      "raw": false,
      "region": "id",
      "language": "id",
      "page": 2
    }

Start with the first page unless the user requests broader coverage. Inspect
the current page before requesting another.

## Step 3 — Choose the Output

raw defaults to true, which returns result-page HTML as the Python SDK does.
Set raw=false for parsed JSON; organic results are in data.data.organic, next
to sections such as people_also_ask and pagination.

Request result-page HTML when the page itself is needed:

    {
      "url": "iphone 17"
    }

Use JavaScript rendering for dynamic result features such as AI Overview:

    {
      "url": "what is web scraping",
      "raw": false,
      "render_js": true
    }

### Parameters

| MCP input | Default | Request mapping | Use |
| --- | --- | --- | --- |
| url | required | Body query | Search query or complete search results URL. |
| raw | true | Body format=html | Return result-page HTML; set false to use format. |
| format | json | Body format | json or html when raw=false. |
| region | URL value or omitted | Body region | Result country, such as us or id. |
| language | URL value or omitted | Body language | Result language, such as en or id. |
| page | URL value or omitted | Body page | Positive, one-based results page. |
| render_js | false | Body renderJs | Render JavaScript-dependent result features. |
| timeout | 600 | MCP upstream deadline | Maximum wait in seconds; not sent in the search body. |

Authentication is handled by the MCP client's OAuth 2.1 connection and is
never a tool input.

## Step 4 — Inspect the Results

The complete response envelope is available in MCP structuredContent and as
formatted JSON text. Prefer structuredContent. Check isError, error, and
status_code before using data.

When the user requests a search artifact, save the successful data or full
envelope with local file-writing capability; webSearch has no output-path
input.

## Step 5 — Continue with Relevant URLs

Select only URLs relevant to the user's goal, then load
[mrscraper-fetch](../mrscraper-fetch/SKILL.md) to retrieve and inspect each
selected page before deriving answers, comparisons, or structured output.

Run independent follow-up URLs in parallel when the environment supports safe
parallel execution. Keep the number of pages proportional to the requested
coverage. If the user only requested URL discovery, stop after the search.

## Step 6 — Handle Weak or Missing Results

- Set both region and language when the locale is wrong.
- Rewrite noisy queries around the important entity, attribute, and location.
- Request another result page only after checking the current page.
- Retry once with render_js=true when a dynamic result feature is required.
- Increase timeout when the MCP request deadline is too short.
- Use [mrscraper](../mrscraper/SKILL.md) when the connection or authentication
  fails.

webSearch is for public web search, not for discovering URLs within one
known site.
