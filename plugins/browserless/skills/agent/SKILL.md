---
name: agent
description: Drive an interactive browser session — navigate, snapshot the page, click, type, scroll, handle logins, captchas, cookie banners, and multi-step automation that keeps state across steps. Use when a task needs more than a one-shot scrape/screenshot/pdf, e.g. logging in, filling multi-page forms, downloading files behind a flow, or exploring a site step by step.
---

# Browser Agent

This skill is backed by the **Browserless MCP server** (bundled with this plugin via `.mcp.json`), not a one-shot REST call. It holds a live browser session, so use it when the task is interactive or multi-step. For single-shot work prefer `/browserless:smart-scrape` (scrape, screenshot, pdf, links) instead.

## How to run it

Call the `browserless_agent` MCP tool. It connects to a real Chromium session at `https://mcp.browserless.io` and returns a page **snapshot** (accessibility tree + element refs) after each step. Drive it by issuing commands against those refs.

Typical loop:

1. `navigate` to the starting URL → read the returned snapshot.
2. Act on elements by ref: `click`, `type`, `select`, `scroll`, `press`.
3. Re-read the snapshot, repeat until the goal is reached.
4. Extract the result (text, a screenshot, or a downloaded file).

The agent handles the hard parts automatically — cookie consent, captchas, login flows, shadow DOM, modals, tabs, and file up/downloads. Let it; don't hand-roll those.

## When to use which

| Task | Use |
|------|-----|
| Read / extract one page | `/browserless:smart-scrape` |
| Screenshot or PDF one page | `/browserless:smart-scrape` (formats) |
| Search the web | `/browserless:search` |
| List/crawl a site's URLs | `/browserless:map`, `/browserless:crawl` |
| Run a fixed Puppeteer script | `/browserless:function` |
| **Log in, click through, fill forms, multi-step, stateful** | **`browserless_agent` (this skill)** |

## Auth

Same credentials as the rest of the plugin: `BROWSERLESS_TOKEN` (env var or `/browserless:auth`). With no token, the hosted endpoint falls back to OAuth sign-in.

If the `browserless_agent` tool isn't listed, the MCP server isn't connected — run `/mcp` to check, and ensure the plugin's `.mcp.json` is loaded.
