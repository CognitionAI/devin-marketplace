---
name: alert-from-query
description: Create a Coralogix alert from a natural language description or DataPrime query
argument-hint: "<description of what to alert on>"
triggers:
  - user
  - model
---

Help the user create a Coralogix alert based on their description. Walk through this workflow:

## 1. Understand the intent

Parse what the user wants to be alerted on. Identify:
- The **signal**: What condition should trigger the alert (error rate, latency threshold, log pattern, metric value)?
- The **scope**: Which service, application, or subsystem?
- The **severity**: How critical is this (informational, warning, critical)?
- The **threshold**: What value or condition triggers it?

## 2. Validate the data exists

- Use `list_datasets` and `search_for_fields` to confirm the relevant data fields exist in Coralogix.
- If the user described a log pattern, use `query_dataprime` to test the query and confirm it returns expected results.
- If the user described a metric condition, use `search_relevant_metrics` and `query_promql_instant` to verify the metric exists and has data.

## 3. Check for existing alerts

- Use `search_alert_definitions` to check if a similar alert already exists. If so, tell the user and ask if they want to modify it or create a new one.

## 4. Build the alert

- Use `manage_alerts` with `action: "create"` to create the alert.
- Choose the appropriate alert type based on the signal:
  - **Logs immediate** for log pattern matching
  - **Metric threshold** for PromQL-based conditions
  - **Ratio** for error rate alerts
  - **New value** for anomaly detection on new patterns
- Set sensible defaults for notification frequency and grouping.

## 5. Confirm and export

- After creation, retrieve the alert with `get_alerts_object` and show the user the full definition.
- Ask if they want to export it as Infrastructure as Code (Terraform HCL or Kubernetes YAML) using `manage_alerts` with the appropriate export action.

Always confirm with the user before creating the alert. Show them the configuration you intend to create and get explicit approval.
