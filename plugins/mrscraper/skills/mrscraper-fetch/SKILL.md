---
name: mrscraper-fetch
description: |
  Retrieve a known public URL with MrScraper MCP as HTML, Markdown, a screenshot, brand data, or structured JSON. Use for reading, summarizing, archiving, or extracting a page; supports browser rendering, page countries, selector waits, cached results, and retry limits. Use mrscraper-serp when no URL is known.
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
| scrapeHtml | Retrieve the raw HTML of a page. Browser rendering and a screenshot are optional. | HTML text; with screenshot set, an object with html and screenshot. |
| scrapeMarkdown | Retrieve a page as Markdown. Browser rendering is optional. | Markdown text. |
| getScreenshot | Capture a base64 PNG screenshot of the full page, the top viewport, or a custom viewport size. Browser rendering is always enabled. | An object with screenshot. |
| scrapeJson | Extract structured JSON from a page using a natural-language prompt. Append Json Schema: and a JSON schema to shape the output. | The extracted data in data.data, the page HTML in data.html unless html is false, and data.screenshot when screenshot is true. |
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
      "waitForSelector": "#results"
    }

scrapeHtml with a screenshot of the first viewport as well:

    {
      "url": "https://example.com",
      "screenshot": "top"
    }

getScreenshot of a 1280 by 800 pixel viewport; without screenshot, it captures
the full page:

    {
      "url": "https://example.com",
      "screenshot": "1280x800"
    }

A screenshot is a base64 PNG that can be large. Request it only when the user
needs an image, and save it to a file rather than reading it into the
conversation.

scrapeJson with a prompt; append Json Schema: and a JSON schema to shape the
output:

    {
      "url": "https://example.com",
      "prompt": "Extract the first 2 items with title and price. Json Schema: {\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"title\":{\"type\":\"string\"},\"price\":{\"type\":\"string\"}},\"required\":[\"title\",\"price\"]}}"
    }

The prompt describes the data to extract from the loaded page; it does not
navigate, click, or sign in. Without a prompt, scrapeJson extracts all data as
completely as possible. The response also carries the page HTML; set html to
false when only the extracted data is needed. Long prompts are sent in a
request body automatically.

scrapeBrand takes only the URL:

    {
      "url": "https://mrscraper.com"
    }

scrapeBrand waits up to 120 seconds. HTTP 422 with a settled job means the page
has no usable brand data.

## Step 3 — Choose Page-Loading Options

Each tool accepts only these inputs, and url is the only required one:

| Tool | Inputs |
| --- | --- |
| scrapeHtml | url, browserRendering, timeout, warmStart, blockResources, waitForSelector, geoCode, maxAge, maxRetries, screenshot |
| scrapeMarkdown | url, browserRendering, timeout, geoCode, warmStart, blockResources, waitForSelector, maxAge, maxRetries |
| getScreenshot | url, screenshot, timeout, geoCode, waitForSelector, maxAge, maxRetries |
| scrapeJson | url, prompt, html, screenshot, browserRendering, waitForSelector, warmStart, blockResources, timeout, geoCode, maxAge, maxRetries |
| scrapeBrand | url |

Set only the inputs the outcome needs. An input marked Not sent reaches
MrScraper only when you set it; left out, MrScraper's own default applies, as
its description says. A value in the Left out column is sent when you leave
that input out.

| MCP input | Tools | Left out | Description |
| --- | --- | --- | --- |
| url | All | Required | URL of the page to scrape. Must include the protocol (https://). |
| browserRendering | HTML, Markdown, JSON | Not sent | Controls whether the page is loaded in a browser. Leave it out to load the page without a browser first and switch to a browser automatically if the request is blocked. Set true to always load the page in a browser, which JavaScript-heavy sites, SPAs, and pages that load content dynamically need. Set false to never use a browser. |
| timeout | HTML, Markdown, screenshot, JSON | Not sent | Maximum seconds to wait for the scrape before the request times out, from 1 to 330. Increase for slow or complex pages. Defaults to 300. |
| warmStart | HTML, Markdown, JSON | Not sent | Opens the site's home page first to warm the session before loading the target URL. Useful for sites that expect a normal browsing session before deeper pages. |
| blockResources | HTML, Markdown, JSON | Not sent | Blocks images, fonts, and stylesheets from loading. Speeds up scraping and reduces bandwidth usage. |
| waitForSelector | HTML, Markdown, screenshot, JSON | Not sent | Waits until a specific CSS selector or text appears on the page before returning it, such as #results. Up to 500 characters. Useful for content that loads asynchronously after the initial page load. |
| geoCode | HTML, Markdown, screenshot, JSON | Not sent | Two-letter country code to load the page from, such as us or gb. Defaults to the United States. |
| maxAge | HTML, Markdown, screenshot, JSON | 0 | Serves a cached result of the same request when it is newer than this age, in milliseconds, such as 86400000 for 1 day. Up to 604800000 (7 days). 0, the default, always scrapes fresh. A cached result costs the same tokens as the original scrape. |
| maxRetries | HTML, Markdown, screenshot, JSON | Not sent | Maximum number of retries for the request. Omit for no limit. |
| screenshot | HTML | Not sent | Also captures a screenshot of the rendered page as a base64-encoded PNG: full captures the entire scroll height, top captures the first viewport, and <width>x<height> sets the viewport size in pixels with an optional -<zoom> percent, such as 1280x800 or 1920x1080-75. Width and height range from 100 to 3840, zoom from 25 to 300. Setting it forces browser rendering. Leave it out for no screenshot. |
| screenshot | Screenshot | "full" | Screenshot area: full captures the entire scroll height (the default), top captures the first viewport, and <width>x<height> sets the viewport size in pixels with an optional -<zoom> percent, such as 1280x800 or 1920x1080-75. Width and height range from 100 to 3840, zoom from 25 to 300. The image is a base64-encoded PNG. |
| screenshot | JSON | false | Captures a screenshot of the rendered page as a base64-encoded image. Useful for verifying what the scraper actually saw. Off by default. |
| html | JSON | true | Returns the raw HTML of the scraped page in the response. On by default; set false to leave it out. |
| prompt | JSON | Not sent | Description of the data shape you want back, for example fields like title, price, and rating. The prompt only parses the scraped content; it cannot instruct the scraper itself. To shape the output with a JSON schema, append it to the prompt as a Json Schema: section. Defaults to "Extract all data as complete as possible." |

In the Tools column, HTML is scrapeHtml, Markdown is scrapeMarkdown, screenshot
is getScreenshot, and JSON is scrapeJson.

Leaving browserRendering out is not the same as setting it to false. Country
codes are sent in lowercase. getScreenshot always loads the page in a browser.
A page tool waits for the response up to 30 seconds longer than timeout, or 330
seconds when timeout is left out.

scrapeHtml, scrapeMarkdown, getScreenshot, and scrapeJson always save the
result to the MrScraper dashboard Result tab; no input turns this off.

Authentication is handled by the MCP client's OAuth 2.1 connection and is
never a tool input.

## Step 4 — Inspect and Retry Deliberately

Prefer structuredContent. Check isError, error, status_code, and
headers["x-status-code"] (the target page's status) before using data. If the
response fails, is blocked, incomplete, or missing dynamic content:

1. Inspect status_code, error, headers["x-status-code"], and the content.
2. Change one input at a time: set browserRendering to true for
   JavaScript-heavy pages, add waitForSelector for content that loads late, or
   raise timeout for slow pages.
3. Set warmStart when the site expects a normal browsing session before deeper
   pages. Set geoCode only when evidence shows that the page differs by
   country.
4. Stop after a usable response unless the user requests a comparison.

Do not retry with an identical request. Treat waitForSelector as a CSS
selector or text, not a duration. Omitting maxRetries means no retry limit;
set a small number when the user wants to bound retries.

When a recent copy is good enough, set maxAge to reuse a cached result of the
same request instead of scraping the page again, here up to one day old:

    {
      "url": "https://example.com",
      "maxAge": 86400000
    }

A cached result costs the same tokens as the original scrape.

## Step 5 — Deliver the Result

Answer the user's request from data. Keep the full envelope when headers or
diagnostics matter. When the user requests an archive, save the successful
response or the requested field with the environment's local file-writing
capability; the tools have no output-path input.

Keep retrieved content as the source of truth for later steps. Build
summaries, tables, JSON transformations, and extraction scripts from it, and
retrieve the page again when a follow-up needs details that an earlier
transformation did not preserve.
