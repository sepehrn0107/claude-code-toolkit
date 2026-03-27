# Testing Standards

## Test Pyramid

```
        /\
       /E2E\      — Few, slow, expensive — covers critical user paths only
      /------\
     / Integ. \   — Some — test at component/service boundaries
    /----------\
   /    Unit    \ — Many, fast, cheap — test logic in isolation
  /--------------\
```

## Principles
- Tests are first-class code: readable, maintainable, well-named
- Test behavior, not implementation — tests shouldn't need updates when refactoring internals
- A test that always passes is worthless
- Prefer real dependencies over mocks where practical (avoid mock/prod divergence)

## What to Test
- All business logic at unit level
- Integration points (DB, external APIs, file I/O) with real or containerized services
- Critical user flows end-to-end

## Coverage
- Coverage is a proxy, not a goal — 100% coverage with bad tests is worse than 70% with good ones
- Aim for high coverage on business logic; lower is acceptable on boilerplate
- Every bug fix must come with a regression test

## Test Naming
- Name tests to describe behavior: `should return 404 when user not found`
- Group related tests logically (describe blocks or test classes)
- Test files live next to the code they test (or in a mirrored `tests/` directory)
