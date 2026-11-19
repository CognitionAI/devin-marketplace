---
name: search
description: Search the web using the Browserless search API. Returns structured search results from web, news, and image sources with optional content scraping. Use when the user wants to search the web, find information online, or look up something on the internet.
---

# Search

Use the Browserless `/search` REST API to perform web searches and get structured results.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless search endpoint:

```
POST ${BROWSERLESS_API_URL}/search?token=${BROWSERLESS_TOKEN}
Content-Type: application/json
```

## Authentication

Before making the request, source the saved credentials and resolve the token:

```bash
source ~/.browserless/.env 2>/dev/null
```

The token is resolved in this order:
1. `$BROWSERLESS_TOKEN` environment variable (if already set in the shell)
2. `~/.browserless/.env` file (written by `/browserless:auth`)
3. If neither exists, ask the user to run `/browserless:auth` to configure their token

For the API URL, use `$BROWSERLESS_API_URL` if set, otherwise default to `https://production-sfo.browserless.io`.

### Query parameters

These are appended to the URL as query parameters (e.g., `?token=...&timeout=30000`):

- `token` (string): Authorization token (handled by auth, see above).
- `timeout` (number): Timeout for the search operation in milliseconds.

### Request body

```json
{
  "query": "<search query>",
  "sources": ["web"],
  "limit": 10,
  "lang": "en"
}
```

#### Parameters:

- `query` (string, required): The search query.
- `sources` (array of strings): Data sources to search. Values: `"web"`, `"news"`, `"images"`. Default to `["web"]`.
- `limit` (number): Maximum number of results to return.
- `lang` (string): Language code — `"en"`, `"es"`, `"de"`, `"fr"`, `"ja"`, etc.
- `location` (string): Location context for the search.
- `country` (string): Country context for the search.
- `tbs` (string): Time-based filter. Values: `"day"`, `"week"`, `"month"`, `"year"`.
- `categories` (array of strings): Content category filters. Values: `"github"`, `"pdf"`, `"research"`.
- `timeout` (number): Search timeout in milliseconds (body-level override).

#### `scrapeOptions` (object) — Scrape each result page:

- `formats` (array of strings, required): Output formats for scraped content — `"markdown"`, `"html"`, `"links"`, `"screenshot"`.
- `onlyMainContent` (boolean): Extract only the main content, skipping navigation/footer/sidebar.
- `stripNonContentTags` (boolean): Strip non-content HTML tags from output.
- `removeBase64Images` (boolean): Remove base64-encoded images from output.
- `includeTags` (array of strings): Only include content from these HTML tags.
- `excludeTags` (array of strings): Exclude content from these HTML tags.

### Response

```json
{
  "success": true,
  "data": {
    "web": [
      {
        "title": "Result Title",
        "url": "https://example.com",
        "description": "Result description snippet.",
        "position": 1
      }
    ]
  },
  "totalResults": 10
}
```

## Execution

Use `curl` via Bash to make the request. Example:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/search?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "browserless headless browser", "sources": ["web"], "limit": 10}'
```

Present the results in a readable format to the user. If the user wants to deep-dive into a specific result, suggest using the `smart-scrape` skill to fetch that page's content.
