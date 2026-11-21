---
name: service-health
description: Get a comprehensive health overview for a service — RED metrics, dependencies, infrastructure, and active alerts
argument-hint: "<service name>"
triggers:
  - user
  - model
---

Build a comprehensive health report for the service the user specified. Gather data from multiple Coralogix sources in parallel where possible.

## 1. Discover the service

- Use `list_service_catalog_entities` for entity type `service` to confirm the service exists and get its exact name.
- If the name is ambiguous, list candidates and ask the user to confirm.

## 2. RED metrics (Rate, Errors, Duration)

- Use `get_service_catalog_entity_type_schema` for `service` to discover available columns.
- Use `get_service_catalog_entities_data` to pull error rate, throughput, and latency percentiles (p50, p95, p99) for the last 1 hour. Compare against 24-hour-ago baseline if the tool supports it.

## 3. Dependencies

- Use `get_service_map_relations_graph` to map upstream and downstream dependencies.
- For each direct dependency, pull its RED metrics with `get_service_catalog_entities_data` to spot any unhealthy neighbours.

## 4. Infrastructure

- Use `list_service_catalog_entity_types` to check for `k8s-pod` or `jvm` entity types.
- If available, pull resource saturation data (CPU, memory, OOMKilled, heap usage, GC) for the service's pods/JVMs using `get_service_catalog_entities_data`.

## 5. Active alerts and cases

- Use `search_alert_definitions` filtered to the service name to list configured alerts.
- Use `manage_cases` to check for any open cases linked to this service.

## 6. Recent logs

- Use `query_dataprime` to sample recent error and warning logs:
  ```
  source logs | filter $d.service == '<service>' | filter $d.severity in ('ERROR','WARN') | limit 20
  ```

## 7. Report

Present the health overview as a structured report:

- **Status**: Overall health (Healthy / Degraded / Critical) based on the evidence.
- **RED metrics**: Current values with trend direction vs baseline.
- **Dependencies**: Dependency graph summary, flagging any degraded dependencies.
- **Infrastructure**: Resource utilisation and any saturation warnings.
- **Alerts**: Active alerts and open cases.
- **Recent errors**: Top error patterns from logs.
- **Recommendations**: Any actions to take (scale, investigate, create missing alerts).
