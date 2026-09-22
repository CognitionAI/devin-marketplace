---
name: review
description: "Linear: Code Review."
metadata:
  devin:
    from_playbook: true
    playbook_id: "playbook-b57154e41ca443318e79e089faba37ed"
    playbook_macro: "!review"
    playbook_title: "Linear: Code Review"
    playbook_access: "community"
---

# Code Review

## Overview

This playbook guides the process of reviewing a pull request attached to a Linear ticket. The workflow ensures thorough review of requirements fulfillment, code quality, security, and adherence to codebase standards. The agent uses the Linear MCP to manage ticket status and communication throughout.

## What's Needed From User

- Linear ticket URL or ticket ID (e.g., `ENG-123` or `https://linear.app/team/issue/ENG-123/...`)
- Repository access for the codebase where the PR was created

<phase name="Context Gathering" id="1">
## Context Gathering Phase

Understand the ticket requirements and locate the PR to review.

1. Fetch the ticket details using the Linear MCP `get_issue` tool with the ticket ID
2. **Review all comments and attachments on the ticket** - comments often contain critical context, clarifications, or updated requirements. Attachments may include designs, specifications, or acceptance criteria.
3. Verify a PR is attached to the ticket:
   - Check the ticket's links field for PR URLs
   - If no PR is found, send a brief message asking for the PR link, then stop and wait
4. Extract key requirements from the ticket:
   - What is the expected behavior or outcome?
   - Are there specific acceptance criteria?
   - What was the original intent of the ticket creator?
5. Before reviewing code: use the devin MCP to get a high-level understanding of the relevant systems and architecture. Use `ask_question` to learn about the relevant systems. Use `read_wiki_contents` to understand how different parts of the codebase connect.
6. Look for coding standards and guidelines:
   - Search for knowledge/md files in the repository meant for agents or developers
   - Check for CONTRIBUTING.md, CODING_STANDARDS.md, or similar files
   - If Notion or Confluence MCPs are available, search for coding guidelines there
7. If there is critical ambiguity about the requirements: Send a brief message with specific clarifying questions, then stop and wait for answers
8. If requirements are clear: proceed to the Code Review phase (after completing verification)

<verification>
- The ticket requirements and acceptance criteria are understood
- A PR link has been identified and is accessible
- The original intent of the ticket creator is clear
- Relevant coding standards and guidelines have been gathered
- You understand what "correct" implementation looks like for this ticket
- Did you review all comments and attachments on the ticket?
</verification>
</phase>

<phase name="Code Review" id="2">
## Code Review Phase

1. Use `list_issue_statuses` with the team from the issue to discover available status names, then update the ticket status to "In Review" (or equivalent) using `update_issue`
2. Check out the PR branch and review the diff:
   - Understand the scope of changes (files modified, lines added/removed)
   - Identify the main areas of the codebase being modified
3. **Requirements Fulfillment Check**:
   - Does the implementation address all requirements from the ticket?
   - Does it capture the full intent of the ticket creator, not just the literal text?
   - Are there edge cases mentioned in the ticket that aren't handled?
   - Are there acceptance criteria that aren't met?
4. **Bug Detection**:
   - Look for logic errors and off-by-one mistakes
   - Check for null/undefined handling and type safety issues
   - Identify potential race conditions or timing issues
   - Verify error handling is comprehensive
   - Check for resource leaks (unclosed connections, memory leaks)
   - Look for broken edge cases and boundary conditions
5. **Security Review**:
   - Check for injection vulnerabilities (SQL, XSS, command injection)
   - Verify authentication and authorization are properly enforced
   - Look for sensitive data exposure (logging secrets, improper error messages)
   - Check for insecure dependencies or configurations
   - Verify input validation and sanitization
   - Look for CSRF, SSRF, or other web vulnerabilities if applicable
6. **Standards Compliance**:
   - Compare against coding standards found in knowledge/md files
   - Check for code re-use opportunities (are there existing utilities being duplicated?)
   - Verify naming conventions match the codebase
   - Check for proper abstraction and separation of concerns
   - Look for dead code or unnecessary complexity
   - Verify test coverage matches project standards
   - Check documentation requirements are met

<verification>
- All ticket requirements have been checked against the implementation
- The code has been reviewed for bugs and logic errors
- Security vulnerabilities have been assessed
- Adherence to codebase standards has been verified
- Code re-use opportunities have been identified
- Each finding has been documented with specific file/line references
</verification>
</phase>

<phase name="Feedback" id="3">
## Feedback Phase

1. Compile your review using the Output Format below
2. Categorize each finding by severity:
   - **Blocker**: Must be fixed before merge (security issues, bugs, missing requirements)
   - **Major**: Should be fixed, significantly impacts code quality
   - **Minor**: Nice to have, stylistic or minor improvements
   - **Nitpick**: Optional suggestions, won't block approval
3. Update the ticket using `update_issue` to add a comment with the review summary
4. Post review comments directly on the PR if GitHub access is available
5. Send a brief message to the user with the review summary and recommendation (approve/request changes)

## Output Format

Your review should include the following sections:

### Summary
- Overall assessment: Approve / Request Changes / Needs Discussion
- Number of findings by severity
- Brief description of the PR's purpose and scope

### Requirements Check
- ✅ or ❌ for each requirement/acceptance criterion
- Notes on partial implementations or edge cases

### Findings

For each issue found:
- **Severity**: Blocker/Major/Minor/Nitpick
- **Category**: Bug/Security/Standards/Requirements
- **Location**: File path and line number(s)
- **Description**: Clear explanation of the issue
- **Suggestion**: How to fix it (if applicable)

### Positive Observations
- Well-implemented aspects worth noting
- Good patterns or practices used

### Recommendations
- Summary of required changes (if any)
- Optional improvements to consider
- Questions for the author

<verification>
- All findings are categorized by severity and type
- Each finding includes specific file/line references
- The ticket has been updated with the review summary
- PR comments have been posted (if GitHub access available)
- User has been notified with the final recommendation
- Requirements checklist is complete
</verification>
</phase>

## Specifications

- The review must check all four areas: requirements, bugs, security, standards
- Each finding must include severity, category, location, and description
- The ticket must be updated with the review summary
- All ticket status transitions must be reflected in Linear
- Validation: The ticket should have a comment documenting the review; the user should receive a clear approve/reject recommendation

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

### Other MCPs
- If Notion or Confluence MCPs are available, use them to search for coding standards and guidelines

## Advice and Pointers

- **Keep all ticket comments extremely brief and terse** - write like a human, not an AI. No fluff, no verbose explanations. Just the essential information
- Focus on issues that matter - don't nitpick on minor style issues if the codebase doesn't have strict style guides
- When reviewing security, consider the context - an internal tool has different requirements than a public-facing API
- Look for patterns in the codebase before flagging something as non-standard
- If you find many issues, prioritize the most important ones in your summary
- Be constructive - suggest solutions, not just problems

## Forbidden Actions

- Do not make code changes or push commits
- Do not merge or approve the PR in GitHub (only provide recommendation)
- Do not send any messages to the user other than the specified messages at the end of each phase or if the user messages you
- Do not dismiss potential issues without investigation - document all findings
- Do not block on minor issues - categorize appropriately and let the author decide
- Removing or overriding attributes of the existing tickets without explicit instructions
