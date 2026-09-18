---
name: fix-finding
description: >
  Fix a vulnerability that Strix found and prove the fix. Use when the user
  gives a Strix finding id or link, says "fix this Strix finding", "patch the
  SQL injection Strix found", "remediate STRIX-123", or asks to close a Strix
  vulnerability with a code change.
---

# Fix a Strix finding

Turn one Strix vulnerability into a reviewed code change, then let Strix confirm the fix.

## When

- The user names a finding id, a Strix vulnerability URL, or a scan plus a finding title.
- The finding has a code location in a repository you can edit.

Do not use this skill to triage a list of findings (triage-findings) or to start a new scan (run-scan).

## How

1. Call `get_vulnerability` with the finding id. Read `description`, `technical_analysis`, `evidence`, `remediation_steps`, `code_file`, `code_locations`, `code_before`, and `code_after`.
2. If the id is unknown, call `list_vulnerabilities` with `status` `open` and search by title or endpoint. Ask the user when more than one finding matches.
3. Call `list_vulnerability_http_exchanges` when you need the exact request that proved the issue. Reproduce the issue locally before you change code.
4. Locate the vulnerable code in the repository. Treat `code_after` and `remediation_steps` as a suggestion, not as the final patch. Fix the root cause, not only the reported endpoint.
5. Search the codebase for the same pattern and fix every instance.
6. Add or update a test that fails before the fix and passes after it. Run the project's lint and test commands.
7. Open a pull request. Put the finding id, the severity, and a plain-language summary of the root cause in the description. Do not paste secrets, tokens, or full proof-of-concept payloads that target production.
8. Call `update_vulnerability` with `status` `in_progress` and a `note` that links the pull request.
9. After the pull request merges and deploys, ask the user before you call `retest_vulnerability`. A retest sends traffic to the target and spends Strix credits. When the retest confirms the fix, Strix marks the finding `fixed`.

## Rules

- Never mark a finding `fixed`, `ignored`, or `not_affected` without a merged change or an explicit user decision. Record the reason in `note`.
- Never run `poc_script_code` against a system the user did not name as a test target.
- When `create_vulnerability_fix_pr` is callable and the user prefers a Strix-authored fix, offer it as an alternative. It opens a pull request from the Strix agent instead of from Devin.
