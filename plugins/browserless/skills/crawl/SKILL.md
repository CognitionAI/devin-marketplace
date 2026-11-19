---
name: crawl
description: Crawl a website starting from a seed URL, following links to configurable depth while scraping all discovered pages. Use when the user wants to crawl an entire website, scrape multiple pages, extract content from many pages at once, or do a deep site-wide scrape.
---

# Crawl

Use the Browserless `/crawl` REST API to asynchronously crawl a website, following links to a configurable depth and scraping every discovered page.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to start the crawl, then poll for results:

```
POST ${BROWSERLESS_API_URL}/crawl?token=${BROWSERLESS_TOKEN}        # Start crawl
GET  ${BROWSERLESS_API_URL}/crawl/{id}?token=${BROWSERLESS_TOKEN}   # Check status / get results
GET  ${BROWSERLESS_API_URL}/crawl?token=${BROWSERLESS_TOKEN}        # List all crawls
DELETE ${BROWSERLESS_API_URL}/crawl/{id}?token=${BROWSERLESS_TOKEN} # Cancel a crawl
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

### Request body (POST /crawl)

```json
{
  "url": "<seed URL - required, must be http:// or https://>",
  "limit": 100,
  "maxDepth": 5,
  "scrapeOptions": {
    "formats": ["markdown"]
  }
}
```

#### Core parameters:
- `url` (string, required): The starting URL to crawl.
- `limit` (number, optional, default `100`): Maximum number of pages to crawl (max depends on your plan).
- `maxDepth` (number, optional, default `5`): How many link-levels deep to follow from the seed URL (0-20).
- `maxRetries` (number, optional, default `1`): Retry attempts per failed page (0-5).
- `delay` (number, optional, default `200`): Milliseconds to wait between requests (0-10000).

#### Link-following controls:
- `allowExternalLinks` (boolean, optional, default `false`): Follow links to external domains.
- `allowSubdomains` (boolean, optional, default `false`): Follow links to subdomains.
- `includePaths` (array of strings, optional): Regex patterns — only crawl URLs matching these patterns.
- `excludePaths` (array of strings, optional): Regex patterns — skip URLs matching these patterns.

#### Sitemap handling:
- `sitemap` (string, optional, default `"auto"`): How to use the site's sitemap.
  - `"auto"` - Try sitemap first, fall back to link extraction.
  - `"force"` - Only use sitemap; fail if unavailable.
  - `"skip"` - Ignore sitemap entirely; follow links only.

#### `scrapeOptions` (object, optional): Per-page scrape configuration.
- `formats` (array of strings, default `["markdown"]`): Output formats — `"markdown"`, `"html"`, `"rawText"`.
- `onlyMainContent` (boolean, default `true`): Extract only primary content, skip nav/footer/sidebar.
- `includeTags` (array of strings, optional): Only include content from these HTML selectors.
- `excludeTags` (array of strings, optional): Exclude content from these HTML selectors (e.g., `"nav"`, `"footer"`).
- `waitFor` (number, default `0`): Milliseconds to wait after page load before scraping (0-30000).
- `headers` (object, optional): Custom HTTP headers to send with each request.
- `timeout` (number, default `30000`): Navigation timeout in milliseconds (1000-180000).

#### Webhook (object, optional): Get notified instead of polling.
- `url` (string, required): HTTPS endpoint to receive events.
- `events` (array of strings, optional, default `["completed"]`): Events to subscribe to — `"page"`, `"completed"`, `"failed"`.

### Response (POST /crawl — start)

```json
{
  "success": true,
  "id": "crawl_abc123def456",
  "url": "https://production-sfo.browserless.io/crawl/crawl_abc123def456"
}
```

### Response (GET /crawl/{id} — status & results)

```json
{
  "status": "completed",
  "total": 15,
  "completed": 15,
  "failed": 0,
  "expiresAt": "2025-07-01T12:00:00.000Z",
  "next": null,
  "data": [
    {
      "status": "completed",
      "contentUrl": "<pre-signed S3 URL with scraped content>",
      "metadata": {
        "title": "Page Title",
        "description": "Meta description",
        "language": "en",
        "sourceURL": "https://example.com/page",
        "statusCode": 200,
        "scrapedAt": "2025-07-01T10:30:00.000Z",
        "error": null
      }
    }
  ]
}
```

Key fields:
- `status`: `"in-progress"`, `"completed"`, `"failed"`, or `"cancelled"`.
- `total`, `completed`, `failed`: Progress counters.
- `data`: Array of scraped pages. Each has a `contentUrl` (pre-signed S3 URL, expires in 1 hour) and `metadata`.
- `next`: Pagination URL if there are more results.
- `expiresAt`: When results expire (24 hours after completion).

## Execution

The crawl API is asynchronous. Start the crawl, then poll for results:

### Step 1: Start the crawl

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/crawl?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "maxDepth": 3,
    "limit": 50,
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  }'
```

Save the `id` from the response.

### Step 2: Poll for results

```bash
source ~/.browserless/.env 2>/dev/null
curl -s "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/crawl/CRAWL_ID?token=$BROWSERLESS_TOKEN"
```

Check the `status` field. If `"in-progress"`, wait a few seconds and poll again. If `"completed"`, the results are in `data`.

### Step 3: Fetch page content

Each result's `contentUrl` is a pre-signed URL to the scraped content. Fetch it directly:

```bash
curl -s "PRE_SIGNED_URL"
```

Present a summary of crawled pages (count, titles, URLs) and offer to show content for specific pages. If the crawl is still in progress, show the progress (completed/total) and continue polling.

### Listing and cancelling crawls

```bash
# List all crawls
curl -s "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/crawl?token=$BROWSERLESS_TOKEN"

# Cancel a crawl
curl -s -X DELETE "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/crawl/CRAWL_ID?token=$BROWSERLESS_TOKEN"
```

**Note**: The Crawl API is available on Cloud plans only. Results expire 24 hours after completion. Content URLs expire 1 hour after generation.
