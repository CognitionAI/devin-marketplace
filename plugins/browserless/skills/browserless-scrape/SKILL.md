---
name: browserless-scrape
description: >
  Read a single web page with Browserless Smart Scraper and get markdown,
  HTML, links, a screenshot, a PDF, a summary, or structured JSON that
  matches a schema. Use when the user gives a URL and wants its content or
  specific data from it. Triggers: "scrape this page", "get the text of",
  "pull the prices from", "screenshot this site", "extract into JSON".
---

# Browserless Smart Scraper

Fetch one URL and return its content. Smart Scraper tries a fast fetch first
and falls back to a full browser with bot-detection handling when the page
needs it, so it works on JavaScript-heavy and protected sites.

## When

- The user has a specific URL and wants its content or data from it.
- Do not use it for many pages of the same site (`browserless-crawl`) or for
  pages that need clicking, typing or a multi-step flow (`browserless-agent`).

## How

Call `browserless_smartscraper` with `url` and the `formats` you need:

- `markdown` (the default) for reading and summarizing.
- `json` with `jsonOptions` (a JSON `schema`, a `prompt`, or both) for
  structured data such as product lists or pricing tables.
- `summary` for a short AI-written summary.
- `links`, `html`, `rawText`, `screenshot` or `pdf` when the task needs them.

`json` and `summary` add a small AI extraction cost on top of the scrape, so
request them only when the user wants structured or summarized output.

Useful options:

- `onlyMainContent: true` drops navigation, footers and sidebars.
- `waitFor` (milliseconds, up to 30000) waits for late-loading content.
- `profile` replays a saved login (see `browserless-profiles`).

## Done when

The response has `ok: true` and the requested format is present. If it comes
back empty or blocked, retry once with `waitFor`, then switch to
`browserless-agent` to load and inspect the page interactively.
