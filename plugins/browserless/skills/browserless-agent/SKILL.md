---
name: browserless-agent
description: >
  Drive a real cloud browser with Browserless to complete tasks that need
  interaction: clicking, typing, submitting forms, multi-step flows,
  logged-in pages, and checking how a site behaves. Use when reading a page
  is not enough. Triggers: "go to the site and", "fill in", "click",
  "sign in to", "test the checkout", "check what happens when".
---

# Browserless Agent

`browserless_agent` runs batches of browser commands (`goto`, `snapshot`,
`click`, `type` and more) in a cloud browser session that can stay open
between calls.

## When

- The task needs clicks, typing, form submission, or several steps on one
  site.
- The page only shows the content after interaction or sign-in.
- Do not use it for a plain page read; `browserless_smartscraper` is faster
  and cheaper.

## How

The tool's own description explains the full command loop. Follow it. In
short:

1. `goto` the page, then `snapshot` to see its elements and their refs.
2. Act only on refs from the latest snapshot, and take a fresh snapshot after
   anything that changes the page.
3. Set `keepSessionAlive: true` when you will need more than one call, and
   pass the returned `sessionId` on every follow-up.
4. Close the session with a `close` command when the task is finished, or
   tell the user it is still open and why.

For sites that need a login, check `browserless-profiles` first so the
browser can start signed in. `browserless_skill` loads extra guides for
common problems such as cookie banners, modals, tabs and file downloads.

When a step needs a person (a one-time code, a CAPTCHA, a payment
confirmation), stop and hand off as the tool's description explains. Do not
guess credentials or keep retrying.

## Done when

The task's end state is visible in a snapshot or read, the outcome is
reported, and the session is closed.
