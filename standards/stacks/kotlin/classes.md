# Classes and Structure

## Source File Organization
- Multiple declarations in one file are encouraged when they are semantically related and the file stays under a few hundred lines
- Extension functions relevant to all clients of a class go in the same file as the class
- Client-specific extensions go next to the client code — do not create a file just to collect all extensions for a class

## Directory Structure
- Follow the package structure; omit the common root package prefix
- `org.example.kotlin.network.socket` → `network/socket/` under source root
- On JVM mixed projects: Kotlin files live alongside Java files in the same source root

## Class Layout (order)
1. Property declarations and initializer blocks
2. Secondary constructors
3. Method declarations
4. Companion object

- Do not sort methods alphabetically or by visibility
- Do not separate regular methods from extension methods
- Put related logic together, top-to-bottom readable order
- Nested classes go next to the code that uses them; externally-used nested classes go after the companion object

## Interface Implementation
- Implement members in the same order as declared in the interface; intersperse additional private helpers as needed

## Overloads
- Always put overloads adjacent to each other in the class

## Class Headers
Short header — single line:
```kotlin
class Person(id: Int, name: String)
```

Long header — one parameter per line, closing `)` on its own line, superclass on same line as `)`:
```kotlin
class Person(
    id: Int,
    name: String,
    surname: String
) : Human(id, name) { /*...*/ }
```

Multiple supertypes — superclass first, then interfaces each on their own line:
```kotlin
class Person(
    id: Int,
    name: String,
    surname: String
) : Human(id, name),
    KotlinMaker { /*...*/ }
```

Long supertype list — break after colon, align all supertypes:
```kotlin
class MyFavouriteVeryLongClassHolder :
    MyLongHolder<MyFavouriteVeryLongClass>(),
    SomeOtherInterface,
    AndAnotherOne {

    fun foo() { /*...*/ }
}
```

- Use 4-space indent for constructor parameters (consistent with body properties)
- When class header is long, add a blank line before the body or put `{` on its own line

## Modifiers Order
```
public / protected / private / internal
expect / actual
final / open / abstract / sealed / const
external
override
lateinit
tailrec
vararg
suspend
inner
enum / annotation / fun
companion
inline / value
infix
operator
data
```
- Place all annotations before modifiers
- Omit redundant modifiers (e.g., `public`) in non-library code

## Annotations
- On a separate line before the declaration, same indentation:
  ```kotlin
  @Target(AnnotationTarget.PROPERTY)
  annotation class JsonExclude
  ```
- Multiple no-argument annotations may share a line:
  ```kotlin
  @JsonExclude @JvmField
  var x: String
  ```
- Single no-argument annotation may be on the same line as the declaration:
  ```kotlin
  @Test fun foo() { /*...*/ }
  ```

## File Annotations
- After file comment, before `package`, separated from `package` by a blank line:
  ```kotlin
  /** License */
  @file:JvmName("FooBar")

  package foo.bar
  ```
