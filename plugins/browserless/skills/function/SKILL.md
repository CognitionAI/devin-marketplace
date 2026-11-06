---
name: function
description: Execute custom Puppeteer JavaScript code on the Browserless cloud. Use when the user needs to run arbitrary browser automation scripts, interact with page elements, fill forms, click buttons, or perform complex multi-step browser tasks that go beyond simple scraping.
---

# Function

Use the Browserless `/function` REST API to execute custom Puppeteer JavaScript code in a cloud browser.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless function endpoint:

```
POST ${BROWSERLESS_API_URL}/function?token=${BROWSERLESS_TOKEN}
Content-Type: application/javascript
```

OR with JSON payload:

```
POST ${BROWSERLESS_API_URL}/function?token=${BROWSERLESS_TOKEN}
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

### Option 1: JavaScript body (Content-Type: application/javascript)

Send raw JavaScript code directly. The function receives a `page` (Puppeteer Page) and optional `context` object, and must return `{ data, type }`.

```javascript
export default async ({ page, context }) => {
  await page.goto("https://example.com");
  const title = await page.title();
  return {
    data: { title },
    type: "application/json"
  };
};
```

### Option 2: JSON body (Content-Type: application/json)

```json
{
  "code": "export default async ({ page, context }) => { await page.goto(context.url); const title = await page.title(); return { data: { title }, type: 'application/json' }; };",
  "context": {
    "url": "https://example.com"
  }
}
```

Parameters:
- `code` (string, required): ESM JavaScript code. Must export a default async function that receives `{ page, context }` and returns `{ data, type }`.
- `context` (object, optional): Data passed into the function for dynamic behavior.

### Return value

The function must return:
- `data`: The result - can be a Buffer, JSON object, or plain text string.
- `type`: Content-Type string that determines the response format (e.g., `"application/json"`, `"text/plain"`, `"image/png"`).

### Response

The response body and content-type match what the function returns.

## Execution

Use `curl` via Bash. For simple scripts, use `application/javascript` content type. For scripts needing dynamic context data, use `application/json`. Example:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/function?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/javascript" \
  -d 'export default async ({ page }) => {
  await page.goto("https://example.com");
  const title = await page.title();
  return { data: { title }, type: "application/json" };
};'
```

Write the Puppeteer code based on the user's requirements. Use best practices: wait for selectors before interacting, handle navigation events, and return structured data.
