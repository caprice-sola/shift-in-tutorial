# snip — Service Level Indicators (SLIs)

These SLIs define "good" for snip. They drive **what we test** and **what CI gates on**.
Targets are deliberately modest so a workshop pipeline can check them.

| # | SLI | Definition | Target (SLO) |
|---|-----|------------|--------------|
| 1 | **Redirect latency** | p95 server time to answer `GET /{code}` | < 50 ms |
| 2 | **Redirect availability** | share of `GET /{code}` returning a valid redirect or a correct 404 | ≥ 99.9% |
| 3 | **Resolve correctness** | share of follows that redirect to the exact stored URL | 100% |
| 4 | **Create validation** | share of create requests with invalid/unsafe URLs that are correctly rejected | 100% |
| 5 | **Stats accuracy** | recorded clicks equal actual follows | 100% |

## How these map into the workshop

- **M1** references these in the test strategy.
- **M3b** turns at least one SLI into a **CI gate** (latency or correctness are the easy first choices).
- **M4** weights system test coverage toward the redirect hot path (SLIs 1–3).
- **M5** treats SLI impact as part of the feature's acceptance criteria.

> **Facilitator note:** in `start`, SLI 4 (unsafe URLs accepted), SLI 2 (unknown codes 500 instead
> of 404), and SLI 3 (short-code collisions overwrite silently) are all unmet on purpose — the
> planted issues M2/M3a exist to close. Full list with rationale: `solutions/README.md`.
>
> This file is `app/`'s copy, extracted into the attendee-facing `start` branch — but `start`'s
> copy of this note has been deliberately reworded to not name specifics, since attendees read it
> during M1, before M2 discovers any of this. The two copies have diverged on purpose. **Don't
> re-run the `app/` → `start` extraction and overwrite `start`'s version with this one** — if `app/`
> ever needs re-extracting, carry this note's de-spoilered wording over by hand.
