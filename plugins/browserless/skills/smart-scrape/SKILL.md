---
name: smart-scrape
description: Scrape a webpage using Browserless smart-scrape API with cascading strategies (HTTP fetch, proxy, headless browser, captcha solving). Returns content in multiple formats including markdown, HTML, screenshot, PDF, and links. Use when the user wants to scrape, read, or extract content from a webpage.
---

# Smart Scrape

Use the Browserless `/smart-scrape` REST API to scrape a webpage. The API automatically tries cascading strategies: direct HTTP fetch, proxy, headless browser, and browser with captcha solving.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless smart-scrape endpoint:

```
POST ${BROWSERLESS_API_URL}/smart-scrape?token=${BROWSERLESS_TOKEN}
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
  "url": "<target URL - required, must be http:// or https://>",
  "formats": ["markdown", "html", "screenshot", "pdf", "links"],
  "timeout": 30000
}
```

- `url` (required): The webpage URL to scrape.
- `formats` (optional, default `["html"]`): Array of output formats. Choose based on what the user needs:
  - `"markdown"` - Best for reading/summarizing content. **Default to this when the user just wants to read a page.**
  - `"html"` - Raw HTML content.
  - `"screenshot"` - Base64-encoded screenshot image.
  - `"pdf"` - Base64-encoded PDF.
  - `"links"` - Array of all links found on the page.
- `timeout` (optional): Max time in milliseconds.

### Response

```json
{
  "ok": true,
  "statusCode": 200,
  "content": "<html>...</html>",
  "contentType": "text/html; charset=utf-8",
  "strategy": "http-fetch",
  "attempted": ["http-fetch"],
  "message": null,
  "screenshot": null,
  "pdf": null,
  "markdown": "# Page Title\n...",
  "links": ["https://example.com/page1", "..."]
}
```

Key response fields:
- `ok`: Whether the scrape succeeded.
- `strategy`: Which strategy worked (http-fetch, http-proxy, browser, browser-captcha).
- `attempted`: All strategies that were tried.
- `markdown`, `screenshot`, `pdf`, `links`: Populated based on requested formats.
- `message`: Error description if `ok` is false.

## Execution

Use `curl` via Bash to make the request. Default to `["markdown"]` format unless the user asks for something specific. Present the markdown content directly to the user, or save binary outputs (screenshot/pdf) to files.

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/smart-scrape?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "formats": ["markdown"]}'
```
