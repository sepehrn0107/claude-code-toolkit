# Security Standards

Based on OWASP Top 10 and general secure development practices.

## Input Validation
- Validate all input at system boundaries (HTTP, CLI, file reads, env vars)
- Whitelist valid inputs rather than blacklisting bad ones
- Never trust user input in SQL queries, shell commands, or file paths
- Sanitize before storage; escape before display

## Secrets Management
- Never hardcode secrets, tokens, or credentials in source code
- Use environment variables or a secrets manager
- Never commit `.env` files with real values — use `.env.example` instead
- Rotate secrets that may have been exposed immediately

## Common Vulnerabilities
- **SQL Injection**: Use parameterized queries or ORMs, never string interpolation
- **XSS**: Escape all user-generated content before rendering
- **CSRF**: Use tokens for state-changing requests
- **SSRF**: Validate and restrict outgoing HTTP destinations
- **Path Traversal**: Canonicalize and validate file paths before access
- **Insecure Deserialization**: Avoid deserializing untrusted data

## Authentication & Authorization
- Use established auth libraries — don't roll your own crypto
- Hash passwords with bcrypt or argon2, never MD5 or SHA1
- Enforce authorization at the service layer, not just the UI
- Apply least privilege: grant only what's needed

## Dependencies
- Keep dependencies up to date
- Audit for known vulnerabilities (`npm audit`, `pip-audit`, `govulncheck`, etc.)
- Prefer well-maintained, widely-used libraries over obscure ones
