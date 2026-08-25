# Solution branches

Each sub-module has a branch capturing the repo state **after** that module. A stuck mob checks
out the previous branch to resync. Branches are built in order; each starts from the previous one.

| Branch | Built in task | Contains |
|---|---|---|
| `start` | T0 | The `app/` starter only. No tests, no CI, no AI tooling. |
| `solution/m1-context` | T1 | `app/CLAUDE.md` v1 + `app/docs/test-strategy.md` v1. |
| `solution/m2-review` | T2 | CI stub + GitHub MCP notes + one AI-reviewed PR fixing some planted issues. |
| `solution/m3a-unit-hook` | T3 | `pytest`/`pytest-cov`, unit tests, a `mutmut` run, a `Stop` hook. |
| `solution/m3b-ci` | T4 | `.github/workflows/ci.yml` running units + one SLI gate. |
| `solution/m4-system` | T5 | System-test subagent + Robot suites + slow CI stage + `app/CLAUDE.md` v2. |
| `solution/m5a-bdd` | T6 | Pre-prepared issue (link expiry) + BDD/Example-Mapping skill (`.claude/skills/example-mapping/`). |
| `solution/m5b-feature` | T7 | Link-expiry feature built in-loop, tests generated, PR opened. |

## Build status

- [x] T0 `start`
- [x] T1 `solution/m1-context`
- [x] T2 `solution/m2-review`
- [x] T3 `solution/m3a-unit-hook`
- [x] T4 `solution/m3b-ci`
- [x] T5 `solution/m4-system`
- [ ] T6 `solution/m5a-bdd`
- [ ] T7 `solution/m5b-feature`
- [ ] T8 module guides filled in

---

## Planted issues (FACILITATOR-ONLY — do not fix in `start`)

These give the M2 code-review exercise something real to find, and several map directly to unmet
SLIs so the fixes have business meaning.

1. **No URL validation** (`shortener.create_link`, `models.CreateLinkRequest`). Any string is
   accepted, including `javascript:` and non-URLs. → open-redirect / script-scheme risk; breaks **SLI 4**.
2. **No short-code collision check** (`shortener.generate_code` / `create_link`). A regenerated
   code can silently overwrite an existing link. → breaks **SLI 3** correctness under collision.
3. **Unknown code raises instead of 404.** `store.get` does a bare `dict[...]` lookup, so
   `GET /{code}` and the stats endpoint raise `KeyError` → HTTP 500 instead of a clean 404.
   → breaks **SLI 2** availability.
4. **No tests at all.** The headline gap; the whole day addresses it.
5. **List endpoint has no pagination / leaks insertion order.** Minor maintainability smell;
   good "should we fix this now?" discussion for the pyramid/scope conversation.

Suggested split: M2's AI review typically catches #1 and #3 quickly; leave #2 as a deliberately
subtle one to discuss. #4 is the bridge into M3a.
