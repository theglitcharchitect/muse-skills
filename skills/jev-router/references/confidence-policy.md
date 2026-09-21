# Confidence policy

From TypeSafe's confidence documentation
(https://docs.typesafe.ai/confidence), opened 2026-09-21, plus local
calibration rules.

## How confidence works

Confidence is derived from the shape of the probability distribution:
concentrated means confident, spread means uncertain. Choice and score
answers carry a `confidence` field; the boolean type does not (its
probability is the whole signal).

## The three paths

- **Act** (high confidence): proceed automatically.
- **Proceed with caution** (medium): confirm, flag, or gather more
  evidence first.
- **Route to human** (low): escalate. A 0.5 confidence floor catches
  genuine uncertainty.

## Thresholds scale with risk

What sets the band is reversibility plus cost plus consequence, not the
action's name. Fully reversible and cheap: automate on high
confidence. Reversible but costly, or cheap but hard to undo: automate
only in a middle band, with logging or confirmation. Irreversible, or
touching money, other people, or private data: human review below very
high confidence. Published bands from other deployments (for example
>0.95 automate, 0.70-0.95 reversible-only, <0.70 human) are examples of
the shape, never numbers to copy.

Defaults in `config.json` (tune from the shadow log, never from documentation):

| Action type   | Proceed threshold |
|---------------|-------------------|
| browser_run   | 0.60              |
| research      | 0.60              |
| retry         | 0.60              |
| publish       | 0.80              |
| send_message  | 0.85              |
| delete        | 0.90              |

Falling back: any action without a named threshold uses
`proceed_threshold` (0.60).

## Calibration rules

- Thresholds come from the shadow log of your own labeled decisions,
  never from documentation examples or another deployment's numbers.
- Calibration holds across groups of predictions, not single answers.
  A 0.9 confidence means roughly nine in ten such answers are right;
  it is not a guarantee about this one. Judge a threshold by its
  error rate over dozens of decisions, never by one vivid case.
- Shadow before active for every new question template, not just the
  router as a whole. A template earns active mode when its shadow
  decisions match your judgment consistently.
- Log the model version that answered and the question-set version with
  every decision, so a regression can be traced to an alias move or a
  template edit.
- Re-tune when the user complains in either direction (too many
  interruptions or too much silence). A threshold nobody ever
  complains about is probably miscalibrated, not perfect.
- Jev advises. Sentinel and the human authorize. A Jev verdict is never
  the permission for a sensitive action.
