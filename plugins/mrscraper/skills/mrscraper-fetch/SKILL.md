---
name: mrscraper-fetch
description: |
  Retrieve a known public URL with MrScraper MCP as HTML, Markdown, a screenshot, brand data, or structured JSON. Use for reading, summarizing, archiving, or extracting a page; supports browser rendering, page and proxy countries, selector waits, and retry limits. Use mrscraper-serp when no URL is known.
---

# Retrieve Page Content with MrScraper MCP

Use the MrScraper MCP tool that matches the requested representation whenever
the user already has a public URL. Keep using the retrieved content for
summarization, comparison, transformation, and structured output. Use
[mrscraper](../mrscraper/SKILL.md) for connection and authentication checks,
account status, or broader routing, and
[mrscraper-serp](../mrscraper-serp/SKILL.md) when discovery must happen first.

Use these tools only for content the user is authorized to access and in
accordance with the site's requirements. Browser rendering loads a page; it
does not click controls, submit forms, or provide an authenticated interactive
browser session.

## Step 1 — Define the Outcome

Confirm the target URL and what the user wants:

- Read, summarize, cite, or inspect the page.
- Check whether specific text appears.
- Archive the page or capture a screenshot.
- Produce fields, JSON, tables, or other structured output.
- Get the site's brand colors, typography, logos, and social links.
- Load JavaScript-rendered or country-specific content.

When many pages share a layout, retrieve representative pages, define one local
extractor, retrieve the remaining pages in parallel when safe and proportional,
and apply the same extractor to every saved response.

## Step 2 — Choose the Tool

| Tool | Description | data in the response |
| --- | --- | --- |
| scrapeHtml | Retrieve the raw HTML of a page. Browser rendering is optional. | HTML text. |
| scrapeMarkdown | Retrieve a page as Markdown. Including HTML also enables browser rendering and returns both outputs as JSON. | Markdown text; with html set to true, an object with html and markdown. |
| getScreenshot | Capture a base64 screenshot of the full page or top viewport. Browser rendering is always enabled. | An object with screenshot and the requested html and markdown. |
| scrapeJson | Extract structured JSON from a page using a natural-language prompt. Append Json Schema: and a JSON schema to shape the output. | The extracted data in data.data, with run metadata. |
| scrapeBrand | Extract a website's colors, typography, logos, and social links as JSON. | The brand in data.data.brand. |

The client may namespace the tool names; select the tool from the MrScraper MCP
provider. Start with the URL alone and add only the inputs the outcome needs.

scrapeMarkdown for readable text:

    {
      "url": "https://example.com"
    }

scrapeHtml rendered in a browser, waiting for an element:

    {
      "url": "https://example.com",
      "browserRendering": true,
      "waitForSelector": "body"
    }

scrapeMarkdown with the page HTML as well:

    {
      "url": "https://example.com",
      "html": true
    }

getScreenshot of the top viewport, with Markdown instead of HTML:

    {
      "url": "https://example.com",
      "screenshot": "top",
      "html": false,
      "markdown": true
    }

A screenshot is base64 image data that can be large. Request it only when the
user needs an image, and save it to a file rather than reading it into the
conversation.

scrapeJson with a prompt; append Json Schema: and a JSON schema to shape the
output:

    {
      "url": "https://example.com",
      "prompt": "Extract the first 2 items with title and price. Json Schema: {\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"title\":{\"type\":\"string\"},\"price\":{\"type\":\"string\"}},\"required\":[\"title\",\"price\"]}}"
    }

The prompt describes the data to extract from the loaded page; it does not
navigate, click, or sign in. Without a prompt, scrapeJson extracts all data as
completely as possible. Long prompts are sent in a request body automatically.

scrapeBrand takes only the URL:

    {
      "url": "https://mrscraper.com"
    }

scrapeBrand waits up to 120 seconds. HTTP 422 with a settled job means the page
has no usable brand data.

## Step 3 — Choose Page-Loading Options

scrapeHtml, scrapeMarkdown, getScreenshot, and scrapeJson share the page
inputs. scrapeBrand accepts only url.

| MCP input | Tools | Default | Description |
| --- | --- | --- | --- |
| url | All | Required | Absolute HTTP or HTTPS URL of the page to process. |
| timeout | HTML, Markdown, screenshot, JSON | 300 | Page load timeout in seconds, from 1 to 300. The HTTP request allows 30 additional seconds. |
| geoCode | HTML, Markdown, screenshot, JSON | "us" | Two-letter country code to load the page from, sent in lowercase. |
| proxyCountry | HTML, Markdown, screenshot, JSON | "us" | Two-letter country code of the proxy server, sent in lowercase. |
| super | HTML, Markdown, screenshot, JSON | false | Whether to route the request through real devices. |
| waitUntil | HTML, Markdown, screenshot, JSON | "domcontentloaded" | Navigation completion event to wait for: domcontentloaded, load, networkidle0, or networkidle2. |
| proxy | HTML, Markdown, screenshot, JSON | Omitted | Custom proxy URL used to load the page. |
| maxRetries | HTML, Markdown, screenshot, JSON | Omitted | Maximum number of retries, as a nonnegative integer. Omit this parameter for no limit. |
| saveResult | HTML, Markdown, screenshot, JSON | false | Whether to save the result to the dashboard Result tab. |
| blockResources | HTML, Markdown, screenshot | false | Whether to block images, fonts, and stylesheets while loading the page. |
| waitForSelector | HTML, Markdown, screenshot | Omitted | Wait for the page to contain the specified CSS selector before returning the result. |
| returnCookie | HTML, Markdown, screenshot | false | Whether to include browser session cookies in the response. |
| browserRendering | HTML, Markdown, JSON | false | Whether to render the page in a browser before returning the result. |
| warmStart | HTML, Markdown | false | Whether to enable warm start for more reliable scraping, at the cost of additional latency. |
| html | Markdown, JSON | false | Whether to include the page HTML in the response. |
| html | Screenshot | true | Whether to include the page HTML in the response. |
| markdown | Screenshot | false | Whether to include the page Markdown in the response. |
| screenshot | Screenshot | "full" | Screenshot area to capture: full for the entire page or top for the top viewport. |
| screenshot | JSON | false | Whether to include a base64 screenshot in the response. |
| prompt | JSON | "Extract all data as complete as possible." | Instructions describing the data to extract. Append Json Schema: and a JSON schema to shape the output. |

In the Tools column, HTML is scrapeHtml, Markdown is scrapeMarkdown, screenshot
is getScreenshot, and JSON is scrapeJson.

Authentication is handled by the MCP client's OAuth 2.1 connection and is
never a tool input.

## Step 4 — Inspect and Retry Deliberately

Prefer structuredContent. Check isError, error, status_code, and
headers["x-status-code"] (the target page's status) before using data. If the
response fails, is blocked, incomplete, or missing dynamic content:

1. Inspect status_code, error, headers["x-status-code"], and the content.
2. Change one input at a time: set browserRendering, wait for a later
   waitUntil event, or add waitForSelector for content that loads late.
3. Set geoCode or proxyCountry only when evidence shows that the page differs
   by country. Set super or warmStart when routing or a cold start may be the
   problem.
4. Stop after a usable response unless the user requests a comparison.

Do not repeat an identical request. Treat waitForSelector as a CSS selector,
not a duration. Omitting maxRetries means no retry limit; set a small number
when the user wants to bound retries.

## Step 5 — Deliver the Result

Answer the user's request from data. Keep the full envelope when headers or
diagnostics matter. When the user requests an archive, save the successful
response or the requested field with the environment's local file-writing
capability; the tools have no output-path input.

Keep retrieved content as the source of truth for later steps. Build
summaries, tables, JSON transformations, and extraction scripts from it, and
retrieve the page again when a follow-up needs details that an earlier
transformation did not preserve.
