# Code Review Standards

Code review is the primary mechanism for catching bugs, sharing knowledge, and
maintaining quality. These standards apply to both authors and reviewers.

---

## As the Author

### Before Opening a PR

Do a self-review first. Read your own diff as if you're the reviewer.

- [ ] Does this do exactly what the ticket/task describes — no more, no less?
- [ ] Are there any obvious bugs, edge cases, or off-by-one errors?
- [ ] Is there dead code, debugging artifacts, or commented-out blocks to remove?
- [ ] Are there hardcoded values, secrets, or magic numbers that should be constants?
- [ ] Does the diff include unrelated changes? (If yes, split into separate PRs)
- [ ] Do all existing tests pass?
- [ ] Are there new tests for new behaviour?

### Writing a Good PR Description

A PR description is a letter to your reviewers. Don't make them reverse-engineer your intent.

Include:
- **What**: A 1-2 sentence summary of what changed
- **Why**: The motivation — what problem does this solve?
- **How** (if non-obvious): The approach taken, especially for complex changes
- **Testing**: How you verified the change works
- **Screenshots** (for UI changes)

### PR Size

Small PRs get better reviews. Large PRs get rubber-stamped.

- Aim for under 400 lines of diff for feature work
- Infrastructure or refactoring PRs can be larger if purely mechanical
- If a feature requires 1000+ lines, break it into sequential PRs

---

## As the Reviewer

### What to Look For

Review in this order — each layer builds on the previous:

1. **Correctness**: Does it do what it's supposed to? Are there edge cases, race conditions, off-by-ones?
2. **Tests**: Are there adequate tests? Do they test behaviour, not implementation?
3. **Security**: Input validation, auth checks, secret handling, injection risks (see security standards)
4. **Design**: Is the abstraction right? Does it fit the existing architecture?
5. **Readability**: Is it clear what this code does and why? Are names accurate?
6. **Style**: Formatting, naming conventions, code standards (lowest priority — let the linter handle most of this)

### Giving Feedback

Be specific and constructive. Your goal is to improve the code, not to demonstrate your knowledge.

**Label your comments by severity:**
- `[blocking]` — Must be addressed before merge (bug, security issue, wrong approach)
- `[suggestion]` — Worth considering, but author's call
- `[nit]` — Minor style/naming preference; fine to ignore or batch-fix

**Be concrete:**
```
# Vague (unhelpful):
"This function is too complex."

# Specific (helpful):
"[suggestion] This function has 4 responsibilities. Consider splitting the validation
and the persistence into separate functions to make each independently testable."
```

**Suggest, don't demand** (for non-blocking items):
```
# Demand:
"Rename this to userEmail."

# Suggestion:
"[nit] `email` is ambiguous here — `userEmail` might be clearer since we also have `senderEmail` nearby."
```

**Acknowledge good work.** If you see something clever or well-done, say so. Reviews aren't only for criticism.

### Turnaround Time

- Reviews should be completed within one business day
- If you can't review within that window, say so — the author shouldn't be blocked silently
- For urgent fixes, explicitly ask someone to review within the hour

---

## As the Author Receiving Feedback

- **Don't take it personally.** The reviewer is commenting on the code, not you.
- **Respond to every comment.** Either fix it, explain why you disagree, or ask for clarification.
- **Don't silently ignore.** If you choose not to apply a suggestion, say why.
- **Ask for clarification** if a comment is unclear — don't guess at what was meant.
- **When you disagree**: State your reasoning. If you can't resolve it, escalate to a team discussion rather than a prolonged back-and-forth.

---

## Merging

- The author merges (not the reviewer), once all blocking comments are addressed
- Don't merge with unresolved blocking comments
- Squash merge for feature branches to keep history clean; preserve commits for large refactors
- Delete the branch after merging

---

## Anti-Patterns to Avoid

**As a reviewer:**
- **Rubber stamping**: Approving without actually reading the diff
- **Nitpicking everything**: 30 nit comments buries the 2 important ones
- **Drive-by rewriting**: Suggesting a complete rewrite when the approach is fine
- **Scope creep in review**: "While you're in here, can you also fix X?" — open a new ticket
- **Personal style over team standards**: Enforce the agreed style guide, not your personal preferences

**As an author:**
- **Opening a PR too early**: WIP code in review wastes everyone's time — use draft PRs
- **Ignoring the feedback**: Merging without addressing blocking comments
- **Defensive responses**: Treating questions as attacks
- **Mega PRs**: A 3000-line PR will get a poor review no matter how good the reviewer is
