---
name: dataprime-help
description: Help build and debug DataPrime queries — syntax guidance, field discovery, and interactive query refinement
argument-hint: "<what you want to query, or a broken query to fix>"
triggers:
  - user
  - model
---

Help the user write, debug, or optimise a DataPrime query. DataPrime is Coralogix's query language for logs, spans, and datasets.

## If the user has a query that isn't working

1. Use `list_dataprime_constructs` and `describe_dataprime_construct` to check the syntax of the commands and functions they used.
2. Use `show_dataprime_command_details` for detailed syntax and examples of specific commands.
3. Identify the issue (wrong field path, incorrect function usage, syntax error) and suggest the fix.
4. Use `query_dataprime` to test the corrected query and confirm it returns results.

## If the user wants to build a new query

1. Understand what they want to find. Ask a clarifying question if the intent is ambiguous.
2. Use `list_datasets` to identify the right data source (logs, spans, or a named dataset).
3. Use `search_for_fields` to discover the correct field paths for the data they want to filter or extract.
4. Use `get_system_dataset_info` if querying a system dataset to understand its schema.
5. Build the query incrementally:
   - Start with the `source` and basic `filter` to confirm data exists.
   - Add aggregations, grouping, or transformations.
   - Use `query_dataprime` at each step to validate.
6. If the user needs a command or function you're unsure about, use `list_dataprime_commands` to browse available options and `describe_dataprime_construct` for details.

## If the user wants to optimise a query

1. Review the query for common performance issues:
   - Missing or broad time filters.
   - Unnecessary `*` selections when specific fields would suffice.
   - Aggregations that could be pushed earlier in the pipeline.
2. Use `query_dataprime` to time the original and optimised versions.

## General guidance

- Always show the user the query before running it.
- Explain what each part of the query does.
- When suggesting field paths, use `search_for_fields` rather than guessing — field naming varies across applications.
- For complex queries, build them up step by step rather than writing the whole thing at once.
