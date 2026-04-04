# Formatting

## Indentation
- 4 spaces — no tabs
- Opening brace at end of line; closing brace on its own line aligned with the opening construct:
  ```kotlin
  if (elements != null) {
      for (element in elements) {
          // ...
      }
  }
  ```

## Horizontal Whitespace
- Spaces around binary operators: `a + b` — except range-to: `0..i`
- No spaces around unary operators: `a++`
- Space between control-flow keywords and `(`: `if (`, `when (`, `for (`, `while (`
- No space before `(` in constructor, method declaration, or call: `class A(val x: Int)`, `foo(1)`
- No space after `(`, `[` or before `]`, `)`
- No space around `.` or `?.`: `foo.bar().filter { it > 2 }`
- Space after `//`: `// comment`
- No spaces around type parameter angle brackets: `class Map<K, V>`
- No spaces around `::`: `Foo::class`, `String::length`
- No space before `?` for nullable types: `String?`
- Avoid horizontal alignment — renaming an identifier should not require reformatting

## Colon
- Space **before** `:` when separating type from supertype, delegating to super/other constructor, or after `object`
- No space before `:` when separating declaration from its type
- Always space after `:`

## Functions
Long signature — one parameter per line, trailing `)` then `:` return type:
```kotlin
fun longMethodName(
    argument: ArgumentType = defaultValue,
    argument2: AnotherArgumentType,
): ReturnType {
    // body
}
```

Prefer expression body for single-expression functions:
```kotlin
fun foo() = 1        // good
fun foo(): Int { return 1 }  // bad
```

Expression body that doesn't fit on one line — `=` on first line, body indented 4 spaces:
```kotlin
fun f(x: String, y: String, z: String) =
    veryLongFunctionCallWithManyWords(andLongParametersToo(), x, y, z)
```

## Properties
Simple read-only — single line:
```kotlin
val isEmpty: Boolean get() = size == 0
```

Complex — `get`/`set` on separate lines:
```kotlin
val foo: String
    get() { /*...*/ }
```

Long initializer — break after `=`, indent 4:
```kotlin
private val defaultCharset: Charset? =
    EncodingRegistry.getInstance().getDefaultCharsetForPropertiesFiles(file)
```

## Control Flow
Multiline condition — curly braces always required; closing `)` with opening `{` on own line:
```kotlin
if (!component.isSyncing &&
    !hasAnyKotlinRuntimeInScope(module)
) {
    return createKotlinNotConfiguredPanel(module)
}
```

`else`, `catch`, `finally`, `while` on the same line as preceding `}`:
```kotlin
if (condition) {
    // body
} else {
    // else part
}
```

`when` — separate multi-line branches with a blank line; single-line branches without braces:
```kotlin
when (foo) {
    true -> bar()   // good
    false -> { baz() } // bad
}
```

## Method Calls
Long argument lists — break after `(`, indent 4, group closely related args:
```kotlin
drawSquare(
    x = 10, y = 10,
    width = 100, height = 100,
    fill = true
)
```
Space around `=` in named arguments.

## Chained Calls
`.` or `?.` on the next line, single indent:
```kotlin
val anchor = owner
    ?.firstChild!!
    .siblings(forward = true)
    .dropWhile { it is PsiComment || it is PsiWhiteSpace }
```

## Lambdas
- Spaces around `{}` and around `->`:  `list.filter { it > 10 }`
- Single lambda argument: pass outside parentheses
- No space between label and `{`: `ints.forEach lit@{ ... }`
- Multiline: parameter names on the first line, `->` then newline:
  ```kotlin
  appendCommaSeparated(properties) { prop ->
      val propertyValue = prop.get(obj)
  }
  ```
- Very long parameter list: arrow on its own line

## Trailing Commas
Encouraged at declaration sites (constructor params, function params, enum entries, destructuring):
```kotlin
class Person(
    val firstName: String,
    val lastName: String, // trailing comma
)
```
Optional at call sites — use judgment.

## Semicolons
Omit semicolons wherever possible.
