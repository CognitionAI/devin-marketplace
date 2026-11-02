---
name: read-prethink-context
description: Read Moderne Prethink files in `.moderne/context/` before refactoring, writing tests, or adding a feature. Use when a repository has that directory, or when asked about its architecture, dependencies, code quality, or risky untested code.
---

# Read Prethink context

Prethink is generated, structured information about a repository. Check for `.moderne/context/` before exploring the code. If it does not exist, continue with normal exploration, and tell the user only if the context would materially help.

## Find the right file

Read only the files that match the task and exist in this repository.

| Task | Files |
| --- | --- |
| Understand services and integrations | `architecture.md`, `calm-architecture.json`, `service-endpoints.csv`, `database-connections.csv` |
| Check dependencies | `dependencies.md`, `dependency-usage.csv`, `dependency-list-report.csv` |
| Plan a refactor | `method-quality-metrics.csv`, `class-quality-metrics.csv`, `package-quality-metrics.csv`, `code-smells.csv` |
| Write or fix tests | `test-gaps.csv`, `test-mapping.csv`, `test-quality.csv` |
| Match local style | `coding-conventions.csv`, `error-handling.csv` |
| Understand unfamiliar code | `method-descriptions.csv`, `class-descriptions.csv` |

A Markdown file with the same name as a CSV describes that CSV's columns. Read it first.

## Use the context carefully

* Treat the files as a snapshot. When they disagree with the source code, trust the source code.
* Use the context to choose where to look, then confirm important facts in the code.
* Do not edit these files by hand. They are generated.

## Generate missing context

The recipe `io.moderne.prethink.UpdatePrethinkContextStarter` generates this directory and updates the repository's agent configuration files. Run it only when the user asks. See the [Prethink guide](https://docs.moderne.io/user-documentation/agent-tools/prethink/).
