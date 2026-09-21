# Contributing

## What this repo is

A decision layer for agents (TypeSafe Jev, routed through a shadow-mode
usage router) plus a library of 24 skills it can route between. Contributions
should serve that shape: better gates, better question sets, better skills.

## How to contribute

1. Open an issue first for anything beyond a typo fix. Say what the gate or
   skill decides and show one worked example.
2. New gates go in `skills/jev-router/bin/` as a single stdlib-only Python
   script with a `main()`, a module docstring showing usage, and a
   `QUESTION_SET` constant. No third-party dependencies.
3. New question sets ship with versioned references under
   `skills/jev-router/references/`. Document the question types, the
   mapping from answers to verdicts, and the failure modes you considered.
4. New skills follow the standard layout: `SKILL.md` with `name` and
   `description` frontmatter, scripts under `bin/` or `scripts/`.
5. Run the demo (`python3 demo/run.py`) and the smoke test
   (`python3 skills/jev-router/bin/jev.py smoke`) before submitting.

## Ground rules

- Shadow mode first. Any new gate or threshold ships logging-only, with a
  note on how to calibrate it. Nothing merges that enforces on day one.
- No credentials in the repo, ever. No real keys, no placeholder keys that
  look real, no private paths. The sanitization bar is documented in
  `docs/sanitization-notes.md`; hold new contributions to it.
- Jev advises, the human authorizes. A contribution that lets the router
  spend, send, delete, or publish without a human in the loop will not be
  accepted.
- Write like a person. Concrete nouns, short sentences, no hype.
