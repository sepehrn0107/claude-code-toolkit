# Idiomatic Kotlin

## Immutability
- Prefer `val` over `var` for local variables and properties
- Use immutable collection interfaces (`List`, `Set`, `Map`) for non-mutated collections
- Use `listOf()`, `setOf()`, `mapOf()` — not `arrayListOf()`, `hashSetOf()`, etc.
  ```kotlin
  // Bad
  fun validateValue(actual: String, allowed: HashSet<String>) { ... }
  val allowedValues = arrayListOf("a", "b", "c")

  // Good
  fun validateValue(actual: String, allowed: Set<String>) { ... }
  val allowedValues = listOf("a", "b", "c")
  ```

## Default Parameter Values
Prefer default parameters over overloads:
```kotlin
// Bad
fun foo() = foo("a")
fun foo(a: String) { /*...*/ }

// Good
fun foo(a: String = "a") { /*...*/ }
```

## Type Aliases
Define a type alias when a functional type or parameterized type appears multiple times:
```kotlin
typealias MouseClickHandler = (Any, MouseEvent) -> Unit
typealias PersonIndex = Map<String, Person>
```

## Lambda Parameters
- Short, non-nested lambdas: use `it` convention
- Nested lambdas: always declare parameters explicitly

## Returns in Lambdas
- Avoid multiple labeled returns in a lambda — restructure for a single exit point
- If unavoidable, convert the lambda to an anonymous function
- Do not use a labeled return for the last statement in a lambda

## Named Arguments
Use named argument syntax when:
- Multiple parameters share the same primitive type
- Parameters are of `Boolean` type and their meaning isn't obvious from context
```kotlin
drawSquare(x = 10, y = 10, width = 100, height = 100, fill = true)
```

## Conditional Expressions
Prefer expression form of `try`, `if`, `when`:
```kotlin
return if (x) foo() else bar()
return when(x) {
    0 -> "zero"
    else -> "nonzero"
}
```

## if vs when
- `if` for binary conditions
- `when` for 3+ options

## Guard Conditions in when
Wrap multiple boolean expressions in guard conditions with parentheses:
```kotlin
when (status) {
    is Status.Ok if (status.info.isEmpty() || status.info.id == null) -> "no information"
}
```

## Nullable Boolean
Use explicit comparison — not truthiness:
```kotlin
if (value == true) { ... }
if (value == false) { ... }
```

## Loops
- Prefer `filter`, `map`, and other higher-order functions over explicit loops
- Exception: use `for` loop instead of `forEach` when the receiver isn't nullable
- Use `..<` for open-ended ranges:
  ```kotlin
  for (i in 0..<n) { /*...*/ }  // good
  for (i in 0..n - 1) { /*...*/ }  // bad
  ```

## Strings
- Prefer string templates over concatenation
- Prefer multiline strings over `\n` in regular strings
- Use `trimIndent()` for multiline strings without internal indentation; `trimMargin()` when internal indentation is needed
- Simple variable in template — no braces: `"$name"`; longer expressions — use braces: `"${children.size}"`

## Functions vs Properties
Prefer a property when the underlying algorithm:
- Does not throw
- Is cheap to calculate (or cached on first run)
- Returns the same result given the same object state

## Extension Functions
- Use liberally — if a function works primarily on an object, make it an extension
- Restrict visibility as much as makes sense (local, member, or private top-level)

## Infix Functions
- Declare `infix` only when both objects play a similar role (`and`, `to`, `zip`)
- Never `infix` if the function mutates the receiver

## Factory Functions
- Give factory functions distinct names that explain what's special: `fromPolar(angle, radius)` not `Point(...)`
- Only use the class name as the factory function name when there is truly no special semantics
- Prefer factory functions over multiple overloaded constructors that can't be reduced to default parameters

## Platform Types (Java interop)
- Explicitly declare Kotlin type for public functions returning platform types:
  ```kotlin
  fun apiCall(): String = MyJavaApi.getProperty("name")
  ```
- Explicitly declare type for class/package-level properties initialized from platform types

## Scope Functions
Use scope functions purposefully (refer to the Kotlin docs on scope functions):
- `let` — transform a nullable or chain after a non-null check
- `run` — execute a block with object as receiver, returning result
- `with` — call multiple methods on an object without repeating the reference
- `apply` — configure an object, returns the receiver
- `also` — side effects, returns the receiver

## Redundant Constructs to Omit
- Omit `: Unit` return type
- Omit semicolons
- Omit `public` modifier in non-library code

## Documentation Comments
- Place opening `/**` on its own line for multi-line KDoc; begin each line with `*`
- Short comments on a single line: `/** Short description. */`
- Prefer inline description over `@param`/`@return` tags; use tags only for lengthy descriptions
  ```kotlin
  // Good
  /**
   * Returns the absolute value of the given [number].
   */
  fun abs(number: Int): Int { /*...*/ }
  ```

## Library Code Extras
- Always explicitly specify member visibility
- Always specify function return types and property types
- Provide KDoc for all public members (except overrides that add no new documentation)
