# Testing

## Test Method Naming
- Use backtick-enclosed descriptive names (JVM/Android API 30+):
  ```kotlin
  @Test fun `ensure everything works`() { /*...*/ }
  ```
- Underscores allowed in test code: `ensureEverythingWorks_onAndroid()`
- Name should describe the scenario and expected outcome

## Framework
- JUnit 5 (`@Test`, `@BeforeEach`, `@AfterEach`) as the default on JVM
- [Kotest](https://kotest.io/) for data-driven or behavior-style tests
- [MockK](https://mockk.io/) for mocking — not Mockito (Kotlin-idiomatic)

## Structure
- Mirror the source package structure in test directories
- One test class per production class; suffix with `Test`: `UserServiceTest`
- Use `@Nested` classes or Kotest `context {}` blocks to group related scenarios

## Assertions
- Prefer `kotlin.test` assertions or Kotest matchers over raw JUnit asserts:
  ```kotlin
  assertEquals(expected, actual)
  actual shouldBe expected          // Kotest
  ```
- Assert one concept per test; multiple asserts are fine for the same concept

## Test Data / Fixtures
- Use builder functions or data class `copy()` to construct test data — avoid large constructor calls
- Prefer local `val` fixtures inside each test over shared mutable state
- Name fixture builders clearly: `aUser()`, `aValidOrder()`

## Coroutines
- Test suspending functions with `runTest {}` (kotlinx-coroutines-test):
  ```kotlin
  @Test
  fun `fetches user successfully`() = runTest {
      val result = repository.fetchUser(1)
      result shouldBe expectedUser
  }
  ```
- Inject `TestDispatcher` to control time in tests

## What to Test
- Unit: pure functions, domain logic, ViewModels/Presenters in isolation
- Integration: repository + real DB/network (use test containers or in-memory variants)
- Avoid testing Kotlin language behavior or framework internals

## Coverage
- Cover all business logic branches and error paths
- Every bug fix: write a failing regression test first, then fix
- Coverage % is a proxy — prioritize meaningful behavioral coverage over raw numbers
