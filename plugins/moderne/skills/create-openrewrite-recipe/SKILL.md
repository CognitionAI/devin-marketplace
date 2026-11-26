---
name: create-openrewrite-recipe
description: Write, fix, or test an OpenRewrite recipe, including declarative YAML, Refaster templates, Java visitors, and scanning recipes. Use when a task asks for a new or changed recipe. Do not use to run an existing recipe.
---

# Create an OpenRewrite recipe

Search the [recipe catalog](https://codegenomeproject.org/recipes) first, or call `searchForRecipe` if the Moderne MCP server is connected. Write a recipe only when no existing one does the job.

## Choose the recipe type

Use the simplest type that works.

| Need | Type |
| --- | --- |
| Compose or configure existing recipes | Declarative YAML |
| Replace one expression or statement with another | Refaster template |
| Make a decision that depends on the surrounding code | Imperative Java |
| Generate files, or see every source file before changing any | `ScanningRecipe` |

## Set up the project

Start a new project from [rewrite-recipe-starter](https://github.com/moderneinc/rewrite-recipe-starter). In an existing project, import `org.openrewrite.recipe:rewrite-recipe-bom` and add `org.openrewrite:rewrite-test` as a test dependency.

Rewrite modules are distributed through the Code Genome Project repository, which requires authentication. Follow the [development environment guide](https://docs.openrewrite.org/authoring-recipes/recipe-development-environment). If dependencies do not resolve, report that instead of guessing at versions or repositories.

## Declarative recipes

Put the YAML in `src/main/resources/META-INF/rewrite/`.

```yaml
---
type: specs.openrewrite.org/v1beta/recipe
name: com.yourorg.UseNewLogger
displayName: Use the new logger
description: Replaces the old logger type with the new one.
recipeList:
  - org.openrewrite.java.ChangeType:
      oldFullyQualifiedTypeName: com.yourorg.OldLogger
      newFullyQualifiedTypeName: com.yourorg.NewLogger
```

## Refaster templates

Write a class with `@BeforeTemplate` and `@AfterTemplate` methods. The `rewrite-templating` annotation processor generates the recipe at build time. See [the Refaster guide](https://docs.openrewrite.org/authoring-recipes/refaster-recipes).

## Imperative recipes

Extend `org.openrewrite.Recipe` and implement `getDisplayName()`, `getDescription()`, and `getVisitor()`. Declare options with `@Option`, and use Lombok's `@Value` with `@EqualsAndHashCode(callSuper = false)` so the recipe stays immutable and serializable.

Follow these rules:

* Change nothing when you cannot prove a change is safe, and keep each change minimal.
* Return a new visitor from every `getVisitor()` call, and keep no mutable state on the recipe.
* Never mutate an LST. Use `with` methods, and return the same object when nothing changes.
* Create code with `JavaTemplate` rather than building LST elements by hand.
* Add a `Preconditions.check` when the recipe applies only to some source files.
* Decide deliberately whether each `visit` method calls `super`, because that controls traversal.
* Pass state within a visitor with cursor messages, and across files with a `ScanningRecipe`.
* Finish the work in one cycle unless a later cycle is essential.
* Remember that a repository can have several modules, so do not assume one project per run.

## Test the recipe

Every recipe needs a test with a change and a test with no change. One string in a source spec asserts no change, and two strings assert before and after.

```java
class UseNewLoggerTest implements RewriteTest {
    @Override
    public void defaults(RecipeSpec spec) {
        spec.recipe(new UseNewLogger());
    }

    @Test
    void replacesOldLogger() {
        rewriteRun(
            java(
                """
                class A { com.yourorg.OldLogger logger; }
                """,
                """
                class A { com.yourorg.NewLogger logger; }
                """
            )
        );
    }
}
```

* For a declarative recipe, use `spec.recipeFromResources("com.yourorg.UseNewLogger")`.
* When the before code needs a library, use `spec.parser(JavaParser.fromJavaVersion().classpath("library-name"))`. The after code does not need it on the classpath.

Run the tests with the project's build tool. The recipe is finished when they pass.

## References

* [Recipe conventions](https://docs.openrewrite.org/authoring-recipes/recipe-conventions-and-best-practices)
* [Writing a Java recipe](https://docs.openrewrite.org/authoring-recipes/writing-a-java-refactoring-recipe)
* [Recipe testing](https://docs.openrewrite.org/authoring-recipes/recipe-testing)
* [Data tables](https://docs.openrewrite.org/authoring-recipes/data-tables)
