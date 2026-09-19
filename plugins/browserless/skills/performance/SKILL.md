---
name: performance
description: Run a Lighthouse performance audit on a webpage and get scores for accessibility, best practices, performance, PWA, and SEO. Use when the user wants to audit a website's performance, check accessibility scores, run Lighthouse, or analyze page speed and SEO.
---

# Performance

Use the Browserless `/performance` REST API to run a Lighthouse audit on a webpage and get performance, accessibility, best practices, PWA, and SEO scores.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless performance endpoint:

```
POST ${BROWSERLESS_API_URL}/performance?token=${BROWSERLESS_TOKEN}
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
  "config": {
    "extends": "lighthouse:default",
    "settings": {
      "onlyCategories": ["performance", "accessibility", "best-practices", "seo", "pwa"]
    }
  }
}
```

Parameters:
- `url` (string, required): The webpage URL to audit.
- `config` (object, optional): Lighthouse configuration object.
  - `extends` (string): Set to `"lighthouse:default"` to use standard config.
  - `settings` (object): Lighthouse settings.
    - `onlyCategories` (array of strings, optional): Limit the audit to specific categories. Valid values: `"accessibility"`, `"best-practices"`, `"performance"`, `"pwa"`, `"seo"`. Default: all categories.
    - `onlyAudits` (array of strings, optional): Run only specific audits by name (e.g., `"unminified-css"`, `"first-contentful-paint"`).
  - `budgets` (array of objects, optional): Lighthouse performance budgets.

### Response

```json
{
  "lighthouseVersion": "12.x.x",
  "requestedUrl": "https://example.com",
  "categories": {
    "performance": { "score": 0.95 },
    "accessibility": { "score": 0.88 },
    "best-practices": { "score": 1.0 },
    "seo": { "score": 0.92 },
    "pwa": { "score": 0.6 }
  },
  "audits": {
    "first-contentful-paint": {
      "title": "First Contentful Paint",
      "score": 0.99,
      "displayValue": "0.8 s"
    },
    "largest-contentful-paint": {
      "title": "Largest Contentful Paint",
      "score": 0.85,
      "displayValue": "1.5 s"
    }
  }
}
```

Key response fields:
- `categories`: High-level scores (0-1) for each audit category.
- `audits`: Detailed results for individual audits, each with a `score` (0-1) and `displayValue` (human-readable metric).

**Note**: Audits can take 30 seconds to several minutes depending on site complexity. The full response can be 350-800kb.

## Execution

Use `curl` via Bash to make the request. Example:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/performance?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

To audit only specific categories:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/performance?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "config": {
      "extends": "lighthouse:default",
      "settings": {
        "onlyCategories": ["performance", "seo"]
      }
    }
  }'
```

Present the results in a readable format. Show category scores as percentages (multiply by 100). Highlight areas that score below 0.9 as needing attention. If the response is very large, summarize the key category scores and only show detailed audit results that the user is interested in.
