# Naming Conventions

## Packages
- Always lowercase, no underscores: `org.example.project`
- Avoid multi-word names; if needed, concatenate or use camelCase: `org.example.myProject`

## Classes and Objects
- `UpperCamelCase`: `DeclarationProcessor`, `EmptyDeclarationProcessor`

## Functions, Properties, Local Variables
- `lowerCamelCase`, no underscores: `processDeclarations()`, `declarationCount`

## Factory Functions
- May share the name of the abstract return type they create:
  ```kotlin
  interface Foo { /*...*/ }
  fun Foo(): Foo { return FooImpl() }
  ```

## Test Methods
- Backtick-enclosed spaces allowed in tests only: `` `ensure everything works`() ``
- Underscores also allowed in test code: `ensureEverythingWorks_onAndroid()`

## Constants
- `SCREAMING_SNAKE_CASE` for `const val`, top-level or object `val` with immutable data:
  ```kotlin
  const val MAX_COUNT = 8
  val USER_NAME_FIELD = "UserName"
  ```
- `camelCase` for properties holding objects with behavior or mutable state:
  ```kotlin
  val mutableCollection: MutableSet<String> = HashSet()
  ```
- Singleton-reference properties may use the same style as `object` declarations:
  ```kotlin
  val PersonComparator: Comparator<Person> = /*...*/
  ```

## Enum Constants
- Either `SCREAMING_SNAKE_CASE` or `UpperCamelCase` — pick one and be consistent per enum

## Backing Properties
- Prefix private backing property with `_`:
  ```kotlin
  class C {
      private val _elementList = mutableListOf<Element>()
      val elementList: List<Element>
          get() = _elementList
  }
  ```

## Acronyms
- Two-letter acronyms: both uppercase — `IOStream`
- Longer acronyms: capitalize first letter only — `XmlFormatter`, `HttpInputStream`

## Naming Guidance
- Class name: noun or noun phrase — `List`, `PersonReader`
- Method name: verb or verb phrase — `close`, `readPersons`; use past tense for non-mutating variants (`sort` mutates, `sorted` returns copy)
- Avoid meaningless words: `Manager`, `Wrapper`, `Util`

## Files
- Single class/interface per file: name matches the class — `DeclarationProcessor.kt`
- Multiple top-level declarations: descriptive `UpperCamelCase` name — `ProcessDeclarations.kt`
- Avoid `Util` in file names
- Multiplatform platform-specific files: suffix with source set — `Platform.jvm.kt`, `Platform.android.kt`
