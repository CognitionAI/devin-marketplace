---
name: investigate-error
description: Investigate an error or exception in Coralogix — find root cause, impacted services, and suggest fixes
argument-hint: "<error message, service name, or case ID>"
triggers:
  - user
  - model
---

Investigate the error or issue the user described using Coralogix observability data. Follow this workflow, adapting based on what information is available:

## 1. Identify the error

- If the user gave a **case ID**, use `get_alerts_object` with `get_watch_data: true` to pull the case, its alert, and triggering records.
- If the user gave an **error message or service name**, use `query_dataprime` to search logs:
  ```
  source logs | filter $d.severity == 'ERROR' | filter $d.message ~= '<pattern>' | limit 50
  ```
  Adjust the time window based on user context (default: last 1 hour).
- If needed, use `search_for_fields` to discover the right field paths before querying.

## 2. Understand the blast radius

- Use `get_service_map_relations_graph` to see which services depend on the affected service.
- Use `get_service_catalog_entities_data` to pull RED metrics (error rate, latency, throughput) for the affected service and its direct dependencies over the same time window.
- If infrastructure data is available, use `list_infrastructure_resources` and `get_infrastructure_resource_health_history` to check for underlying host/pod health issues (OOMKilled, CPU saturation, restarts).

## 3. Find the root cause

- Use `query_dataprime` to look for correlated errors across upstream services, narrowing the time window around the first occurrence.
- Check for recent deployments or config changes using log queries for deploy-related events.
- If spans are available, query the spans dataset to trace the request path that produced the error.

## 4. Check existing alerting

- Use `search_alert_definitions` to see if there is already an alert covering this error pattern. Note any gaps.

## 5. Report findings

Present a structured summary:

- **Error**: What happened, when it started, and the error pattern.
- **Impact**: Which services and users are affected, error rate/latency changes.
- **Root cause**: Your best assessment of why this is happening, with evidence.
- **Fix suggestion**: Concrete next steps — code change, config change, scaling action, or rollback.
- **Alerting gap**: Whether an alert should be created to catch this earlier next time.
