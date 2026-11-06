---
name: map
description: Discover and map all URLs on a website using the Browserless map API. Crawls sitemaps, pages, and subdomains to build a list of all URLs. Use when the user wants to map a website's structure, find all pages on a site, discover URLs, or get a sitemap.
---

# Map

Use the Browserless `/map` REST API to discover and list all URLs on a website.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless map endpoint:

```
POST ${BROWSERLESS_API_URL}/map?token=${BROWSERLESS_TOKEN}
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

### Request body

```json
{
  "url": "https://example.com",
  "limit": 100
}
```

Parameters:
- `url` (string, required): Base URL to discover links from. Must be http:// or https://.
- `search` (string, optional): Query to rank results by relevance. Use this to find specific pages.
- `limit` (number, optional, default 5000): Max number of URLs to return (1-5000).
- `timeout` (number, optional): Request timeout in milliseconds.
- `sitemap` (string, optional, default `"include"`): Sitemap discovery mode.
  - `"include"` - Use sitemap alongside crawling.
  - `"skip"` - Don't use sitemap, crawl only.
  - `"only"` - Only use sitemap, don't crawl.
- `includeSubdomains` (boolean, optional, default `true`): Include URLs from subdomains.
- `ignoreQueryParameters` (boolean, optional, default `true`): Remove query params to reduce duplicates.
- `location` (object, optional): Geo-targeting.
  - `country` (string): Country code, e.g. `"us"`, `"gb"`, `"de"`.
  - `languages` (string[]): Preferred languages.

### Response

```json
{
  "success": true,
  "links": [
    {
      "url": "https://example.com/page1",
      "title": "Page Title",
      "description": "Page description."
    },
    {
      "url": "https://example.com/page2"
    }
  ]
}
```

Response fields:
- `success` (boolean): Whether the operation succeeded.
- `links` (array): Discovered URLs with optional title and description.

## Execution

Use `curl` via Bash to make the request. Example:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/map?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "limit": 100}'
```

Present the discovered URLs to the user in a readable format. If the user wants to search for specific pages, use the `search` parameter to filter by relevance.
