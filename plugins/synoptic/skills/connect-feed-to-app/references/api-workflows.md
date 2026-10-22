# Synoptic API workflows

Use the linked guide for each operation's full schema.

## History and post lookup

Use base URL `https://api.synoptic.com` with the appropriate key in `x-api-key`:

- `GET /v1/streams/{streamId}` for metadata and API access details.
- `GET /v1/streams/{streamId}/posts` for bounded history; `limit` is at most 50 and `nextToken` continues the list.
- `GET /v1/streams/{streamId}/posts/search` for post-text search with `offset` pagination.
- `GET /v1/streams/{streamId}/post/{postId}` for one post.

History, search, and enterprise-history endpoints are each limited to one request per second. On HTTP 429, wait at least one second and add jitter. Prefer WebSocket for ongoing updates. See the [REST reference](https://docs.synoptic.com/s/rest/api-reference).

## Realtime post delivery

Connect to `wss://ws.api.synoptic.com/v1/on-stream-post` with a reader key in the `x-api-key` upgrade header (preferred when the client can set it) or the `apiKey` query parameter. The `streamIds` query parameter takes comma-separated stream IDs; without it, every stream the key can access is included. The optional `lastPosts` query parameter sends at most 50 recent posts in total, not 50 per stream.

Handle `sub_ack`, `stream.post.created`, `stream.post.last-posts`, `info`, and `keep-alive` frames. Post events use `{ "event": "...", "data": { ... } }`. `lastPosts` is a small catch-up window, not a replay of an arbitrary outage; fill larger gaps from REST history. A restart notice gives about 30 seconds to replace the connection.

Custom streams deliver only posts for the follower's selected targets; with no selected targets, no targeted posts arrive. See [subscriptions](https://docs.synoptic.com/s/websocket/subscribe-to-posts), [events](https://docs.synoptic.com/s/websocket/events), and [custom streams](https://docs.synoptic.com/s/integrations/custom-streams).

## Publishing stream posts

Use a publisher key with `wss://ws.api.synoptic.com/v1/add-stream-post`. Send an `add-stream-post` event with `data` containing `streamId`, Markdown `content`, and a stable `idempotencyKey` for that logical publication. Optional fields include `metadata`, `vendorMetadata`, and `releaseAt`. `customTarget` is required for custom streams and must be omitted for regular streams. An accepted publish returns `stream.post.created`.

The REST equivalent is `POST /v1/streams/{streamId}/post`, which uses its own create-post schema, not the WebSocket envelope. Reuse the idempotency key when retrying the same publication; deduplication covers a bounded window, not permanent exactly-once delivery. See [publishing](https://docs.synoptic.com/s/websocket/publish-posts) and the [REST schema](https://docs.synoptic.com/s/rest/api-reference).

## Structured source payloads

Connect to `wss://ws.api.synoptic.com/v1/source-post` with a source key in the `x-api-key` upgrade header; query-string authentication is not accepted. The `connected` frame lists authorized `sourceId` values, `schemaVersion`, and `hasSchema`, but not the JSON Schema itself. Take the schema from the source configuration; do not invent one.

Send a flat `{ "sourceId": "...", "data": { ... }, "idempotencyKey": "..." }` object, without an `event` wrapper. `data` must match the source's JSON Schema; when `hasSchema` is false, no validation runs. The response contains `sourceId`, `valid`, and `errors`. Invalid payloads are stored for auditing but not routed downstream. A validation acknowledgement does not prove subscriber delivery.

Reconnect on `4010 source-schema-updated` or `4011 source-routes-updated`. Resolve the authentication or authorization failure before retrying after `4001` or `4003`. The MCP tools cannot create sources, edit schemas, or set up downstream routes; use the existing source configuration or the Synoptic UI. See [source posts](https://docs.synoptic.com/s/websocket/add-source-posts).

## Numeric data

For labelled metrics, use a configured series and `wss://ws.api.synoptic.com/v1/time-series` with a time-series publisher key in `x-api-key`. Wait for `connected`, then send flat objects with `seriesId`, optional default `labels`, and `points`. A response with `ok: true` and `written` confirms the write. Readers use `on-time-series` with a `subscribe` action and receive `time_series.snapshot` and `time_series.points`; an HTTP latest-values endpoint also exists. See [time series](https://docs.synoptic.com/s/websocket/time-series) for limits and label rules.

## Enrichments

Source-routed posts may contain `enrichments`; publisher posts are not automatically enriched. An absent enrichment key differs from a present empty array. `metadata.tickers` comes from source data; `enrichments.tickers` is computed. Do not send `enrichments` when publishing, and do not treat a match as proof of an event or market outcome. See [enrichments](https://docs.synoptic.com/s/integrations/enrichments).
