---
name: browserless
description: >
  Pick the right Browserless tool for live-web work: reading pages, searching,
  mapping or crawling sites, and driving a real browser. Use whenever a task
  needs current content from the web, especially sites that render with
  JavaScript, block bots, or need a login, even when the user does not
  mention Browserless. Triggers: "scrape", "read this page", "look up",
  "check the site", "crawl", "log in to", "fill in the form on".
---

# Browserless

Browserless runs real Chrome browsers in the cloud. The tools handle
JavaScript rendering and bot detection, so prefer them over plain HTTP
fetching for any page that might be dynamic or protected.

## Choose a tool

| Need | Tool | Skill |
|------|------|-------|
| Find pages on a topic, no URL yet | `browserless_search` | this one |
| Read one known URL as markdown, HTML, links, a screenshot, a PDF or extracted JSON | `browserless_smartscraper` | `browserless-scrape` |
| List the URLs on a site | `browserless_map` | `browserless-crawl` |
| Content from many pages of a site | `browserless_crawl` | `browserless-crawl` |
| Click, type, submit forms, follow multi-step flows | `browserless_agent` | `browserless-agent` |
| Start signed in to a site | `browserless_profiles`, then `profile` on another tool | `browserless-profiles` |

Start with the cheapest tool that can answer the request: search, then
scrape, then map or crawl, and drive the browser with `browserless_agent` only
when the page needs interaction or session state.

## Search

Call `browserless_search` with a short `query`. Narrow it with `sources`
(`web`, `news`, `images`), `categories` (`github`, `research`, `pdf`), `tbs`
for recency (`day`, `week`, `month`, `year`) and `limit`. Add `scrapeOptions`
only when the snippets are not enough; otherwise scrape the best URLs
afterwards. Cite the source URLs in your answer.

## Rules

- Tool names may appear with a prefix in your tool list; call whichever
  `browserless_*` name is available.
- Sign-in is handled by OAuth when the server is connected. Never ask the
  user to paste an API token into the chat.
- Use the tools only for content the user is allowed to access.
