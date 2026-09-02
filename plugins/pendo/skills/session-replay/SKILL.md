---
name: session-replay
description: Find and surface relevant session replays for debugging, UX research, and understanding user behavior. Use this skill whenever someone asks about session replays, wants to watch how users interact with their product, needs to debug a user issue by seeing what happened, or wants to find sessions with frustration signals like rage clicks or errors. Also trigger when users mention watching recordings, finding replays for a specific visitor or page, investigating UX problems, or looking for sessions with high activity — even if they don't say "session replay" explicitly.
---

# Session Replay Finder

Find relevant session replays to debug issues, conduct UX research, or understand how users interact with your product. Session replays are recordings of real user sessions that show exactly what a visitor saw and did.

## Parameters

- **visitor_id**: Optional — find sessions for a specific visitor.
- **account_id**: Optional — find sessions for a specific account.
- **page_name**: Optional — find sessions involving a specific page.
- **timeframe**: The time period to search (default: last 7 days, max: 31 days).
- **min_duration**: Minimum session duration in minutes (default: 2 minutes).
- **min_activity**: Minimum activity percentage (default: 5%).

## Step 0: Determine Subscription and App Context

Before querying, you need the subscription ID. Use `list_all_applications` to get available subscriptions and apps. If there's only one subscription, use it. If there are multiple, ask the user which one to use.

Store the `subId` for all subsequent calls.

## Step 1: Clarify Search Criteria

Understand what the user is looking for. Common scenarios:

- **Specific visitor sessions** — the user provides a visitor ID or name.
- **Sessions on a particular page** — the user names a page or feature.
- **Sessions with frustration signals** — the user wants to find rage clicks, errors, dead clicks, or u-turns.
- **High-activity sessions for UX research** — the user wants to see engaged sessions.
- **Account-level sessions** — the user wants to see sessions from a specific account.

### Resolving page or feature names

If the user provides a page or feature name (not an ID), resolve it first using `searchEntities`:

- Use `itemType: ["Page"]` (or `["Feature"]`) with the user's search term.
- If multiple results match, present them and ask the user to pick — just like in the account-health skill. Show the page/feature name, ID, and any description to help disambiguate.
- Once confirmed, use the `pageId` in the session replay query.

### Resolving account names

If the user provides an account name, use `searchEntities` with `itemType: ["Account"]` to find the account ID. Follow the same disambiguation pattern as the account-health skill — present matches with a ⭐ Recommended tag based on activity signals, and confirm before proceeding.

## Step 2: Find Session Replays

Use `sessionReplayList` to find matching recordings.

**Query parameters:**

- **startDate / endDate**: Based on the user's timeframe. Default to the last 7 days. Maximum range is 31 days — if the user asks for more, let them know and cap at 31. Both dates are inclusive, so "last 7 days" means endDate = today and startDate = today minus 6 days (not 7). For the maximum 31-day window, use today minus 30 days as the start. Getting this off by one will cause an API error.
- **visitorId**: If searching for a specific visitor.
- **accountId**: If searching for a specific account.
- **pageId**: If searching for sessions on a specific page (resolved in Step 1).
- **minDuration**: Convert the user's minutes to milliseconds. Default is 120000ms (2 minutes).
- **minActivityPercentage**: Filter out low-activity sessions. Default is 5%.

If the user hasn't specified filters, use the defaults (last 7 days, 2 min duration, 5% activity) and let them know what defaults you're using so they can adjust.

### Handling empty results

If the initial query returns no sessions, don't just report "no results found" — try to help:

1. **Widen the date range.** If you started with 7 days, automatically retry with 31 days (the maximum) and let the user know you expanded the window.
2. **Relax filters.** If you used a page or feature filter and got nothing, try dropping it and searching broadly, then mention that no sessions matched the specific page but here are recent sessions from the account/visitor.
3. **Lower thresholds.** If duration or activity filters are high, try reducing them.

Only report "no sessions found" after you've exhausted these fallbacks. When you do widen the search, always tell the user what you changed so they understand the results.

## Step 3: Enrich Results with Context

For the top results returned, gather additional context to make the replays more actionable:

**Tools**: `visitorQuery`, `accountQuery`

- Look up visitor metadata (name, email, account) for the visitors in the top sessions.
- Look up account information if account IDs are present in the results.
- Note frustration events from the replay metadata — the session replay results include counts of rage clicks, dead clicks, error clicks, and u-turns.

This enrichment helps the user quickly identify which sessions are worth watching without having to open each one.

## Step 4: Rank and Present Results

Prioritize sessions based on the user's intent. The default ranking favors actionable sessions:

1. **Frustration signals** — sessions with rage clicks, dead clicks, u-turns, or error clicks bubble up first. These are the most likely to reveal real problems.
2. **Activity percentage** — higher activity means the user was actively engaged (not idle).
3. **Duration** — longer sessions may provide more context for debugging.
4. **Recency** — more recent sessions are generally more relevant.

If the user is doing UX research (rather than debugging), weight activity percentage and duration more heavily than frustration signals.

## Output Format

Present session replays in a clear, scannable format:

```
## Session Replays Found

**Search Criteria**: {criteria_summary}
**Period**: {start_date} to {end_date}
**Results**: {count} sessions found

### Top Sessions

| # | Visitor | Account | Duration | Activity | Frustration Signals | Link |
|---|---------|---------|----------|----------|---------------------|------|
| 1 | {name_or_id} | {account} | {duration} | {activity}% | {signals} | [Watch]({url}) |
| 2 | ... | ... | ... | ... | ... | ... |

### Frustration Summary

- **Rage Clicks**: {total} across {n} sessions
- **Dead Clicks**: {total} across {n} sessions
- **Error Clicks**: {total} across {n} sessions
- **U-Turns**: {total} across {n} sessions

### Recommended Sessions to Review

1. **{reason}**: [Watch Session]({url})
   - Visitor: {name}, Duration: {duration}, {frustration_details}

2. **{reason}**: [Watch Session]({url})
   - Visitor: {name}, Duration: {duration}, {frustration_details}
```

Adapt the output to what's relevant. If there are no frustration signals, skip the Frustration Summary section rather than showing all zeros. If only a few sessions are found, skip the "Top Sessions" table and just present them as the recommended list.

The "Recommended Sessions to Review" section is the most important part — give each recommendation a short reason explaining why this session is worth watching (e.g., "Highest rage click count", "Long session on checkout page with errors", "Most active visitor from this account").

## Rules

- **Maximum date range is 31 days.** If the user asks for more, explain the limit and default to 31 days.
- **Default to last 7 days** if no timeframe is specified.
- **Always include the direct URL** to watch each session. This is the most actionable piece of information.
- **Highlight frustration signals prominently.** Sessions with rage clicks, dead clicks, error clicks, or u-turns are almost always the most interesting to review.
- **Filter out noise by default.** The 2-minute minimum duration and 5% activity floor prevent very short or idle sessions from cluttering results. Let the user know these defaults and offer to adjust.
- **Resolve names to IDs first.** If the user provides a page name, feature name, or account name, use `searchEntities` to get the ID before querying replays. Confirm with the user if there are multiple matches.
- **Present the most actionable sessions first.** Don't just dump 50 sessions — curate and explain why the top picks matter.
- **Handle large result sets gracefully.** The API can return up to 50 sessions. If you get close to that cap, let the user know there are likely more sessions matching their criteria and suggest narrowing filters (shorter date range, specific page, specific account, higher activity threshold) to find more targeted results. Always present only the top 5–10 most relevant sessions in the table regardless of how many come back.
- **Keep it concise outside the results.** Let the session data speak for itself. Don't over-explain what session replay is or how it works unless the user seems unfamiliar.
