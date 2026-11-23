---
name: browserless-crawl
description: >
  Map a website's URLs or crawl many of its pages with Browserless. Use when
  the user wants every page in a site or section, a list of a site's URLs,
  or content gathered across a documentation site, blog or catalog.
  Triggers: "crawl", "all pages on", "map the site", "list the URLs",
  "get every doc page".
---

# Browserless Map and Crawl

Two tools for working with a whole site:

- `browserless_map` lists URLs quickly from sitemaps and links, without
  scraping them.
- `browserless_crawl` follows links from a seed URL and scrapes each page it
  finds.

## When

- Map first when the user needs to find the right pages, or when you are not
  sure how big a site is.
- Crawl when the user needs the content of many pages.
- For one page, use `browserless-scrape` instead.

## Map

Call `browserless_map` with `url`. Pass `search` to rank the URLs by
relevance to a topic, and `limit` to cap the list. `sitemap` controls
sitemap use (`include`, `skip`, `only`), and `includeSubdomains` and
`ignoreQueryParameters` tune which URLs come back. Then scrape the few pages
that matter, or crawl a section.

## Crawl

Call `browserless_crawl` with `url` and keep it bounded:

- `limit` caps the number of pages, and `maxDepth` caps how many links deep
  it follows from the seed.
- `includePaths` and `excludePaths` take regex patterns for URL paths, for
  example `^/docs/`.
- `scrapeOptions` picks the output formats (`markdown`, `html`, `rawText`)
  and can set `onlyMainContent`.

Large crawls take time. Set `waitForCompletion: false` to get a crawl ID back
straight away instead of waiting for every page.

## Done when

The crawl reports a finished status and the pages the user needs are in the
results. Summarize or quote from them; do not paste every page back.
