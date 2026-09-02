# Evals

Fixture-agnostic evaluation scenarios for this skill, one per migration shape. They carry no fixture of their own — to run them you provide:

- **A fixture app** matching a case's `fixture_requirements`: a working codebase that consumes GitLab feature flags the way the case describes, with known-good behavior you can capture as an oracle before migrating.
- **A reachable Unleash target** (v8+) with credentials appropriate to the provisioning mechanism under test.
- Optionally, **GitLab management-API credentials** so the inventory phase can use the live source instead of code/manifests.

## Running and grading

Run each case in an isolated session/agent: invoke the skill against the fixture, then have a grader check every `expected_behavior` item with concrete evidence (server state read-backs, parity diffs, greps, process environment). A case passes only when every item holds; report per-item PASS/FAIL.

## Skipping cases via prompt

Case selection is prompt-driven. The eval-run prompt may say:

- `skip: <ids or shapes>` — run everything except the listed cases
- `only: <ids or shapes>` — run just the listed cases

The runner must honor these directives and report skipped cases as **SKIPPED** in the results — never silently drop them.
