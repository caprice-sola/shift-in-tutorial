---
name: system-tests
description: How this project writes Robot Framework system tests — the shared server fixture, the conventions, and how to run a suite. Use when writing or changing anything under tests/system/.
---

Our system tests drive a **real, running `snip` server over HTTP** using Robot Framework. This
file is the *how*. **What** deserves a system test is decided by `docs/test-strategy.md` and
`docs/slis.md`, not here — read those first if you are adding a case rather than fixing one.

## Before you write anything

`robotframework` and `robotframework-requests` are declared in the `[system]` extra of
`pyproject.toml`. If `robot` is not on `PATH`, **stop and say so** — the fix is
`pip install -e ".[system]"`, not a guess at a package name.

## Conventions

- **The virtualenv must be active.** The fixture starts the server with `Start Process uvicorn`,
  which resolves `uvicorn` on `PATH`. Run `robot` from an activated venv or the suite fails in
  setup with `FileNotFoundError: 'uvicorn'` — which looks like a broken test and is not one.
- **One server for the whole directory.** `tests/system/__init__.robot` starts a single `uvicorn`
  process for every suite in `tests/system/` and stops it afterwards. Reuse it. Never start a
  server inside a test case, and never add a second `Suite Setup` that binds the same port.
- **Talk HTTP, not Python.** Use `RequestsLibrary` keywords against the `snip` session the
  directory setup created. Do not `import snip.*` — if a test *can* import the application, it
  belongs in `tests/api/` and is not a system test.
- **One suite per user-visible flow**, named after the flow: `redirect_hot_path.robot`.
- **Assert on the response**, not on internals: status code, the `Location` header, JSON fields.
- **Run what you write.** `robot --outputdir robot-results tests/system/`. A suite you have not
  executed is a claim, not a test. Report pass/fail counts; point at `log.html` rather than pasting
  the whole log.

## Syntax

Robot Framework does not look like Python, and two of its rules cause almost every first-time
error: **arguments are separated by two or more spaces**, and a file is divided into `*** … ***`
sections. See [reference.md](reference.md) for those rules and for every keyword our suites
actually use — read it before writing your first suite.

## Copilot equivalent

The same content as a `.github/instructions/system-tests.instructions.md` scoped to
`tests/system/**`, or as a prompt file. Robot Framework is tool-agnostic; only the packaging of
this know-how is Claude-specific.
