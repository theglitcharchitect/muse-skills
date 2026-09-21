# Router policy

## Modes

- `enabled: false` — kill switch. The router returns ALLOW immediately without
  calling Jev. Use when the router misbehaves or costs need to stop now.
- `mode: shadow` — Jev is called and every decision is logged, but the caller
  always proceeds. This is the calibration phase: build a log, compare Jev's
  judgment against your own, adjust `proceed_threshold` before going active.
- `mode: active` — Jev's decision is honored. ALLOW proceeds, DENY stops the
  action, ESCALATE means ask the user before doing anything.

## Decision logic

For each proposed action the router asks Jev two questions against the same state:

1. `route` (choice: proceed / skip / escalate) — should the action run now?
2. `irreversible` (boolean) — is it hard or impossible to undo?

- ALLOW: choice is `proceed` with probability >= `proceed_threshold` (default 0.6)
  and the action is not rated irreversible.
- DENY: choice is `skip` and the action is not irreversible.
- ESCALATE: everything else, including any action rated irreversible regardless
  of the route choice.

## What to route

Route actions that cost time, money, or trust: browser runs, deep-research
passes, retries of failed work, spawning extra subagents, sending messages,
publishing, deleting. Do not route cheap local reads or pure computation.

## Reviewing the log

`logs/router.jsonl` holds one JSON record per decision: timestamp, action,
mode, Jev's choice and probability, irreversibility rating, final decision,
token usage, and cost. Read it before flipping to active.
