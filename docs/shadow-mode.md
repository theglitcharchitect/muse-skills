# Shadow mode

The single most important idea in this repo.

## The rule

A new gate starts in **shadow mode**: it evaluates every decision and logs
the verdict, but it never enforces anything. The action proceeds exactly as
it would have without the gate. You watch the log. When the logged judgment
matches your own judgment consistently, you flip `config.json` to
`"mode": "active"`. Not before.

## Why

A decision gate you cannot calibrate is a random number generator with
confidence. Thresholds in documentation are someone else's thresholds: their
risk tolerance, their cost structure, their mistakes. Your shadow log is the
only honest record of how Jev judges *your* workload. The eval harness
(`skills/jev-router/references/eval-harness.md`) shows how to score the log
against your own calls and set thresholds from the disagreement rate.

Concretely, shadow mode buys three things:

1. **Evidence before authority.** Every verdict arrives with probabilities
   and the margin between options. A week of logs tells you where Jev is
   sharp and where it hedges. You promote it to active only on the sharp
   parts.
2. **A kill switch with a paper trail.** `"enabled": false` disables all
   gating, and the log shows exactly what ran unjudged while it was off.
3. **Safe upgrades.** New question sets, new thresholds, new actions go
   through shadow first. The log is the diff.

## Jev advises, the human authorizes

Shadow mode is the mechanism; the principle is older. The router never
spends, sends, deletes, or publishes on Jev's say-so alone. Those actions
escalate to a person in both modes. Jev's job is to make the human's
decision faster and better informed: a risk score, a probability, a named
weak rung in a draft. The final call stays with the person who bears the
consequence.

## The demo

`python3 demo/run.py` runs entirely in shadow mode. Act 4 is the clearest
illustration: Jev says escalate on a browser run, the run proceeds anyway,
and the decision lands in `logs/router.jsonl`. That log entry is the unit
of calibration. Collect a few hundred, score them against what you would
have decided, set your thresholds, then go active.
