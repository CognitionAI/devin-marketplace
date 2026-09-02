---
name: wisdom-slack-digest
description: >
  This skill should be used when the user asks to "run my feedback digest,"
  "post a Wisdom summary to Slack," "generate a weekly feedback report,"
  "create a customer intelligence digest," "send a feedback digest," "deliver
  a scheduled feedback report," "run the digest," "post this week's feedback,"
  or any request involving pulling themed feedback from Wisdom and delivering
  it to a channel. Also triggers on "run /digest" or "execute the digest."
version: 2.0.0
---

# Wisdom Slack Digest — Execution Guide

Generate a structured customer feedback digest from Enterpret's Wisdom Knowledge
Graph and deliver it to the user's configured channel. Built for both ad-hoc
execution and recurring scheduled delivery via CoWork.

## Prerequisites

- **Enterpret Wisdom** (`enterpret-wisdom-mcp`) — the Knowledge Graph server (required)
- **Delivery channel** — Slack, email, or other MCP-based connector (optional; CoWork is always available)

Validate Wisdom access before executing. If the configured delivery channel's MCP
is unavailable, fall back to displaying the digest in chat and inform the user.

## Execution Flow

### Step 1: Load configuration

Read `context/digest-config.md` (in the plugin root). Parse the YAML blocks to extract:

- **digest_title** — header for the digest
- **delivery** — channel type (slack, email, cowork) and destination (channel ID, address, etc.)
- **topics** — list of keyword themes, each with name, keywords, and description
- **breakdowns** — dimensions to slice by (if any)
- **display settings** — max_quotes_per_topic, max_quote_length, show_sentiment, show_source

If `context/digest-config.md` does not exist, tell the user to run `/digest` to
set one up. Stop execution.

### Step 2: Validate access

**Wisdom MCP:** Call `get_organization_details`. If it fails, stop with auth error.

**Delivery channel:** Check for the configured delivery MCP's tools.
- If available, proceed normally.
- If unavailable, switch to CoWork mode (display in chat) and note: "Configured
  delivery channel ({type}) is not connected. Showing digest in chat instead."

### Step 3: Query for each topic

For each topic in the config, build and run a Cypher query. Use the `wisdom-kg`
skill's query rules (LIMIT, count syntax, date formatting).

**Topic query — theme-level granularity:**

Use `search_knowledge_graph` first to resolve topic keywords to actual theme names.
Then query at the theme level:

```cypher
MATCH (t:Theme)<-[:HAS_THEME]-(cft:CustomerFeedbackTags)<-[:HAS_TAGS]-(fi:FeedbackInsight)
  -[:HAS_SENTIMENT]->(sp:SentimentPrediction),
  (fi)<-[:SUMMARIZED_BY]-(nli:NaturalLanguageInteraction)
WHERE t.name CONTAINS '{theme_name}'
  AND nli.record_timestamp >= "{start_date}"
RETURN
  t.name AS theme,
  sp.label AS sentiment,
  nli.content AS verbatim,
  nli.source AS source,
  fi.feedback_record_id AS record_id,
  nli.record_timestamp AS timestamp
LIMIT 50
```

**With breakdowns** — add OPTIONAL MATCH for DerivedAccount:

```cypher
MATCH (t:Theme)<-[:HAS_THEME]-(cft:CustomerFeedbackTags)<-[:HAS_TAGS]-(fi:FeedbackInsight)
  -[:HAS_SENTIMENT]->(sp:SentimentPrediction),
  (fi)<-[:SUMMARIZED_BY]-(nli:NaturalLanguageInteraction)
OPTIONAL MATCH (nli)-[:HAS_ACCOUNT]->(da:DerivedAccount)
WHERE t.name CONTAINS '{theme_name}'
  AND nli.record_timestamp >= "{start_date}"
RETURN
  t.name AS theme,
  sp.label AS sentiment,
  nli.content AS verbatim,
  nli.source AS source,
  da.name AS account_name,
  fi.feedback_record_id AS record_id,
  {breakdown_properties}
LIMIT 50
```

**Critical rules:**
- Use `OPTIONAL MATCH` for Account joins — many records lack account links
- Use `HAS_ACCOUNT` → `DerivedAccount` (not `PROVIDED_BY_ACCOUNT` → `Account`)
- Run one query per topic; OR multiple keywords within each topic
- For case-insensitive matching: `toLower(t.name) CONTAINS toLower('{keyword}')`

**Breakdown property mapping:**

| Breakdown | Node | Property |
|-----------|------|----------|
| geo/region | DerivedAccount | `salesforce_account_region_c` |
| segment | DerivedAccount | `salesforce_account_segment_c` |
| customer_stage | DerivedAccount | `salesforce_customer_stage_c` |
| opp_stage | NLI | `gong_account_opportunity_stagename` |

If configured properties don't exist, call `get_schema` to verify before querying.

### Step 4: Synthesize results

For each topic, produce these elements (in priority order):

1. **Insight headline** — A single bold sentence that tells the reader what's
   happening and why it matters. This is the most important output. It should be
   specific ("Editor redesign is driving 636 negative reports — 10x last month's
   baseline") not generic ("Customers have mixed feedback about the editor").
2. **Severity signal** — Classify as: :red_circle: Needs attention, :large_orange_circle: Monitor,
   or :green_circle: Healthy. Base this on volume, sentiment ratio, and trend direction.
3. **The sharpest quote** — ONE customer verbatim that crystallizes the issue.
   Select for specificity and emotional clarity, not length. From `nli.content`
   (customer words, NOT AI summaries from `fi.content`).
4. **Suggested action** — One concrete next step. "Investigate X," "Prioritize Y,"
   "Share with Z team." This makes the digest actionable, not just informational.
5. **Supporting numbers** — Volume, sentiment ratio as percentage, top source.
   These support the insight, not lead it.

If a topic returns zero results: "No feedback matching this topic in the current
period — this may indicate a data gap or a genuinely quiet area."

Read the `evidence-synthesis` skill for guidance on selecting quotes and writing
insight headlines.

### Step 5: Format the digest

The digest uses a **three-tier architecture** optimized for how people actually
read Slack: scan the channel, click into what's interesting, dig into detail
only when needed.

**Design principles:**
- Lead with insight, support with evidence, end with action
- Whitespace is a feature — dense text gets skipped
- One strong quote beats five mediocre ones
- Numbers need context ("636 negative" means nothing; "18% negative, up from 4%" lands)
- Source names are implementation detail — don't lead with them

#### Tier 1: Channel Message (the headline)

This appears in the Slack channel. A busy person should understand the key
signals in 10 seconds without clicking anything. **Under 600 characters.**

```
:star: *{digest_title} — {today's date}*
_{total_volume} feedback items · {source_count} sources · last {period}_

{severity_emoji} *{Topic 1 name}* — {insight_headline}
{severity_emoji} *{Topic 2 name}* — {insight_headline}
{severity_emoji} *{Topic 3 name}* — {insight_headline}

:thread: _Details in thread_
```

**Example:**

```
:star: *Canva Create 2026 — Product Change Reactions — April 10, 2026*
_~600 feedback items · 15 sources · last 30 days_

:red_circle: *Editor Redesign Backlash* — 700+ reports, 18% negative. Users can't find moved tools and are reverting to old workflows.
:large_orange_circle: *Styles & Layout Panel Confusion* — Zendesk tickets 3x normal. Users report the panel "simply doesn't appear" after cache clears.
:green_circle: *Templates Sentiment* — Mostly positive across App Store and surveys. Surface friction with post-redesign finishability.

:thread: _Details in thread_
```

Severity emoji guide:
- :red_circle: = high negative ratio (>15%), spiking volume, or enterprise blocker
- :large_orange_circle: = moderate signal, worth monitoring, or mixed sentiment
- :green_circle: = healthy or improving, no immediate action needed

#### Tier 2: Thread — Topic Cards (one reply per topic)

Each topic gets its own threaded reply. Structure: **insight first, evidence
second, action last.** Use whitespace generously between sections.

```
{severity_emoji} *{Topic name}*

*What's happening:*
{2-3 sentence editorial narrative. Name the specific pattern, who's affected,
and what changed. This is analysis, not data recitation.}

*Signal strength:*
{volume} reports · {neg_pct}% negative · Top channel: {source_name}

*Sharpest customer quote:*
> _{verbatim — the one quote that best captures this issue}_

{If breakdowns configured:}

*By {breakdown_name}:*
• {value_1}: {volume} reports ({neg_pct}% neg) — {one-line note}
• {value_2}: {volume} reports ({neg_pct}% neg) — {one-line note}

*Suggested action:*
:point_right: {One concrete, specific next step}

───────────────
```

**Example:**

```
:red_circle: *Editor Redesign Backlash*

*What's happening:*
The move of Styles from the left sidebar to the right edit panel is generating
sustained negative feedback. Users report the panel "simply doesn't appear" after
cache clears, browser switches, and support guidance. This is a discoverability
problem, not a bug — but it's driving significant Zendesk volume.

*Signal strength:*
700+ reports · 18% negative · Top channel: Zendesk Support (155 tickets)

*Sharpest customer quote:*
> _"this new layout is way too hard to navigate. the old lay out was perfect,
> maybe we could have the option to switch to this layout of image editing
> tools if we choose?"_

*Suggested action:*
:point_right: Investigate adding a "Styles" shortcut or tooltip to the left sidebar
to bridge the discoverability gap. 155 Zendesk tickets in 30 days suggests this
is worth a quick fix before the next release.

───────────────
```

#### Tier 3: Raw Data (optional, only if requested)

If the user configures `show_raw_data: true` in their config, post a final
thread reply with the source-level breakdown. Most users don't need this — the
topic cards are sufficient.

```
:bar_chart: *Source Breakdown — {Topic name}*

• Zendesk Support — 155 items (14 pos · 107 neutral · 34 neg)
• Submit A Wish — 2,588 items (3 pos · 6,135 neutral · 636 neg)
• App Store — 621 items (89 pos · 380 neutral · 152 neg)
• Reddit — 58 items (4 pos · 7 neutral · 44 neg)
```

This tier exists for data-oriented readers who want to see the raw numbers.
It should NOT be the default — only include when explicitly configured.

#### Slack mrkdwn formatting rules (critical)

Slack uses its own markup language called **mrkdwn** — it is NOT standard
markdown. These rules are non-negotiable for well-formatted output.

**Bold:** `*text*` (single asterisks, not double)
**Italic:** `_text_` (single underscores)
**Strikethrough:** `~text~`
**Blockquote:** `>` at the start of a line (single `>`, not `>>`)
**Inline code:** `` `text` ``
**Bullet lists:** Use `•` (bullet character), not `-` or `*`
**Links:** `<https://url|display text>`

**What does NOT work in Slack:**
- `**double asterisk**` — renders literally, does not bold
- `## headings` — renders literally, not as headings
- `---` horizontal rules — renders literally
- Markdown tables — renders as jumbled text
- `[link text](url)` — renders literally, not as a link
- Nested blockquotes — Slack only supports one level of `>`

**Whitespace and line breaks:**
- Use `\n\n` (two newlines) between sections when constructing the message
  string for the Slack API. A single `\n` creates a line break; `\n\n`
  creates visual paragraph spacing.
- Every section header (*What's happening:*, *Signal strength:*, etc.) must
  have a blank line before it.
- After a blockquote (`> _quote_`), always add a blank line before the next
  section. Without this, the next line gets absorbed into the blockquote.

**Emoji:** Use Slack emoji shortcodes (`:emoji_name:`), not Unicode emoji
characters. Slack renders shortcodes consistently across all platforms;
Unicode emoji may render differently on mobile vs desktop.

| Shortcode | Renders As | Meaning |
|-----------|-----------|---------|
| `:star:` | star | Digest header |
| `:red_circle:` | red circle | Needs attention |
| `:large_orange_circle:` | orange circle | Monitor |
| `:green_circle:` | green circle | Healthy |
| `:point_right:` | pointing right | Action item |
| `:thread:` | thread | "Details in thread" |
| `:mag:` | magnifying glass | Topic detail header |
| `:bar_chart:` | bar chart | Raw data section |
| `:bulb:` | lightbulb | Takeaway/insight |

**Separator line:** Use `───────────────` (15 box-drawing horizontal characters,
Unicode U+2500). These render as a clean visual divider in Slack. Do NOT
use `---` (renders literally) or `***` (renders as bold empty).

**Quotes:**
- ONE quote per topic card. Choose for specificity and emotional clarity.
- Format: `> _"verbatim text here"_` — blockquote + italic + real quotes
- Truncate to ~200 chars. End with `...` if truncated.
- Always use customer words (`nli.content`), never AI summaries (`fi.content`)
- Always leave a blank line after the blockquote

**Numbers:**
- Sentiment: always show as percentage, not raw count ("18% negative" not "636 negative")
- Volume: raw count is fine ("700+ reports")
- Comparisons: include context ("3x normal", "up from 4%", "155 tickets in 30 days")
- Use `·` (middle dot, U+00B7) as a visual separator between inline stats:
  `700+ reports · 18% negative · Top channel: Zendesk`

**Message construction for the Slack API:**
When calling `slack_send_message`, pass the full formatted text as the `text`
parameter. Do NOT wrap it in a code block or escape the mrkdwn characters.
The message should be sent as plain text with mrkdwn formatting — Slack
renders it automatically.

#### Message length management

- Tier 1 (channel): under 600 characters. This is a headline, not a report.
- Tier 2 (thread cards): under 2000 characters each. If longer, tighten the
  narrative — you're writing too much.
- Tier 3 (raw data): under 1500 characters. If longer, reduce sources shown.
- Total thread depth: max 4-5 replies (1 per topic + optional raw data).
  More than that and readers stop scrolling.

### Step 6: Deliver

**Slack delivery:**
1. Post Tier 1 (channel message) to the configured channel using `slack_send_message`
2. Capture the `thread_ts` from the response
3. Post each Tier 2 reply as a threaded message using `thread_ts`

**Email delivery:**
1. Send Tier 1 as the email body (with Tier 2 appended below a separator)
2. Subject line: `{digest_title} — {today's date}`

**CoWork delivery:**
1. Display Tier 1 in chat
2. Display Tier 2 below it (no threading needed)

**After delivery, always confirm:**

> "**Digest delivered to {destination}** — go take a look!
>
> When you're ready, let me know if you want to adjust anything or set up a
> recurring schedule."

Do NOT immediately suggest scheduling. Let the user review the output first and
come back when ready.

## Reference Files

- **`references/config-template.md`** — Blank configuration template with field docs
- **`references/example-output.md`** — Example of formatted digest output

## Troubleshooting

**Zero results for a topic:** Use `search_knowledge_graph` to verify the theme
exists. Try keyword variations. Cypher CONTAINS is case-sensitive — use `toLower()`.

**Account breakdowns are all null:** Common for sources without account links
(Reddit, file uploads). Suggest removing breakdowns or filtering to account-linked sources.

**Delivery fails:** Check MCP connection. For Slack, verify channel ID with
`slack_search_channels`. Fall back to CoWork display if connector is down.

**Message too long:** Reduce quotes per topic. Reduce breakdown dimensions.
Split thread replies if needed.

**Scheduled run fails:** Computer must be awake, Claude Desktop open. Check
CoWork schedule history for errors.
