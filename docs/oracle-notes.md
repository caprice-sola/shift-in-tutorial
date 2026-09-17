# Oracle notes — breaking the code on purpose (M3a)

`docs/test-strategy.md` names `shortener.py` as the module whose oracles we check by hand: it
carries the highest-risk logic (validation, collision handling, lookup). The check needs no tooling
and takes about three minutes:

```bash
# 1. break one line in src/snip/shortener.py - in create_link's collision-retry loop:
#        code = generate_code()   ->   code = None
pytest tests/unit -q   # 2. does the suite go red?
# 3. green means a missing assertion: strengthen it, re-run, then revert the break
```

A suite that stays green against obviously broken code *is* the finding. That is the oracle
problem, and it is why we do this by hand before trusting any coverage number.

## Automating it later: `mutmut`

`mutmut` does the same thing exhaustively — every mutable line in a module, not one line at a
time. Worth adding once a suite is stable; deliberately not part of the workshop day, since it
needs its own dependency, its own config, and a slow run. If you try it at home: add `mutants/`
and `.mutmut-cache` to `.gitignore`, and add a `[tool.mutmut]` section. Two settings matter and are
easy to get wrong: `source_paths` controls what gets **copied** into mutmut's sandbox (`mutants/`),
not just what gets mutated — set it to `["src"]` so the whole package (and its imports) stays
resolvable. Use `only_mutate = ["src/snip/shortener.py"]` to scope *mutation generation* down to
the one file. Pointing `source_paths` at a single file (the more obvious-looking config) copies
only that file into the sandbox and breaks every test that imports anything else from `snip`.

## What the automated sweep found during the build

The reference build did run `mutmut` once over `shortener.py` while these notes were written -
the same check as above, applied exhaustively. The one survivor it found is exactly the line the
workshop now breaks by hand.

The result: **18 of 19 mutants killed, 1 survived.** The survivor, in
`create_link`'s collision-retry loop:

```diff
 def create_link(url: str) -> LinkRecord:
     code = generate_code()
     while store.exists(code):
-        code = generate_code()
+        code = None
     record = LinkRecord(code=code, url=url)
     store.put(record)
     return record
```

`test_create_link_retries_on_code_collision` forces exactly one collision (via `monkeypatch`) and
exercises this exact line — so the mutant *was* covered. The test still passed against it, because
the assertions only checked that the second link's code differed from the first and that both
still resolved. Under the mutant, `second.code` becomes `None`; `None != "dupe12"` is still true,
and `store.get(None)` still succeeds (the record is happily stored under key `None`). Both
assertions held on a code value that's actually broken — a `None` short code isn't a valid path
segment and would never come out of `generate_code()` for real.

This is the oracle problem, concretely: 100% line coverage on this file, and a test that exercises
the exact right branch, but an assertion too weak to notice the value it got back was garbage.

**Fix:** pin down what the retried value should actually be, not just that it differs:

```python
assert second.code == "uniq99"  # retried via generate_code(), not left blank
```

Re-ran mutmut: **19/19 killed.**

## Takeaway for the mob

A green coverage report answers "did this line run?" — not "would we notice if it broke?" A suite
that stays green against code you broke on purpose — or a surviving mutant, once you automate it —
is a missing assertion until you've concretely shown otherwise (an equivalent mutation that can't
change observable behavior is possible in principle, but wasn't the case here).

## M5b: the same lesson showed up twice more in one feature

Building link expiry added real logic to `resolve()` — a comparison and an exception. First run:
**24 of 26 mutants killed, 2 survived.**

**Survivor 1 — boundary operator:** `record.expires_at <= datetime.now(...)` mutated to `<`. Every
test used a clearly-past timestamp (`now - 1 second`), so `<=` vs `<` made no difference to any of
them — the exact instant of expiry was never exercised. Fixed by freezing "now" (`monkeypatch` on
`shortener.datetime`) and constructing a record whose `expires_at` exactly equals it, then
asserting that still raises. Without this, a future refactor could silently make links valid
"through" their expiry instant instead of "up to and not including" it, and nothing would catch it.

**Survivor 2 — exception payload:** `raise LinkExpiredError(code)` mutated to
`raise LinkExpiredError(None)`. The test only checked *that* a `LinkExpiredError` was raised
(`pytest.raises(LinkExpiredError)`), never *which* code it carried — the same class of gap as the
`None`-short-code mutant above, just on an exception's payload instead of a return value. Fixed by
asserting `str(exc_info.value) == record.code`.

Second run: **26/26 killed.**

Same root cause both times: `pytest.raises(SomeError)` alone proves an error type, not that the
error is *correct*. If the exception (or the mutated code path) can carry meaningfully different
content, assert on the content too.

By hand, both gaps surface from two single-line breaks: change `<=` to `<`, and change
`LinkExpiredError(code)` to `LinkExpiredError(None)`. That is exactly the M5b step — break one
line of the logic you just wrote, re-run, and see whether anything notices.
