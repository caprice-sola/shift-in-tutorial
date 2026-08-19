# Shift In Tutorial — build project

Source-of-truth repository for the full-day, hands-on conference tutorial
**"Shift In: Making Your AI Coding Agent a Quality Engineer."**

This is the project you open in **Claude Code** to build the workshop. The agent reads
`CLAUDE.md` for its mission, conventions, and an ordered build backlog.

## Layout

```
shift-in-tutorial/
├── CLAUDE.md            # Agent mission, conventions, working agreements, build backlog
├── README.md           # You are here
├── docs/               # Workshop design (read these first)
│   ├── shift-in-thesis.md
│   ├── facilitator-map.md
│   ├── workshop-format.md
│   ├── abstract.md
│   ├── abstract-short.md
│   └── module-guide.md          # to be authored (backlog T9)
├── app/                # The starter application teams clone (becomes branch `start`)
│   ├── CLAUDE.md       # The app's own instructions file (authored in M1)
│   ├── docs/           # business-context / quality-characteristics / slis
│   ├── src/snip/       # FastAPI URL-shortener
│   └── tests/          # deliberately empty in `start`
└── solutions/
    └── README.md       # Branch strategy + per-branch build spec + planted-issue list
```

## Getting started

1. Download and unzip this project.
2. `git init && git add -A && git commit -m "scaffold"`
3. Open in Claude Code and say: *"Read CLAUDE.md and start on T0."*
4. Build the branches in backlog order; each becomes a workshop resync point.

## The two repos

- **This repo** = where you (facilitator) build everything, with Claude Code's help.
- **The starter repo** = `app/` extracted to branch `start`, what attendees clone on the day.
  Solution branches `solution/m1-context` … `solution/m5b-feature` carry the per-module answers.
