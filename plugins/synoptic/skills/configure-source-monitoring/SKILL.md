---
name: configure-source-monitoring
description: Configure supported Synoptic source monitors and custom scraper targets for Twitter/X accounts, keywords, hashtags, cashtags, queries, follows or profile changes, Telegram channels, and GitHub repositories. Use when the user wants ongoing collection or a change to monitored sources.
---

# Configure source monitoring

Set up monitoring with existing Synoptic feeds and their supported target configuration. Creating a publishing stream does not set up a scraper. Coverage, target formats, update speed, delays, and account limits vary by feed.

## Select the monitor and targets

Find candidate feeds with `search`, then inspect them with `get_stream`. A Twitter/X feed for account posts, search queries, follows/unfollows, or profile changes does not cover the others. Telegram channels and GitHub repository activity need their matching provider feed. For news, filings, government releases, and other event feeds, use the source families in the read-streams skill.

For a configurable feed, read `customTargetsData.targetType`, `targetTypeInstruction`, `targetValidationRegex`, and the target-count limits. Use the target syntax and case the feed requires. Handles, numeric account IDs, channel URLs, repository paths, keywords, hashtags, cashtags, and full search expressions are not interchangeable. There is no identity lookup tool; do not infer a numeric ID from a display name. Get a missing identifier from the user or a verified source before writing. A regex match validates syntax, not identity or source availability.

If an existing feed covers the request without custom targets, follow it when the user's setup request authorizes that. If no suitable configurable feed exists, explain what is missing. If the user asks to send a custom stream request, use the request-stream-or-feature skill; a submitted request is not an active monitor.

## Save the selection

Check existing follows with `streams_following`. If the user asked to monitor an eligible stream they do not follow, call `follow_stream` before reading its target selection. Then read current targets with `get_stream_custom_targets`. Followers get their own selection; owners get the union of all followers' targets, which must not be copied as a personal selection. Report entitlement or target-limit errors; do not substitute a different monitor.

Changing targets requires a direct subscription to the stream with a target allowance. A follow, package access, or organization access is not enough. With `subscriptions.read`, `get_stream_subscription` shows the direct subscription and its target allowance. If the entitlement is missing, explain what to set up in Synoptic; these tools cannot purchase it.

Use `patch_stream_custom_targets` with `add` or `remove` for a narrow change. `set_stream_custom_targets` replaces the whole selection; an empty list clears it. Preserve unrelated targets. Posts for removed targets stop reaching the user; open Synoptic app feeds apply the change after they reconnect. Removed targets are then removed from the user's collection sources limited to specific targets; such a source left with no targets is deleted. `get_stream_custom_targets` needs `streams.read`; `set_stream_custom_targets` needs `following.write` and `workspace.write`; `patch_stream_custom_targets` also needs `following.read`.

Use the manage-workspace skill to combine feeds in dashboards and apply include/exclude keywords, regex, or AI filters. Collection filters change which posts appear in a collection, not the scraper's targets.

## Report what is established

Confirm saved targets from the tool result, and use `get_stream_posts` to check recent updates when relevant. Report the stage reached: feed found, access obtained, targets saved, collection configured, or matching posts observed. An empty history page does not prove failure, and old matching posts do not prove the new targets are collecting. No tool reports scraper health.

For delivery into another application, use the connect-feed-to-app skill. Reading posts in this conversation does not start a background watch or keep an external consumer connected.
