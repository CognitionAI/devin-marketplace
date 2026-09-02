---
name: database
description: Index of PlanetScale engine skills for MySQL, Postgres, Vitess, and Neki. Use to pick the right engine skill before planning schema changes, indexes, query tuning, migrations, sharding, or connection troubleshooting against a PlanetScale database.
---

# PlanetScale database skills

Pick the one engine skill that matches the database in front of you and follow it. Read only that skill; the engines disagree on enough details that mixing their guidance produces wrong advice.

## Pick an engine

| Database | Skill |
| --- | --- |
| MySQL-compatible, unsharded | `database-mysql` |
| PlanetScale Postgres | `database-postgres` |
| Vitess (sharded MySQL, keyspaces, VSchema) | `database-vitess` |
| Neki (sharded Postgres) | `database-neki` |

If you do not know which engine backs the database, determine it with the PlanetScale MCP server before choosing — do not infer it from the connection string, ORM, or repository conventions.

## Skills

<!-- BEGIN GENERATED INDEX -->
| Skill | Path | Description |
| --- | --- | --- |
| `database-mysql` | `skills/database-mysql/SKILL.md` | Plan and review MySQL/InnoDB schema, indexing, query tuning, transactions, and operations. |
| `database-neki` | `skills/database-neki/SKILL.md` | Overview and information about Neki, the sharded Postgres product by PlanetScale. |
| `database-postgres` | `skills/database-postgres/SKILL.md` | PostgreSQL best practices, query optimization, connection troubleshooting, and performance improvement. |
| `database-vitess` | `skills/database-vitess/SKILL.md` | Vitess best practices, query optimization, and connection troubleshooting for PlanetScale Vitess databases. |
<!-- END GENERATED INDEX -->

## Related

Assessment, safety-review, and change-approval workflows live in the `planetscale` skill index.
