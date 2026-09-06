# snip

A tiny URL shortener — the **starter application** for the Shift In tutorial. Past M2: a first
AI-reviewed PR has landed (see `docs/github-cli-notes.md`) and a CI stub exists, but there are
**still no tests** — that's M3a.

## Run it

```bash
pip install -e .
uvicorn snip.main:app --reload --app-dir src
```

- Interactive docs: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/links` | Create a short link from `{ "url": "..." }` |
| GET | `/api/links` | List links |
| GET | `/api/links/{code}/stats` | Click stats for a code |
| GET | `/{code}` | Follow a short link (redirect) |

## Where to look

- `docs/business-context.md`, `docs/quality-characteristics.md`, `docs/slis.md` — what "good" means.
- `src/snip/` — the implementation.
- `tests/` — empty on purpose; you add tests during the workshop.
