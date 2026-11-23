---
name: browserless-profiles
description: >
  Reuse saved Browserless login profiles so the browser starts already
  signed in to a site, and create one when none exists. Use before any task
  on a site that needs a login. Triggers: "logged in", "my account on",
  "behind the login", "use my saved session", "sign in once and reuse".
---

# Browserless Profiles

A profile is a saved, signed-in browser state (cookies and storage) for the
user's Browserless account. Passing a profile's name as `profile` to
`browserless_agent`, `browserless_smartscraper` or `browserless_crawl` starts
that tool already signed in.

## When

- Any task on a site that needs the user to be signed in.
- Check for an existing profile before asking the user to log in again.

## How

1. Call `browserless_profiles` to list the saved profiles. Each one shows its
   name, how many cookies and sites it covers, and when it was last used.
2. If one matches the site, pass its name as `profile` to the tool you are
   using.
3. If none matches, load the `auth-profile` guide with `browserless_skill`
   and follow it to create a profile in a `browserless_agent` session. The
   user signs in once in a live browser view, and the profile is saved for
   future runs.

## Rules

- Never ask the user to type a password into the chat. Sign-in happens in the
  live browser view.
- If a saved profile has expired and the site shows a login wall, tell the
  user and offer to create a fresh profile.
