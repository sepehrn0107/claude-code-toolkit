# Debugging Standards

A systematic approach to diagnosing and fixing bugs. Random guessing wastes hours.
Follow this process instead.

---

## The Scientific Method for Bugs

Every debugging session is an experiment. Apply this loop:

1. **Reproduce** — Confirm you can trigger the bug reliably
2. **Isolate** — Narrow down where the bug lives
3. **Hypothesize** — Form a specific, falsifiable theory
4. **Test** — Run the smallest possible experiment to confirm or disprove it
5. **Fix** — Change only what's needed to address the confirmed cause
6. **Verify** — Confirm the bug is gone and nothing else broke

Never skip to step 5. Fixing without understanding the cause just moves the bug.

---

## Step 1: Reproduce First

You cannot reliably fix a bug you cannot reproduce.

- Find the exact inputs, state, and sequence of steps that trigger it
- If it's intermittent, find the condition that makes it consistent (concurrency? timing? data size?)
- Write the reproduction as a failing test before touching any code
- If you can't reproduce it, you're not ready to fix it

---

## Step 2: Read the Error Message — Actually Read It

The most common debugging mistake is skimming the error. Read the full message:

- What is the error type/code?
- What is the exact message? (don't paraphrase — read it)
- Where in the stack trace did it originate? (not just the top frame — find the first line in *your* code)
- What was the state at the time? (variable values in the trace, request context, etc.)

Most bugs are solved at this step.

---

## Step 3: Isolate with Binary Search

Once you know the symptom, eliminate half the problem space at each step.

- Does it happen in a fresh environment, or only in yours?
- Does it happen with minimal input, or only with complex input?
- Does it happen on a specific code path, or always?
- Does it happen in isolation, or only with other components?

Keep halving until you have the smallest possible reproduction.

---

## Step 4: Tools by Layer

Use the right tool for where the problem is:

| Layer | Tools |
|-------|-------|
| Logic / algorithms | Debugger with breakpoints, print/log statements, unit tests |
| Data / state | Inspect variables at runtime, add assertions, check DB state |
| Network / API | Browser network tab, `curl`, proxy (mitmproxy, Charles), server logs |
| Performance | Profiler (language-specific), `time` command, DB `EXPLAIN` / `EXPLAIN ANALYZE` |
| Concurrency | Thread dumps, race detectors (`go race`, `ThreadSanitizer`), reduced parallelism |
| Frontend rendering | Browser devtools, React DevTools, Vue DevTools, layout inspector |
| Build / tooling | Verbose build output (`--verbose`), clean build cache, check dependency versions |

---

## Rubber Duck Debugging

Before asking someone for help, explain the bug out loud (or in writing) to an
inanimate object (a rubber duck, a blank doc, a comment block). Be precise:

- What should happen?
- What actually happens?
- What have you already tried?
- What do you currently believe the cause is?

You will often find the answer mid-explanation. This is not a joke — it works.

---

## When to Ask for Help

Time-boxing your debugging is a professional skill, not a weakness.

**The 30-minute rule:**
- If you've been stuck for 30 minutes and aren't making progress, stop and ask.
- Do not ask empty-handed. Bring:
  - A minimal reproduction
  - What you've tried and ruled out
  - Your current best hypothesis

Asking "it doesn't work" wastes everyone's time. Asking "I've isolated it to this 10-line
function and suspect it's a timing issue because X — can you help me verify?" is efficient.

---

## Fixing the Bug

Once you've confirmed the cause:

- Fix the root cause, not the symptom
- Make the smallest change that fixes the issue
- Do not refactor unrelated code at the same time (this introduces new bugs and makes the diff noisy)
- Update or add a test that would have caught this bug
- Write a short commit message explaining **what the bug was** and **why this fixes it**

---

## After the Fix

Ask: **Could this bug happen anywhere else?**

- Search for the same pattern in the codebase
- If so, fix all instances or add a linter rule to prevent recurrence
- If the bug reached production, add it to project lessons (`lessons.md`) — what assumption was wrong?

---

## Anti-Patterns to Avoid

- **Shotgun debugging**: Changing multiple things at once hoping one works — you won't know which one fixed it
- **Commenting out code**: Temporarily hides the problem, usually forgotten, left in forever
- **Adding sleeps/delays**: Masks timing bugs without fixing them
- **Fixing symptoms**: e.g. catching the exception that shouldn't exist instead of fixing why it's thrown
- **Debugging in production**: Reproduce locally; if you truly can't, add logging and wait for recurrence — don't poke live systems
- **Skipping the test**: Fixing without a regression test means the bug will come back
