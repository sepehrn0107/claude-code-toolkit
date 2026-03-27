# Go Standards

Standards for Go projects.

_To be populated via `/retrospective` after working on a Go project, or written manually._

## Topics to Cover
- Package and module organization
- Error handling conventions (wrap with context, don't ignore)
- Interface design (keep interfaces small, define at point of use)
- Concurrency patterns (channels vs. mutexes, goroutine lifecycle)
- Testing (table-driven tests, testify or stdlib)
- Logging (slog or zerolog)
- Build and tooling (golangci-lint, govulncheck)
- HTTP service patterns (standard library vs. chi/gin/echo)
