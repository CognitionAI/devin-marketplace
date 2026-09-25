---
name: triage
description: "Linear: Triage. Triage Alert."
---

# Triage Alert

## Overview

This playbook guides the process of tracing the root cause of a bug or alert using available logs, database access, and code analysis. The workflow ensures thorough investigation across all available data sources to identify strongly plausible root causes. The agent uses the Linear MCP to manage ticket status and communication throughout.

## What's Needed From User

- Linear ticket URL or ticket ID (e.g., `ENG-123` or `https://linear.app/team/issue/ENG-123/...`)
- Repository access for the codebase where the bug may originate
- Access to relevant MCPs (Datadog / Sentry for logs, Redshift/database for data access)

<phase name="Context Gathering" id="1">
## Context Gathering Phase

Think about the full scope of the bug. Tickets are sometimes sparse. Make sure you understand the complete picture of what went wrong.

1. Fetch the ticket details using the Linear MCP `get_issue` tool with the ticket ID
2. **Review all comments and attachments on the ticket** - comments often contain additional context from on-call engineers, customer reports, or related incidents. Attachments may include stack traces, log snippets, screenshots, or monitoring graphs that are essential for investigation.
3. Extract key information from the ticket:
   - Error messages, stack traces, or alert details
   - Affected users, accounts, or entities
   - Timestamps of when the issue occurred
   - Any reproduction steps or conditions mentioned
4. Before diving into logs: use the devin MCP to get a high-level understanding of the relevant systems and architecture. Use `ask_wiki_question` to learn about the relevant systems – send queries for multiple repos that could be relevant to get the full picture. Use `read_wiki_contents` to then get a better understanding how different parts of the codebase connect to each other.
5. Identify the scope of investigation:
   - Which services or components are likely involved?
   - What time range should be searched?
   - What identifiers (user IDs, request IDs, etc.) can be used to filter logs?
6. If there is critical ambiguity about what to investigate: Send a brief message with the specific clarifying questions, then stop and wait for answers
7. If the investigation scope is clear: proceed to the Investigation phase (after completing verification)

<verification>
- Key identifiers for log filtering have been extracted (ticket ID, user ID, timestamps, etc.)
- The affected systems and services have been identified
- The time range for investigation is defined
- You understand what "normal" behavior should look like vs the bug behavior
- Did you try everything in your power to resolve ambiguous aspects before asking the user for help?
- Did you review all comments and attachments on the ticket?
</verification>
</phase>

<phase name="Investigation" id="2">
## Investigation Phase

1. Use `list_issue_statuses` with the team from the issue to discover available status names, then update the ticket status to "In Progress" (or equivalent) using `save_issue`
2. If available: Search logs using MCPs like Sentry, Datadog, etc.
   - Search with relevant query filters (ticket ID, error status, timestamps)
   - Search for error and warning logs
   - Expand search to related services if initial results are sparse
   - Note any error patterns, stack traces, or anomalies
3. If database access is available, query for relevant data:
   - Check the state of affected records
   - Look for data inconsistencies or corruption
   - Review audit logs or history tables if available
4. Analyze the code for potential root causes:
   - Trace the code paths indicated by stack traces or error messages
   - Look for recent changes to affected areas (git blame, recent PRs)
   - Identify edge cases or error handling gaps
   - Check for race conditions, null pointer issues, or validation gaps
5. Cross-reference findings:
   - Correlate log timestamps with code deployments
   - Match error patterns with specific code paths
   - Identify any environmental factors (config changes, dependency updates)

<verification>
- Logs have been searched with appropriate filters
- Database state has been checked (if access available)
- Relevant code paths have been traced
- Findings from different sources have been cross-referenced
- A timeline of events has been established
</verification>
</phase>

<phase name="Root Cause Analysis" id="3">
## Root Cause Analysis Phase

1. Compile a list of strongly plausible root causes, for each including:
   - **Hypothesis**: Clear statement of what went wrong
   - **Evidence**: Specific logs, data, or code that supports this hypothesis
   - **Confidence Level**: High/Medium/Low based on evidence strength
   - **Affected Code**: File paths and line numbers if identifiable
   - **Suggested Fix**: Brief description of how to address the issue
2. If multiple root causes are plausible, rank them by likelihood based on evidence
3. Identify any gaps in the investigation that could be filled with additional access or information
4. Add a comment to the ticket using `save_comment` with the root cause analysis summary
5. Send a brief message to the user with all strongly plausible root causes and supporting evidence

## Output Format

Your final analysis should include the following sections:

### Summary of Current Code State
Describe the current behavior of the affected system:
- What the code is supposed to do (expected behavior)
- What the code is actually doing (observed behavior)
- Key code paths and components involved
- Any recent changes that may be relevant

### Edge Cases and Complexity Hotspots
Identify areas of complexity and potential edge cases:
- Parts of the code where logic is distributed across multiple files/services
- Race conditions or timing-sensitive operations
- Error handling gaps or missing validation
- Data consistency concerns across systems

### Root Cause Hypotheses
For each plausible root cause:
- **Hypothesis**: [Clear statement]
- **Evidence**: [Specific supporting evidence]
- **Confidence**: High/Medium/Low
- **Affected Code**: [File paths and lines]
- **Suggested Fix**: [Brief description]

### Open Questions
List any remaining uncertainties:
- Information that would help confirm or rule out hypotheses
- Access or permissions needed for further investigation
- Questions for the team about expected behavior or business logic

### Confidence Assessment
- **Overall Confidence**: High/Medium/Low
- **Completeness**: What percentage of the relevant code/logs have you reviewed?
- **Open-endedness**: What design decisions or assumptions did you make?

<verification>
- All plausible root causes have been documented with evidence
- Each hypothesis includes confidence level and supporting evidence
- Suggested fixes have been provided where possible
- The ticket has been updated with the analysis
- User has been notified with the findings
- Summary of current code state is included
- Edge cases and complexity hotspots are identified
- Open questions and confidence assessment are documented
</verification>
</phase>

## Specifications

- The output must present all strongly plausible root causes with supporting evidence
- Each root cause must include confidence level and evidence
- The ticket must be updated with the root cause analysis summary
- All ticket status transitions must be reflected in Linear
- Validation: The ticket should have a comment documenting the root cause analysis; the user should receive a clear summary of findings with evidence links

## TODO list guidance
Only every create the todo list for the current phase. Once you fully moved to the next phase, create the todo list for the next phase.

## MCP Tool Reference

### Linear MCP
- `get_issue`: Fetch issue details. Parameter: `id` (the issue identifier like "ENG-123")
- `list_issue_statuses`: List available statuses. Parameter: `team` (team name or ID, not `teamId`)
- `save_issue`: Update an issue. Parameter: `id` for the issue, plus `state`, `links`, etc. `links` is a list of `{url, title}` and is append-only: existing links are kept, so pass only the new ones
- `save_comment`: Add a comment to an issue. Parameters: `issueId` (the issue identifier) and `body` (Markdown)

### Devin MCP
Use for high-level codebase understanding. Available tools:
- `read_wiki_structure`: Get documentation topics. Parameter: `repoName` (e.g., "owner/repo")
- `read_wiki_contents`: View documentation. Parameter: `repoName`
- `ask_wiki_question`: Ask about a repo. Parameters: `repoName` and `question`


Use other MCPs relevant for this task such as Datadog or Sentry if available.

Note: There is no `search` tool on the Devin MCP. Use `ask_wiki_question` instead.
IMPORTANT: there is also a deepwiki MCP that is similar. DO NOT USE IT. Only use the Devin MCP. Because the Devin MCP allows you to access your private repos. The Deepwiki MCP only does public repos.

## Advice and Pointers

- **Keep all ticket comments extremely brief and terse** - write like a human, not an AI. No fluff, no verbose explanations. Just the essential information
- When searching logs, start with specific filters and broaden if needed
- Pay attention to timestamps - correlate events across different systems
- Look for patterns across multiple occurrences of the same error
- Check for recent deployments or config changes around the time of the incident
- Don't stop at the first plausible cause - investigate thoroughly to find all contributing factors

## Forbidden Actions

- Do not start any implementation or code fixes
- Do not create branches or PRs
- Do not send any messages to the user other than the specified messages at the end of each phase or if the user messages you
- Do not dismiss potential root causes without evidence - present all plausible hypotheses
- Do not make changes to production systems or data
- Removing or overriding attributes of the existing tickets without explicit instructions
