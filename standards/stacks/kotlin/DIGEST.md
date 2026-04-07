# Kotlin Standards Digest

> Compact reference for orchestration. Sub-agents load the specific full files they need.
> Source: https://kotlinlang.org/docs/coding-conventions.html (v2.3.20, April 2026)

## naming → standards/stacks/kotlin/naming.md
- Packages: all-lowercase no underscores; classes/objects: `UpperCamelCase`; functions/vars: `lowerCamelCase`
- Constants (`const val`, top-level immutable `val`): `SCREAMING_SNAKE_CASE`; backing props: `_underscore` prefix
- Files: one class → match class name; multi-declaration → descriptive `UpperCamelCase.kt`

## classes → standards/stacks/kotlin/classes.md
- Class body order: properties → secondary constructors → methods → companion object
- Long headers: one param per line, `)` on own line, supertype on same line as `)`
- Modifier order: visibility → expect/actual → final/open/abstract/sealed → external → override → ... → data

## formatting → standards/stacks/kotlin/formatting.md
- 4-space indent, no tabs; opening `{` at end of line; `else`/`catch`/`finally` on same line as `}`
- Prefer expression bodies (`fun foo() = 1`); omit `Unit` return type; omit semicolons
- Chained calls: `.` / `?.` on next line with single indent; lambdas: spaces inside `{ }` and around `->`

## idioms → standards/stacks/kotlin/idioms.md
- Prefer `val` over `var`; use immutable collection interfaces (`List`, `Set`, `Map`)
- Default parameters over overloads; `it` in short non-nested lambdas; named args for booleans/same-type params
- `if` for binary, `when` for 3+ options; prefer expression form of `if`/`when`/`try`

## testing → standards/stacks/kotlin/testing.md
- JUnit 5 + Kotest matchers + MockK; backtick names for descriptive test methods
- `runTest {}` for coroutines; inject `TestDispatcher` to control time
- Regression test before every bug fix; cover business logic branches, not framework behavior
