---
name: checkmarx-sast-resolution
description: "Triage the top TO_VERIFY finding in a recent Checkmarx One SAST scan, report whether it is real, update its triage status, and open a fix PR for a verified issue."
triggers: ["user"]
---

# Checkmarx SAST resolution

1. Confirm the repository and branch (use the repository's default branch if
   unspecified), Checkmarx One tenant, and region. Authenticate to the tenant's
   official regional Checkmarx API with its configured secret, e.g.
   `CHECKMARX_API_KEY`. Never print the key or access token.
2. Use the Projects and Scans APIs to identify the matching project and its
   latest SAST scan on that branch. If no scan exists or it is older than 30
   days, report that and stop; do not start a new scan.
3. Read the paginated [SAST results](https://checkmarx.stoplight.io/docs/checkmarx-one-api-reference-guide/branches/main/68dabfc984bc3-retrieve-sast-scan-results)
   as JSON. Consider only `TO_VERIFY` findings. Select one by severity
   (`CRITICAL`, then `HIGH`, then `MEDIUM`), using `firstCreatedAt` to pick the
   oldest among ties. If there are none, report that and stop.
4. Fetch the query description and inspect the flagged code on the scanned
   revision. Report the project ID, scan ID, query ID, similarity ID, and
   evidence for whether the finding is a real vulnerability or a false
   positive. If the evidence is inconclusive, leave the finding unchanged.
5. Recheck the finding's current status before making changes. If it has
   already been triaged, report that and stop. Use the
   [SAST predicate API](https://checkmarx.stoplight.io/docs/checkmarx-one-api-reference-guide/branches/main/yj7nwi7ggcv3l-change-a-sast-predicate)
   to record the verdict according to the tenant's triage policy. If the
   target state is unclear, ask rather than guessing. For a confirmed issue,
   test a focused fix and open a PR against the target branch. Do not merge it.
