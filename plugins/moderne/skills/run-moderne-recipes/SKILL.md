---
name: run-moderne-recipes
description: Find and run OpenRewrite recipes, query their results, and search code across a Moderne organization with the Moderne MCP tools. Use for organization-wide migrations, impact analysis, or code search on repositories in a Moderne tenant.
---

# Run Moderne recipes

These tools work on repositories already ingested into the user's Moderne tenant, and they use the user's own access. They do not read the local checkout. The server is in beta, so trust its current tool list when it differs from this guide.

## Choose an organization

Most tools take an `organizationId`. If the user did not name one, call `listOrganizations` and ask them to choose. `runRecipe` does not accept the root organization, `ALL`.

To target specific repositories, group them with `createUserOrganization`. Ask before calling `updateUserOrganization` or `deleteUserOrganization`.

## Run a recipe

1. Call `searchForRecipe` to find the recipe.
2. Call `describeRecipeOptions` and `describeRecipeDataTables` to learn its inputs and outputs.
3. Call `runRecipe` with `recipeId`, `organizationId`, `dataTableNames`, and any `options`. Do not set `email`.
4. Call `runRecipe` again with the returned `recipeRunId` until `terminal` is `true`. Each call returns within about twenty seconds.
5. Call `processDataTableSql` with the run ID to answer questions about the results.

If a response has no `structuredContent`, the run failed before it was queued, so there is nothing to resume. If the final status is `ERROR` or `CANCELED`, report `errorMessage`.

## Search code

* Use `codeSearch` to find matches, and `readFile` to read more of a matching file.
* Use `codeSearchSql` for counts, distributions, and joins.
* Use `findMethods`, `findTypes`, and `findImplementations` for type-aware lookups.
* Use `usageExamples` to see how a method, constructor, or program is usually called.

## Report results accurately

No tool commits code or opens a pull request, so a finished run has not changed any repository. To deliver changes, the user can use the Moderne Platform or the API's `commit` mutation.

See the [remote server guide](https://docs.moderne.io/user-documentation/agent-tools/mcp/remote-server/).
