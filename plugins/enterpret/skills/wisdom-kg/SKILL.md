---
name: wisdom-kg
description: >
  This skill teaches Claude how to query the Enterpret Wisdom Knowledge Graph
  for any organization's customer feedback data. It covers the schema, query
  language (Cypher), validated patterns, citation formatting, and critical rules
  to avoid failed queries. Auto-loads for any command that accesses the KG.
version: 5.0.0
---

# Wisdom Knowledge Graph — Query Guide

## Organization Context

Organization details are loaded from `context/organization.json` (created during onboarding). This file contains:

- **name** — Organization display name (e.g., "Acme Corp")
- **slug** — URL slug (e.g., "acme-corp")
- **dashboardUrl** — Base URL to the Enterpret dashboard
- **citationBaseUrl** — Base URL for record citation links
- **taxonomy.l1Categories** — Top-level categories with volume
- **taxonomy.themeCategories** — Theme types (COMPLAINT, HELP, PRAISE, IMPROVEMENT, etc.)

If `context/organization.json` does not exist, tell the user to run `/start` for first-time setup.

## Session Setup

Run `get_organization_details` as a pre-flight check at session start. Cache the org details and schema once — never re-query per command.

## User Context

Check for `.claude/enterpret-customer-insights.local.md` — if it exists, parse YAML frontmatter for user preferences (`name`, `role`, `team`, `focus`, `output_style`, `brand_colors`, `company_name`, `language`).

If the file does not exist, assume a **Product Manager** persona: focused on customer experience and product operations, wants structured evidence-based output, cares about CSAT/DSAT/volume trends, produces weekly VOC reports. Frame recommendations as product decisions, not abstract findings.

## Search Before Query

**ALWAYS** use `search_knowledge_graph` before writing Cypher when the user mentions a specific feature, issue, or topic. User language rarely matches taxonomy labels.

Search with 2-3 keyword variations:
- The user's exact words
- Synonyms or related terms
- More specific sub-topics

Use the EXACT theme/subtheme names returned by search in Cypher queries. Never guess taxonomy names.

## Time Window Conventions

| Context | Default Window | Rationale |
|---------|---------------|-----------|
| Trend analysis / weekly brief | 30 days | Enough for WoW comparison with context |
| Urgency / escalation scan | 48 hours – 7 days | Recent spikes matter more |
| Strategic evidence (PRDs, competitive) | 90 days | Full quarter for sizing |
| Post-launch comparison | 30/30 (30 pre, 30 post) | Clean A/B period |
| WoW comparison | Current 7d vs prior 7d | Standard week-over-week |

**Always state the time window in output.** Compute dates in ISO format (YYYY-MM-DD).

## Trend Computation

Week-over-week requires TWO separate queries. Compute in analysis, not Cypher:
```
trend = (current_period - prior_period) / prior_period
```

Handle edge cases:
- Prior = 0, current > 0 → "NEW"
- Prior = 0, current = 0 → "Inactive"
- Negative trend → "↓ X%"
- Flat (< 5% change) → "→ flat"

**Rising 50% WoW at 30 mentions is more important than flat at 200.** Trend acceleration is the strongest signal.

## Segment Handling

When account metadata exists, break results by segment. Weight enterprise accounts higher.

When NOT available (common), note the limitation:
> "Account-level segmentation not available. Volume counts represent all feedback."

Never fabricate segment data.

## Channel Mix Interpretation

| Pattern | Interpretation |
|---------|---------------|
| Support tickets only | Moderate — blocking enough to contact support |
| Tickets + app reviews | High — blocking AND publicly visible |
| Tickets + reviews + social | Pervasive — spreading across channels |
| Reviews only | Perception issue — may not be functionally broken |

## MCP Tools Available

You have 5 tools from the `enterpret-wisdom-mcp` MCP server:

| Tool | Use For |
|------|---------|
| `get_organization_details` | Verify connection (returns org name, slug). Use as pre-flight check. |
| `get_schema` | Retrieve full KG schema (node types, relationships, properties). Call once per session. |
| `execute_cypher_query` | Run Cypher queries against the KG. Primary data access method. |
| `search_knowledge_graph` | Natural language search. Good for exploration, less precise than Cypher. |
| `find_user_quote` | Direct quote retrieval by topic or user. Faster than Cypher for getting verbatim quotes. Good for evidence gathering when you need representative quotes quickly. |

## Schema Overview

### Node Types

| Node | Description | Key Properties |
|------|-------------|----------------|
| `NaturalLanguageInteraction` | A single feedback record (ticket, review, etc.) | `record_id`, `content`, `record_timestamp`, `source`, `uf_cor_9a00Yg__list` (COR) |
| `FeedbackInsight` | AI-extracted insight from an NLI | `record_id`, `content`, `summary_type`, `feedback_record_id` |
| `CustomerFeedbackTags` | Junction node connecting insights to taxonomy | `record_id`, `nli_id`, `theme_id`, `l1_id`, `l2_id`, `l3_id` |
| `Theme` | Grouped topic (e.g., "Delayed Response Times") | `name`, `display_name`, `description`, `category_enum` |
| `Subtheme` | More specific topic under a Theme | `name`, `display_name` |
| `L1`, `L2`, `L3` | Taxonomy hierarchy levels | `name`, `description` |
| `SentimentPrediction` | Sentiment label for an insight | `label` (values: `"Positive"`, `"Negative"`, `"Neutral"`) |
| `TaxonomyHierarchy` | Pre-built taxonomy paths | `l1_id`, `l2_id`, `l3_id`, `theme_id` |

### Key Relationships

```
(NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(FeedbackInsight)
(FeedbackInsight)-[:HAS_TAGS]->(CustomerFeedbackTags)
(FeedbackInsight)-[:HAS_SENTIMENT]->(SentimentPrediction)
(CustomerFeedbackTags)-[:BELONGS_TO_L1]->(L1)
(CustomerFeedbackTags)-[:BELONGS_TO_L2]->(L2)
(CustomerFeedbackTags)-[:BELONGS_TO_L3]->(L3)
(CustomerFeedbackTags)-[:HAS_THEME]->(Theme)
(CustomerFeedbackTags)-[:HAS_SUBTHEME]->(Subtheme)
(Theme)-[:HAS_SUBTHEME]->(Subtheme)
(TaxonomyHierarchy)-[:HAS_L1]->(L1)
(TaxonomyHierarchy)-[:HAS_L2]->(L2)
(TaxonomyHierarchy)-[:HAS_L3]->(L3)
(TaxonomyHierarchy)-[:HAS_THEME]->(Theme)
```

### CRITICAL: Traversal Paths

**To get from NLI to taxonomy (L1/L2/L3/Theme):**
```
NaturalLanguageInteraction → SUMMARIZED_BY → FeedbackInsight → HAS_TAGS → CustomerFeedbackTags → BELONGS_TO_L1/L2/L3 or HAS_THEME
```

**To get sentiment:**
```
FeedbackInsight → HAS_SENTIMENT → SentimentPrediction
```
Note: Sentiment is on FeedbackInsight, NOT on NaturalLanguageInteraction.

**To get L2 under L1 (or L3 under L2):**
Use CustomerFeedbackTags as the hub — it connects to L1, L2, L3, and Theme DIRECTLY (flat, not chained).
```cypher
MATCH (cft:CustomerFeedbackTags)-[:BELONGS_TO_L1]->(l1:L1)
MATCH (cft)-[:BELONGS_TO_L2]->(l2:L2)
WHERE l1.name = "{L1_CATEGORY}"
```

### Common Properties for Filtering

| Property | On Node | Example Values | Notes |
|----------|---------|----------------|-------|
| COR (Country/Region) | `NaturalLanguageInteraction.uf_cor_9a00Yg__list` | `"US"`, `"KR"`, `"BR"` | List type — use `=` not `CONTAINS` |
| Timestamp | `NaturalLanguageInteraction.record_timestamp` | `"2026-02-01"` | ISO format, use `>=` and `<` for ranges |
| Source | `NaturalLanguageInteraction.source` | Various | |
| Citation ID | `FeedbackInsight.feedback_record_id` | UUID | Use for dashboard links |
| Sentiment | `SentimentPrediction.label` | `"Positive"`, `"Negative"`, `"Neutral"` | Capitalized |
| Insight type | `FeedbackInsight.summary_type` | `"BASIC"` | |

---

## 14 Critical Query Rules

These rules prevent failed queries. Violating any one will cause errors or incorrect results.

### 1. ALWAYS use LIMIT
```cypher
// CORRECT
MATCH (t:Theme) RETURN t.name LIMIT 20

// WRONG — will timeout on large datasets
MATCH (t:Theme) RETURN t.name
```
Default LIMIT: 10-20 for exploration, up to 50 for reports. Never exceed 50.

### 2. ALWAYS use COUNT(DISTINCT ...) with the right ID
```cypher
// CORRECT — count unique feedback records
RETURN COUNT(DISTINCT fi.feedback_record_id) AS volume

// WRONG — inflates counts due to multiple paths
RETURN COUNT(nli) AS volume
```

### 3. NEVER use `count` as an alias
```cypher
// CORRECT
RETURN COUNT(DISTINCT fi.feedback_record_id) AS volume

// WRONG — `count` is a reserved word in Cypher
RETURN COUNT(DISTINCT fi.feedback_record_id) AS count
```

### 4. Sentiment label property is `label`, values are CAPITALIZED
```cypher
// CORRECT
WHERE sp.label = "Negative"

// WRONG — property is label not sentiment
WHERE sp.sentiment = "negative"
```
Valid values: `"Positive"`, `"Negative"`, `"Neutral"`

### 5. COR filtering uses `=` on list properties
```cypher
// CORRECT
WHERE nli.uf_cor_9a00Yg__list = "US"

// WRONG — CONTAINS doesn't work on list-type properties
WHERE nli.uf_cor_9a00Yg__list CONTAINS "US"
```

### 6. NEVER use labels() function
```cypher
// CORRECT — match specific node types
MATCH (n:Theme) RETURN n.name

// WRONG — labels() is not supported
MATCH (n) WHERE "Theme" IN labels(n) RETURN n.name
```

### 7. NEVER use array indexing
```cypher
// CORRECT — use UNWIND for list access
MATCH (n:NaturalLanguageInteraction) UNWIND n.uf_cor_9a00Yg__list AS cor RETURN cor

// WRONG — array indexing not supported
MATCH (n:NaturalLanguageInteraction) RETURN n.uf_cor_9a00Yg__list[0]
```

### 8. Date filtering uses `record_timestamp` with string comparison
```cypher
// CORRECT — string comparison on ISO dates
WHERE nli.record_timestamp >= "2026-02-01" AND nli.record_timestamp < "2026-02-08"

// WRONG — no date() function, wrong property name
WHERE date(nli.created_at) >= date("2026-02-01")
```

### 9. NEVER use MATCH after WITH — use single MATCH with multiple paths
The KG translator does not support `MATCH` after `WITH`. For co-occurring/cascade queries, use a single `MATCH` with comma-separated paths:
```cypher
// CORRECT — single MATCH, two paths from same node
MATCH (fi:FeedbackInsight)-[:HAS_TAGS]->(cft1:CustomerFeedbackTags)-[:HAS_THEME]->(t1:Theme),
      (fi)-[:HAS_TAGS]->(cft2:CustomerFeedbackTags)-[:HAS_THEME]->(t2:Theme)
WHERE t1.name CONTAINS "X" AND NOT t2.name CONTAINS "X"

// WRONG — MATCH after WITH is not supported
MATCH (fi)-[:HAS_TAGS]->(cft)-[:HAS_THEME]->(t1:Theme)
WHERE t1.name CONTAINS "X"
WITH fi.feedback_record_id AS rid
MATCH ... WHERE fi2.feedback_record_id = rid
```

### 10. Week-over-week requires TWO separate queries
Do NOT try to compute WoW in a single query. Run:
- Query 1: Current week data
- Query 2: Previous week data
- Compare results in your analysis (outside Cypher)

### 11. Citation URLs use feedback_record_id from FeedbackInsight
```
{citationBaseUrl}{feedback_record_id}
```
Read `citationBaseUrl` from `context/organization.json`. Always include `fi.feedback_record_id` in queries where you need citation links. This field is on `FeedbackInsight`, NOT on `NaturalLanguageInteraction`.

### 12. Account metadata is schema-dependent
Account node labels, properties, and relationships **vary by customer KG**. Do NOT assume any of these exist:
- `DerivedAccount` node label — some KGs use `Account`, some use `DerivedAccount`, some have neither
- `da.name` or `a.name` — the Account node may only have `record_id` and `origin_record_id`
- `HAS_ACCOUNT` relationship from NLI — may not exist; account data may live as NLI source-specific properties

**Before running account-level queries:**
1. Check the schema with `get_schema` for account-related nodes and relationships
2. If account nodes exist but lack `name`, try `record_id` or source-specific properties
3. If no account relationship exists, skip account-level analysis and note the gap
4. Commands should ALWAYS have graceful fallback for missing account data

### 13. NEVER use relationship aliases in MATCH
The KG translator does not support relationship variables like `-[r]->`. Always use typed relationships:
```cypher
-- WRONG: MATCH (nli)-[r]->(a:Account)
-- RIGHT: MATCH (nli)-[:HAS_ACCOUNT]->(a:Account)
```
If you need to explore what relationships exist, use `get_schema` instead.

### 14. Use `cypher_query` as the parameter name
The Wisdom MCP tool `execute_cypher_query` expects the parameter named `cypher_query`, NOT `query`.

---

## Guardrails

| Condition | Response |
|-----------|----------|
| < 10 data points | "Directional signal only. Treat with caution." |
| < 3 data points | "Insufficient data for analysis." |
| No results | Say so. Never fabricate or substitute unrelated data. |
| Query fails | Check error, simplify, verify schema. Never retry same failed query. |
| Auth error | Guide user to check token: Settings > API Tokens |

---

## Query Strategy by Command

### /find — Quick feedback lookup
1. `search_knowledge_graph` to map topic to themes
2. Theme volume + sentiment (30d)
3. Subtheme breakdown
4. Verbatim evidence with citations

### /analyze — Deep multi-query synthesis (with optional --rootcause mode)
**Standard mode (30d window):**
1. `search_knowledge_graph` to map topic to themes
2. Theme volume + sentiment
3. Subtheme breakdown
4. WoW trend (two queries)
5. Taxonomy context (L1/L2/L3 positioning)
6. Co-occurring themes (single MATCH, two paths)
7. Insight type distribution (COMPLAINT, IMPROVEMENT, QUESTION, PRAISE)
8. Verbatim evidence with citations
9. Account breadth (if available)

**Rootcause mode (14d window) — same queries, different interpretation:**
- Skip taxonomy placement, add severity assessment (P0/P1/P2) and hypothesis clustering
- Co-occurring themes framed as "Cascade Impact"
- Output includes root cause hypotheses and "What We DON'T Know"

### /explore — Taxonomy browsing, record retrieval
1. L1 categories with volume counts
2. L1 → L2 drill-down for selected category
3. L2 → L3 + Theme drill-down with sentiment
4. Record lookup by feedback_record_id

### /report — All output modes (quick + branded documents)
**Quick modes (chat output, offer doc export):**
1. Weekly Memo: Big 5 scan (emerging, worsening, enterprise blockers, self-serve friction, decision)
2. Account Brief: Account themes, sentiment, market comparison, scalability assessment
3. Executive Summary: Top themes, sentiment split, key movers
4. Regional Digest: Same as weekly with COR filter

**Document modes (guided archetype → docx/pptx/html):**
1. Theme Deep-Dive: L1 → L2 → L3 drill, sentiment, evidence
2. Sentiment Trend: Period comparison, sentiment per theme, WoW
3. Custom: User-defined structure

---

## Error Handling

If a query fails:

1. **Check the error message** — usually indicates which rule was violated
2. **Simplify the query** — remove filters, reduce complexity
3. **Verify schema** — call `get_schema` to confirm node/property names
4. **Try natural language search** — `search_knowledge_graph` as fallback
5. **Never retry the same failed query** — always fix the issue first

If you get an authentication error, tell the user to run `/start` for setup, or contact support@enterpret.com.

---

## Reference Files

- `references/query-patterns.md` — Validated Cypher query patterns (copy and adapt)
- `references/schema-appendix.md` — Extended schema: account metadata, NPS, work items, feature requests, opportunity data, churn signals
