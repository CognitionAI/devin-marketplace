---
name: pr-review-status
description: >
  Report Strix pull request security reviews and the findings that block a
  merge. Use when the user asks "did Strix review my PR", "what is blocking
  PR 42", "show open PR review findings", or wants Strix to review a specific
  pull request.
---

# Strix PR review status

Report review verdicts and the open findings on pull requests.

## When

- The user wants the security status of one or more pull requests.
- The user wants Strix to review a pull request that has no review yet.

Do not use this skill for scan findings (triage-findings).

## How

1. Call `list_pr_reviews` to load the most recent reviews. Pass `repository_full_name` when the user names a repository.
2. Call `list_pr_review_findings` with `pr_state` `open` (and `repository_full_name` when given) and summarize what blocks each merge.
3. For one pull request, call `get_pr_review` to load the verdict and every finding.
4. Present a table with the pull request, the repository, the verdict, and the count of open findings by severity.
5. Close with the pull requests that need attention first and why.

## Fixing a review finding

- When the user works in the reviewed repository, fix the finding on the pull request branch, add a test, and push. Strix reviews the new commits automatically when the repository has PR reviews enabled.
- Call `get_pr_review_settings` to check whether automatic reviews are on. Change them with `update_pr_review_settings` only when an admin asks.

## Starting a review

- Call `start_pr_review` only when the user asks for a review of a specific pull request. The repository must be connected in Strix. Check with `list_repositories` first.
