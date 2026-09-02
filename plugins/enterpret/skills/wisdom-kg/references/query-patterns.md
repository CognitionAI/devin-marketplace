# Validated Cypher Query Patterns

All patterns are validated against the Enterpret Wisdom Knowledge Graph. Copy and adapt — do not invent new patterns without testing.

**Key traversal:** `NaturalLanguageInteraction → SUMMARIZED_BY → FeedbackInsight → HAS_TAGS → CustomerFeedbackTags → BELONGS_TO_L1/L2/L3 or HAS_THEME`

**Placeholder conventions:**
- `{START_DATE}` / `{END_DATE}` — ISO date strings (e.g., `"2026-02-01"`)
- `{COR}` — Country/region code (e.g., `"US"`, `"KR"`)
- `{L1_CATEGORY}` — L1 category name from `context/organization.json`
- `{L2_CATEGORY}` — L2 sub-category name
- `{THEME_NAME}` — Theme name or partial match string

---

## Pattern 1: Top Themes by Volume

### Basic (no filters)
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
RETURN t.name AS theme, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
LIMIT 20
```

### With date range
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
WHERE nli.record_timestamp >= "{START_DATE}" AND nli.record_timestamp < "{END_DATE}"
RETURN t.name AS theme, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
LIMIT 20
```

### With COR (Country/Region) filter
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
WHERE nli.record_timestamp >= "{START_DATE}" AND nli.record_timestamp < "{END_DATE}"
  AND nli.uf_cor_9a00Yg__list = "{COR}"
RETURN t.name AS theme, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
LIMIT 20
```

---

## Pattern 2: Sentiment Distribution

### Overall sentiment (with date range)
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_SENTIMENT]->(sp:SentimentPrediction)
WHERE nli.record_timestamp >= "{START_DATE}" AND nli.record_timestamp < "{END_DATE}"
RETURN sp.label AS sentiment, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
```

### Sentiment for a specific L1 category
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_SENTIMENT]->(sp:SentimentPrediction)
MATCH (fi)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:BELONGS_TO_L1]->(l1:L1)
WHERE l1.name = "{L1_CATEGORY}"
RETURN sp.label AS sentiment, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
LIMIT 10
```

### Sentiment per theme (top themes in a date range)
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_SENTIMENT]->(sp:SentimentPrediction)
MATCH (fi)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
WHERE nli.record_timestamp >= "{START_DATE}" AND nli.record_timestamp < "{END_DATE}"
WITH t.name AS theme, sp.label AS sentiment, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
RETURN theme, sentiment, volume
LIMIT 50
```

---

## Pattern 3: L1 → L2 → L3 Taxonomy Drill-Down

### L1 categories with volume
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:BELONGS_TO_L1]->(l1:L1)
RETURN l1.name AS category, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
LIMIT 20
```

### L2 under a specific L1
```cypher
MATCH (fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:BELONGS_TO_L1]->(l1:L1)
MATCH (cft)-[:BELONGS_TO_L2]->(l2:L2)
WHERE l1.name = "{L1_CATEGORY}"
RETURN l2.name AS subcategory, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
LIMIT 20
```

### L3 + Themes under a specific L2
```cypher
MATCH (cft:CustomerFeedbackTags)-[:BELONGS_TO_L1]->(l1:L1)
MATCH (cft)-[:BELONGS_TO_L2]->(l2:L2)
MATCH (cft)-[:BELONGS_TO_L3]->(l3:L3)
MATCH (cft)-[:HAS_THEME]->(t:Theme)
WHERE l1.name = "{L1_CATEGORY}" AND l2.name = "{L2_CATEGORY}"
RETURN l3.name AS l3_category, t.name AS theme, COUNT(DISTINCT cft.record_id) AS volume
ORDER BY volume DESC
LIMIT 20
```

### L3 under a specific L2 with sentiment
```cypher
MATCH (fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:BELONGS_TO_L2]->(l2:L2)
MATCH (cft)-[:BELONGS_TO_L3]->(l3:L3)
MATCH (fi)-[:HAS_SENTIMENT]->(sp:SentimentPrediction)
WHERE l2.name = "{L2_CATEGORY}"
RETURN l3.name AS issue, sp.label AS sentiment, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
LIMIT 20
```

---

## Pattern 4: Feedback Content with Citations

### By theme
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
WHERE t.name CONTAINS "{THEME_NAME}"
RETURN fi.feedback_record_id AS record_id, nli.content AS verbatim, fi.summary_type AS insight_type
ORDER BY fi.record_id DESC
LIMIT 10
```

### By L1 category + date + COR
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:BELONGS_TO_L1]->(l1:L1)
WHERE l1.name = "{L1_CATEGORY}"
  AND nli.record_timestamp >= "{START_DATE}" AND nli.record_timestamp < "{END_DATE}"
  AND nli.uf_cor_9a00Yg__list = "{COR}"
RETURN fi.feedback_record_id AS record_id, nli.content AS verbatim, fi.summary_type AS insight_type
ORDER BY nli.record_timestamp DESC
LIMIT 10
```

**Citation URL format:**
```
{citationBaseUrl}{record_id}
```
Read `citationBaseUrl` from `context/organization.json`.

---

## Pattern 5: Week-over-Week Comparison

**IMPORTANT: Always run two separate queries. Never attempt WoW in a single query.**

### Current week
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
WHERE nli.record_timestamp >= "{START_DATE}" AND nli.record_timestamp < "{END_DATE}"
RETURN t.name AS theme, COUNT(DISTINCT fi.feedback_record_id) AS current_volume
ORDER BY current_volume DESC
LIMIT 20
```

### Previous week
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
WHERE nli.record_timestamp >= "{PREV_START_DATE}" AND nli.record_timestamp < "{PREV_END_DATE}"
RETURN t.name AS theme, COUNT(DISTINCT fi.feedback_record_id) AS previous_volume
ORDER BY previous_volume DESC
LIMIT 20
```

Then compute: `change = current_volume - previous_volume`, `pct_change = change / previous_volume * 100`

---

## Pattern 6: Theme Category Breakdown (Insight Types)

```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
WHERE nli.record_timestamp >= "{START_DATE}" AND nli.record_timestamp < "{END_DATE}"
RETURN t.name AS theme, fi.summary_type AS category, COUNT(DISTINCT fi.feedback_record_id) AS volume
ORDER BY volume DESC
LIMIT 30
```

---

## Pattern 7: Co-occurring Themes (Cascade Impact)

Find themes that appear alongside a target theme on the same feedback records.

**IMPORTANT:** The KG does not support `MATCH` after `WITH`. Use a single `MATCH` with two paths from the same `FeedbackInsight` node instead:
```cypher
MATCH (fi:FeedbackInsight)-[:HAS_TAGS]->(cft1:CustomerFeedbackTags)-[:HAS_THEME]->(t1:Theme),
      (fi)-[:HAS_TAGS]->(cft2:CustomerFeedbackTags)-[:HAS_THEME]->(t2:Theme)
WHERE t1.name CONTAINS "{THEME_NAME}" AND NOT t2.name CONTAINS "{THEME_NAME}"
RETURN t2.name AS co_occurring_theme, COUNT(DISTINCT fi.feedback_record_id) AS shared_volume
ORDER BY shared_volume DESC
LIMIT 10
```

---

## Pattern 8: Taxonomy Exploration

### All L2 + L3 + Themes under an L1
```cypher
MATCH (cft:CustomerFeedbackTags)-[:BELONGS_TO_L1]->(l1:L1)
MATCH (cft)-[:BELONGS_TO_L2]->(l2:L2)
MATCH (cft)-[:BELONGS_TO_L3]->(l3:L3)
MATCH (cft)-[:HAS_THEME]->(t:Theme)
WHERE l1.name = "{L1_CATEGORY}"
RETURN DISTINCT l2.name AS l2, l3.name AS l3, t.name AS theme
ORDER BY l2, l3, theme
LIMIT 50
```

### Full taxonomy paths using TaxonomyHierarchy
```cypher
MATCH (th:TaxonomyHierarchy)-[:HAS_L1]->(l1:L1)
MATCH (th)-[:HAS_L2]->(l2:L2)
MATCH (th)-[:HAS_L3]->(l3:L3)
MATCH (th)-[:HAS_THEME]->(t:Theme)
WHERE t.name CONTAINS "{THEME_NAME}"
RETURN l1.name AS l1, l2.name AS l2, l3.name AS l3, t.name AS theme
LIMIT 20
```

---

## Pattern 9: Negative Sentiment Volume (Emergency Detection)

```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)-[:HAS_SENTIMENT]->(sp:SentimentPrediction)
MATCH (fi)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
WHERE sp.label = "Negative"
  AND nli.record_timestamp >= "{START_DATE}" AND nli.record_timestamp < "{END_DATE}"
RETURN t.name AS theme, COUNT(DISTINCT fi.feedback_record_id) AS negative_volume
ORDER BY negative_volume DESC
LIMIT 10
```

---

## Pattern 10: Source-Specific Metadata

### Ticket lookup by feedback_record_id
```cypher
MATCH (nli:NaturalLanguageInteraction)-[:SUMMARIZED_BY]->(fi:FeedbackInsight)
WHERE fi.feedback_record_id = "{RECORD_ID}"
OPTIONAL MATCH (fi)-[:HAS_SENTIMENT]->(sp:SentimentPrediction)
OPTIONAL MATCH (fi)-[:HAS_TAGS]->(cft:CustomerFeedbackTags)-[:HAS_THEME]->(t:Theme)
RETURN fi.feedback_record_id AS id, nli.content AS verbatim,
       nli.record_timestamp AS date, t.name AS theme, sp.label AS sentiment
LIMIT 5
```
