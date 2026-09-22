---
name: plan
description: "Linear: Plan. Plan Implementation."
metadata:
  devin:
    from_playbook: true
    playbook_id: "playbook-b0d9a34380374c3e903d900d340d8da7"
    playbook_macro: "!plan"
    playbook_title: "Linear: Plan"
    playbook_access: "community"
---

# Plan Implementation

## Overview

This playbook guides the process of gathering all necessary context for a Linear ticket before implementation begins. The workflow ensures thorough understanding of relevant files, systems, external information, and other details. The output is a concise overview of all important information related to the ticket. The agent uses the Linear MCP to manage ticket status.

## What's Needed From User

- Linear ticket URL or ticket ID (e.g., `ENG-123` or `https://linear.app/team/issue/ENG-123/...`)
- Repository access for the codebase where changes will be made

<phase name="Context Gathering" id="1">
## Context Gathering Phase

Think about the full user intent. Tickets are sometimes sparse. Make sure you disambiguate to the full scope that the user intended.

1. Fetch the ticket details using the Linear MCP `get_issue` tool with the ticket ID
2. **Review all comments and attachments on the ticket** - comments often contain critical context, clarifications, design decisions, or updated requirements that aren't in the main description. Attachments may include designs, specifications, or technical documents.
3. Before diving into code: use the devin MCP to get a high-level understanding of the relevant systems and architecture. Use `ask_question` to learn about the relevant systems – send queries for multiple repos that could be relevant to get the full picture. Use `read_wiki_contents` to then get a better understanding how different parts of the codebase connect to each other.
4. Gather additional context to understand what the ticket means and refers to:
   - Look at past tickets in the same project and from the same author to understand patterns and terminology
   - Search for related commits and PRs (by author and content) that may provide context on the affected systems
   - Check any linked documents, designs, or parent tickets
   - Investigate the actual code
5. Identify any ambiguity in what the ticket refers to or asks for, including jargon or project-specific terms and use all means necessary to answer this yourself
6. If there is critical ambiguity you are unable to resolve: Send a brief message with the specific clarifying questions, then stop and wait for answers
7. If the ticket's meaning is clear: proceed to the Research phase (after completing verification)

<verification>
- Are you thinking about the right repo? Does this intent actually cover multiple repos?
- Is this a frontend change? Or backend? Infra? all the above?
- What is the change in user experience that the author intended?
- The scope covers the full user intent, not just the literal ticket text
- Did you try everything in your power to resolve ambiguous aspects before asking the user for help?
- You are smart so you can make good assumptions if you researched them well. Don't block on the user for preferences. Just simulate what the user would want and do that.
- Did you review all comments and attachments on the ticket?
</verification>
</phase>

<phase name="Research" id="2">
## Research Phase

1. Use `list_issue_statuses` with the team from the issue to discover available status names, then update the ticket status to "In Progress" (or equivalent) using `update_issue`
2. Identify all relevant files and modules:
   - Search for files that will need to be modified
   - Identify related configuration files, tests, and documentation
   - Map out the directory structure of affected areas
3. Trace data flow and control flow through the affected systems:
   - Map callers and callees of functions/methods that will be modified
   - Understand existing patterns and architectural constraints
   - Document API contracts and interfaces involved
4. Research external dependencies and integrations:
   - Check for external services, APIs, or libraries involved
   - Review any relevant external documentation
   - Identify potential compatibility concerns
   - If there are other MCPs available (Notion, Confluence etc.) that might have context look into those as well
5. Gather historical context:
   - Review git history for the affected files
   - Look at past PRs that touched similar areas
   - Check for any known issues or technical debt in the area

<verification>
- All affected files and modules have been identified
- Data flow and control flow are understood and documented
- External dependencies and integrations are mapped
- Historical context has been gathered
- No major knowledge gaps remain about the affected systems
</verification>
</phase>

<phase name="Summary" id="3">
## Summary Phase

1. Compile a concise implementation plan overview using the Output Format below
2. Update the ticket using `update_issue` to add a comment with the implementation plan summary
3. Send a brief message to the user with the compiled overview

## Output Format

Your final implementation plan should include the following sections:

### Summary of Current Code
Describe the current state of the relevant systems:
- **Background Context**: What is this system/feature? How does it work generally?
- **Current Behavior**: What does the specific code do today that may need to change?
- **Key Components**: List the main files, functions, and classes involved

### Affected Files
List all files that will need modification:
- File path and brief description of needed changes
- Related test files
- Configuration files if applicable

### System Overview
Brief description of the systems and components involved:
- How different parts connect to each other
- Data flow through the affected areas
- External dependencies and integrations

### Edge Cases and Complexity Hotspots
Identify areas that need careful attention:
- Parts of the code where logic is distributed across multiple files/repos
- Potential edge cases the implementation must handle
- Error handling and validation concerns
- Backwards compatibility considerations
- Race conditions or timing-sensitive operations

### Key Considerations
Important patterns, constraints, or gotchas to be aware of:
- Existing patterns that should be followed
- Architectural constraints
- Performance considerations
- Security implications

### Suggested Approach
High-level implementation strategy:
- Recommended order of changes
- Key design decisions to make
- Testing strategy

### Open Questions
Any remaining uncertainties:
- Questions that need team input
- Design decisions that require clarification
- Information that would help but isn't blocking

### Confidence Assessment
- **Overall Confidence**: High/Medium/Low - how confident are you that this plan is complete?
- **Completeness**: What percentage of the relevant code have you reviewed?
- **Open-endedness**: What design decisions did you make that weren't explicitly specified?

<verification>
- All sections of the implementation plan overview are filled out
- The summary is concise but comprehensive
- The ticket has been updated with the implementation plan
- User has been notified with the final overview
- Summary of current code is included
- Edge cases and complexity hotspots are identified
- Open questions and confidence assessment are documented
</verification>
</phase>

## Specifications

- The output must be a concise, actionable implementation plan overview
- All relevant files, systems, and dependencies must be identified
- The ticket must be updated with the implementation plan summary
- All ticket status transitions must be reflected in Linear
- Validation: The ticket should have a comment documenting the implementation plan; the user should receive a clear summary of all gathered context

## TODO list guidance
Only every create the todo list for the current phase. Once you fully moved to the next phase, create the todo list for the next phase.

## MCP Tool Reference

### Linear MCP
- `get_issue`: Fetch issue details. Parameter: `id` (the issue identifier like "ENG-123")
- `list_issue_statuses`: List available statuses. Parameter: `team` (team name or ID, not `teamId`)
- `update_issue`: Update an issue. Parameter: `id` for the issue, plus `state`, `links`, etc.
  - When adding resource links, first read the issue to collect existing links and include them in the update so you do not overwrite prior links.

### Devin MCP
Use for high-level codebase understanding. Available tools:
- `read_wiki_structure`: Get documentation topics. Parameter: `repoName` (e.g., "owner/repo")
- `read_wiki_contents`: View documentation. Parameter: `repoName`
- `ask_question`: Ask about a repo. Parameters: `repoName` and `question`

Note: There is no `search` tool on the Devin MCP. Use `ask_question` instead.
IMPORTANT: there is also a deepwiki MCP that is similar. DO NOT USE IT. Only use the Devin MCP. Because the Devin MCP allows you to access your private repos. The Deepwiki MCP only does public repos.

## Advice and Pointers

- **Keep all ticket comments extremely brief and terse** - write like a human, not an AI. No fluff, no verbose explanations. Just the essential information
- When fetching ticket details, also check for any linked documents or parent tickets that may contain additional context
- If the ticket has sub-tasks, note them in your summary as they may affect the implementation scope
- Focus on gathering information, not making implementation decisions - leave options open for the implementer
- Prioritize understanding the "why" behind the ticket, not just the "what"

## Forbidden Actions

- Do not start any implementation or code changes
- Do not create branches or PRs
- Do not send any messages to the user other than the specified messages at the end of each phase or if the user messages you
- Do not make assumptions about implementation approach without researching the codebase first
- Removing or overriding attributes of the existing tickets without explicit instructions
