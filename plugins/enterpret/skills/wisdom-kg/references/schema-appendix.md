# Common Schema Reference — Extended Properties

These properties and paths are common across Enterpret KG instances. **Always verify with `get_schema` before using** — not all instances have all of these.

## Account Metadata (schema-dependent)
```cypher
(nli)-[:PROVIDED_BY_ACCOUNT]->(a:Account)
-- OR: (nli)-[:HAS_ACCOUNT]->(da:DerivedAccount)
```

Common account properties (verify with `get_schema`):
- **Name:** `a.snowflake_enterpret_account_account_name` or `a.salesforce_name`
- **Tier:** `a.snowflake_enterpret_account_account_tier`
- **Industry:** `a.snowflake_enterpret_account_industry`
- **ARR:** `a.salesforce_annualrevenue`
- **CSM:** `a.snowflake_enterpret_account_csm_owner_name`
- **Active:** `a.snowflake_enterpret_account_active_customer`

## NPS Data
NPS survey NLIs have source `snowflake-nps survey` and these properties:
- `snowflake_nps_survey_nps_score_n` — numeric score (0-10)
- `snowflake_nps_survey_nps_category_s` — "Promoter", "Passive", "Detractor"
- `snowflake_nps_survey_account_name_s` — account name
- `snowflake_nps_survey_account_tier_s` — account tier

## Source Values
`nli.source` common values: `Gong`, `intercom`, `g2`, `snowflake-nps survey`, `slack`

## Work Items
```cypher
(t:Theme)-[:HAS_ARTEFACT_REFERENCE]->(wa:WorkItemArtefact)-[:HAS_WORK_ITEM]->(wi:WorkItem)
```
Properties: `wi.name`, `wi.status`, `wi.key`

## Feature Requests
```cypher
(t:Theme)-[:HAS_FEATURE_REQUEST]->(fr:FeatureRequest)
```
Properties: `fr.name`, `fr.status`

## Opportunity Data
```cypher
(nli)-[:HAS_OPPORTUNITY]->(do:DerivedOpportunity)
```
Properties: `do.stage`, `do.amount`

## Churn Signals (Salesforce)
- `a.salesforce_opportunities_records_stagename`
- `a.salesforce_opportunities_records_isclosed`
- `a.salesforce_opportunities_records_iswon`
- `a.salesforce_opportunities_records_closed_lost_reason_c`
