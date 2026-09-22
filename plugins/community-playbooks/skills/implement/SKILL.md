---
name: implement
description: "Linear: Implement."
metadata:
  devin:
    from_playbook: true
    playbook_id: "playbook-b6ba73c577084d2392720a2abf51dc26"
    playbook_macro: "!implement"
    playbook_title: "Linear: Implement"
    playbook_access: "community"
---

# Implement

## Overview

This playbook guides the process of taking a Linear ticket from initial scoping through implementation to final review. The workflow ensures proper context gathering, quality implementation, and thorough code review before delivery. The agent uses the Linear MCP to manage ticket status and communication throughout.

## What's Needed From User

- Linear ticket URL or ticket ID (e.g., `ENG-123` or `https://linear.app/team/issue/ENG-123/...`)
- Repository access for the codebase where changes will be made

<phase name="Disambiguation" id="1">
## Disambiguation Phase

Think about the full user intent. Tickets are sometimes sparse. Make sure you disambiguate to the full scope that the user intended.

1. Fetch the ticket details using the Linear MCP `get_issue` tool with the ticket ID
2. **Review all comments and attachments on the ticket** - comments often contain critical context, clarifications, or updated requirements that aren't in the main description. Attachments may include designs, screenshots, or specifications.
3. Before diving into code: use the devin MCP to get a high-level understanding of the relevant systems and architecture. Use `ask_wiki_question` to learn about the relevant systems – send queries for multiple repos that could be relevant to get the full picture. Use `read_wiki_contents` to then get a better understanding how different parts of the codebase connect to each other.
4. Gather additional context to understand what the ticket means and refers to:
   - Look at past tickets in the same project and from the same author to understand patterns and terminology
   - Search for related commits and PRs (by author and content) that may provide context on the affected systems
   - Check any linked documents, designs, or parent tickets
   - Investigate the actual code
5. Identify any ambiguity in what the ticket refers to or asks for, including jargon or project-specific terms and use all means necessary to answer this yourself
6. If there is critical ambiguity you are unable to resolve: Send a brief message with the specific clarifying questions, then stop and wait for answers
7. If the ticket's meaning is clear: proceed to the Implementation phase (after completing verification)

<verification>
- Are you thinking about the right repo? Does this intent actually cover multiple repos?
- Is this a frontend change? Or backend? Infra? all the above? Ensure you are 
- What is the change in user experience that the author intended? Does your proposal achieve that intent fully?
- Are you making shortcuts or proposing oversimplified fixes? You should not be lazy but ensure you are doing things properly and cleanly
- The scope covers the full user intent, not just the literal ticket text
- Did you try everything in your power to resolve ambiguous aspects before asking the user for help?
- You are smart so you can make good assumptions if you researched them well. Don't block on the user for preferences. Just simulate what the user would want and do that.
- Did you review all comments and attachments on the ticket?
</verification>
</phase>

<phase name="Implementation" id="2">
## Implementation Phase

1. Use `list_issue_statuses` with the team from the issue to discover available status names, then update the ticket status to "In Progress" (or equivalent) using `save_issue`
2. Deeply research the codebase to form a thorough implementation plan:
   - Identify all affected files and modules
   - Trace data flow and control flow through the affected systems
   - Map callers and callees of functions/methods that will be modified
   - Understand existing patterns and architectural constraints
3. Create a feature branch following the repository's branching conventions
4. Implement the changes according to the scoped requirements and proposed approach
    - Use the LSP (goto_definition, goto_references, hover_symbol) to verify types and function signatures are correct
    - Ensure all callers/callees identified in scoping are properly updated
5. Write or update tests to cover the new functionality where applicable
6. Run lint checks and fix any issues
7. Run tests locally if possible to verify the implementation works correctly
8. Commit changes with clear, descriptive commit messages referencing the ticket ID
9. Push the branch and create a pull request with a clear description linking to the ticket
10. Update the ticket using `save_issue` to add the PR link via the `links` parameter and change status to "For Review" (or equivalent)
11. Send a brief message with the PR link and a brief summary of changes made

<verification>
- All affected files and callers/callees have been updated
- The PR follows best coding practices: re-use existing code, follow existing patterns, clean up code that is now unused or can be consolidated, etc. Don't take shortcuts.
- Tests have been written or updated for new functionality
- Lint checks pass
- PR has been created with clear description linking to the ticket
</verification>
</phase>

<phase name="Iteration" id="3">
## Iteration Phase

1. Conduct a thorough self-review of your own PR diff against:
    - The original ticket requirements
    - The verification criteria from this playbook
    - Engineering best practices:
      - Follows existing patterns and naming conventions
      - Proper error handling consistent with the codebase
      - No dead code or unnecessary abstractions introduced
      - Backwards compatibility preserved (if applicable)
2. If issues are found during self-review: fix them, push updates, and repeat the review
3. Wait for CI checks to complete (if available) and ensure they pass. For CI of code review bots like coderabbit, graphite, and devin-ai-integration, you MUST also view the actual comments left by those bots since the CI jobs for these always show up as "passed" but they might still have reported issues.
4. Monitor for PR comments from human and bot reviewers:
    - Resolve all PR comments from human reviewers
    - For bot reviewers, use your own judgement to determine if it's an actual bot (e.g., CI bots, linters, security scanners) vs a human with a bot-like name
    - Address legitimate bot feedback (lint errors, security issues, test failures)
    - Use judgement on stylistic bot suggestions - fix if they improve code quality, otherwise explain why you're not addressing them
5. If there was actionable feedback, after addressing it, push changes and wait for CI to pass again. Move back to step 3 of this phase.
6. Once the review passes and all comments are resolved: send a final brief message confirming the PR is ready for human review

<verification>
- Thorough self-review was conducted against original requirements and verification criteria
- All acceptance criteria from the ticket are addressed
- Code follows existing patterns and conventions
- All PR comments from human reviewers have been resolved
- Bot reviewer feedback has been triaged and addressed appropriately
- CI checks pass after all iterations
- Reviewed comments from code review bots like graphite, coderabbit, and devin-ai-integration even if the corresponding CI actions pass
- Final comment posted to ticket confirming PR is ready
</verification>
</phase>

## Specifications

- The PR must address all requirements specified in the ticket
- Code must pass lint checks and any existing tests
- The ticket must be updated with the PR link before marking as ready for review
- All ticket status transitions must be reflected in Linear
- Validation: The PR should pass CI checks; the ticket should have comments documenting the scoping analysis and final PR link


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

Note: There is no `search` tool on the Devin MCP. Use `ask_wiki_question` instead.
IMPORTANT: there is also a deepwiki MCP that is similar. DO NOT USE IT. Only use the Devin MCP. Because the Devin MCP allows you to access your private repos. The Deepwiki MCP only does public repos.

## Advice and Pointers

- **Keep all ticket comments extremely brief and terse** - write like a human, not an AI. No fluff, no verbose explanations. Just the essential information
- When fetching ticket details, also check for any linked documents or parent tickets that may contain additional context
- If the ticket has sub-tasks, consider whether they should be addressed in the same PR or separately
- For the self-review phase, read the diff as if you were a reviewer unfamiliar with the changes

## Forbidden Actions

- Do not start implementation if there are blocking questions
- Do not push directly to the main branch
- Do not mark the ticket as complete/done - leave that for human verification after PR merge
- Do not skip the self-review phase even if confident in the implementation
- Do not send any messages to the user other than the specified messages at the end of each phase or if the user messages you
- Removing or overriding attributes of the existing tickets without explicit instructions
