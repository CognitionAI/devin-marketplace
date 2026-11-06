---
name: export
description: Export a webpage or file in its native format, optionally bundling all resources (CSS, JS, images) into a ZIP archive for offline use. Use when the user wants to save a webpage for offline viewing, download a page with all its assets, or export web content.
---

# Export

Use the Browserless `/export` REST API to fetch and export a webpage or file in its native format, with optional resource bundling.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless export endpoint:

```
POST ${BROWSERLESS_API_URL}/export?token=${BROWSERLESS_TOKEN}
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
  "includeResources": false,
  "gotoOptions": {
    "waitUntil": "networkidle0"
  },
  "bestAttempt": false,
  "waitForTimeout": 0,
  "waitForSelector": null,
  "waitForEvent": null,
  "waitForFunction": null
}
```

Parameters:
- `url` (string, required): The webpage or file URL to export.
- `includeResources` (boolean, optional, default `false`): When `true`, bundles the HTML and all linked assets (CSS, JS, images) into a ZIP file for offline use.
- `gotoOptions` (object, optional): Puppeteer `Page.goto()` options. Common values for `waitUntil`: `"load"`, `"domcontentloaded"`, `"networkidle0"`, `"networkidle2"`.
- `bestAttempt` (boolean, optional, default `false`): When `true`, continues even if async events (waitFor*) fail or timeout.
- `waitForTimeout` (number, optional): Milliseconds to wait after page load before exporting.
- `waitForSelector` (object, optional): Wait for a CSS selector to appear. Format: `{ "selector": "#content", "timeout": 5000 }`.
- `waitForEvent` (object, optional): Wait for a page event. Format: `{ "event": "load", "timeout": 5000 }`.
- `waitForFunction` (object, optional): Wait for a JS function to return truthy. Format: `{ "fn": "() => document.title !== ''", "timeout": 5000 }`.

### Response

The response content type depends on what is being exported:
- **HTML pages**: `text/html` — raw HTML markup.
- **PDF files**: `application/pdf` — binary PDF data.
- **Images**: Appropriate MIME type (e.g., `image/jpeg`) — binary image data.
- **ZIP archives** (when `includeResources: true`): `application/zip` — contains the HTML file and all its resources.

The response includes `Content-Disposition` headers for file downloads.

## Execution

Use `curl` via Bash to make the request. Always save the output to a file with `-o` since the response may be binary. Example:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/export?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -o exported_page.html \
  -d '{"url": "https://example.com"}'
```

For ZIP export with all resources:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/export?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -o exported_site.zip \
  -d '{"url": "https://example.com", "includeResources": true}'
```

Choose the output filename extension based on what the user is exporting (`.html`, `.pdf`, `.zip`, etc.). When `includeResources` is true, always use `.zip`.
