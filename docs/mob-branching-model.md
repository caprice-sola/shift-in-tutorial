# Where mobs commit on the day — options and recommendation

**Status: undecided.** Written 2026-09-17 as a decision memo. Nothing in the repo or the slide
deck has been changed to match any of this yet — see [Deferred until this is
decided](#deferred-until-this-is-decided) at the bottom.

The question: several mobs work in parallel all day. They must not commit to `start` or the
`solution/*` branches, those are shared checkpoints. So where does each mob's work live, what
happens when they resync, and what does that do to CI and PRs?

---

## Recommendation in one line

Isolate at the **repo** level — one repo per mob — with a single `mob` working branch inside it,
short-lived feature branches for the two PR exercises, and merging allowed into `mob` only.

---

## Option A — one repo per mob *(recommended)*

Each mob gets `snip-mob-1` … `snip-mob-6`, seeded from this repo with all branches.

**Why this one.** Ex 4 and Ex 6 are "push, then read your own CI result." With every mob in one
repo, the Actions tab interleaves six mobs' runs and "is that green check mine?" costs two minutes
at exactly the wrong moment. Per-mob repos also remove the accidental-push risk to `start` /
`solution/*` and the PR base-branch confusion entirely, instead of mitigating them with rules.

**Provisioning** — facilitator, once, before the day:

```bash
for n in 1 2 3 4 5 6; do
  gh repo create <owner>/snip-mob-$n --public \
     --template <owner>/shift-in-tutorial --include-all-branches
  gh issue create --repo <owner>/snip-mob-$n \
     --title "Link expiry" --body-file docs/issues/link-expiry.md
done
```

`--include-all-branches` is required: a template copy takes only the default branch without it,
and the resync checkpoints are the whole point. (Verified against `gh` 2.98.)

**Public, not private.** Actions minutes are free on public repos; six mobs pushing all day on
private repos bills the owning account. Nothing here is secret — the planted prompt injection is
teaching material, not a vulnerability.

**Access.** One collaborator invite per mob, to whichever attendee's `gh` is authenticated on that
mob's laptop. Invitations must be accepted before the day, as pre-work — alongside `gh auth login`.

**Cost:** six repos and six invites to provision, and this build repo has to be pushed to `origin`
first, since the template copies from there.

## Option B — one shared repo, a branch per mob

Works, and needs no provisioning. What it costs:

- **A noisy Actions tab.** Every mob's runs in one list, at the two moments in the day when
  reading your own CI result *is* the exercise.
- **Branch protection becomes mandatory,** not optional: a ruleset blocking pushes to `start` and
  `solution/*`, or one mob's mistake corrupts a checkpoint for everyone.
- **PR base discipline.** `gh pr create` defaults to the repo's default branch, so every mob must
  pass `--base mob-N` every time. Getting it wrong produces a PR whose diff is the mob's work
  against the *build* repo's `main` — a huge, confusing diff.

Reasonable fallback if provisioning six repos isn't worth it, but it trades one-time facilitator
setup for live-exercise friction across every mob at once.

---

## The branch model inside a mob's repo

| Branch | Role |
|---|---|
| `mob` | the mob's trunk for the whole day, created from `start` |
| `start`, `solution/*` | read-only checkpoints — never committed to, never a PR base |
| `fix/…`, `feat/link-expiry` | short-lived, only for the PR exercises (Ex 2, Ex 7 pt 2) |

### Resync: re-point the trunk, don't check out the checkpoint

```bash
git branch mob-before-resync          # keep a handle on what you had
git checkout -B mob solution/m3a-unit-hook
```

The mob keeps committing to `mob`, CI keeps working, and the checkpoint is never written to. Worth
teaching explicitly: left to themselves, mobs will `git checkout solution/m3a-unit-hook` and
commit straight onto it, which is exactly what quietly corrupts a checkpoint.

### Merge policy

"Never merge a PR" is the wrong rule generalised from the right one. The real rule:

> **Never push to, or merge into, `start` or `solution/*`. Merge freely into your own `mob`.**

- **Ex 2:** open the PR, read it on GitHub, **merge it**, then `git pull`. Otherwise the M2 fixes
  aren't in the trunk Ex 3 builds on, and the mob works around its own open PR all day.
- **Ex 7 pt 2:** merging is optional — it's 16:30 and nothing downstream depends on it. Reading
  the PR and what CI reports is the lesson.
- Keep PR branches short-lived, and don't commit to `mob` while a PR against it is open. That is
  the only way this model produces a conflict.

### CI implications

- **Nothing breaks.** `ci.yml` triggers on `push` and `pull_request`, so a PR branch gets two runs
  per push. Cosmetic — arguably a decent "why two runs?" moment; a `branches-ignore` line fixes it.
- Fresh repos run workflows by default; no first-run approval friction inside your own repo.
- The fast job and the system job stay independent per mob, which is the point of Ex 6.

---

## Prerequisites — two gaps that would bite on the day

1. **The M5a issue body isn't in version control.** It exists only as issue #2 on
   `kisszellet/shift-in-tutorial`, so it cannot be provisioned into six repos. It needs to live in
   a file (`docs/issues/link-expiry.md`), hidden HTML comment and all, for `gh issue create
   --body-file` to work. This is required for Option A and good hygiene regardless.
2. **The issue link is hard-coded.** `solution/m5a-bdd`'s `README.md` and
   `docs/link-expiry-acceptance-criteria.md` both point at
   `github.com/kisszellet/shift-in-tutorial/issues/2`. From a mob repo that's a link back to the
   facilitator's repo, and the number will differ (likely #1 in a fresh repo). They should refer
   to "the link-expiry issue in your repo" and let `gh issue list` find it.

## Deferred until this is decided

- Slide 8 of `docs/slides.html` ("Sanity check, not an install party") — the setup steps and the
  "never commit to a checkpoint" rule belong there, plus a separate fix already spotted.
- `docs/workshop-format.md` — the setup section and pre-work list (invites, per-mob repo).
- `docs/github-cli-notes.md` on the solution branches — it currently assumes a **fork** and warns
  about `gh pr create` defaulting to the upstream repo. Under Option A (template copy, no fork
  relationship) that warning is wrong and should be replaced with the `--base mob` rule.
- `docs/module-guide.md` M2 step 5 and M5b step 6 — "don't merge into the resync branch" should
  become the sharper rule above.
