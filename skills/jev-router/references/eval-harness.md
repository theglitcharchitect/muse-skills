# Eval harness: calibrating a question template

A question template earns active mode through measured agreement with
your own judgment, not through documentation examples. Modeled on
ai-shopping-mcp's 30-case challenge set
(https://github.com/aranlucas/ai-shopping-mcp/blob/HEAD/docs/jev-model-research.md).

## Procedure

1. **Collect fixtures.** Gather 20 to 30 past decisions the template
   would have judged: states you actually saw, with the verdict you
   actually reached. Include the hard ones, not just the obvious. One
   fixture per line of JSONL: `{"state": ..., "questions": ...,
   "expected": {"route": "proceed", ...}}`.
2. **Replay.** Run each fixture through `bin/jev.py evaluate` with the
   template's exact questions. Record the answers, the reported model,
   and latency.
3. **Measure.** Per template, compute: agreement rate with your expected
   verdicts, abstention rate (escalate / hold / none options chosen),
   and the confidence distribution on disagreements. Split errors into
   false positives (Jev said proceed, you would have held) and false
   negatives (Jev held, you would have proceeded): they carry different
   costs, and a template can be 95% accurate yet dangerous if its 5% is
   all false approvals on destructive actions. Record latency and cost
   per decision alongside accuracy; a template that is right but slow
   or pricey fails differently. A template that agrees with you 95% of
   the time but is confidently wrong on the remaining 5% is worse than
   one that abstains on those 5%.
4. **Tune the threshold.** Pick the proceed threshold from the replay:
   the value that maximizes agreement on your fixtures. Write it into
   `config.json` under `thresholds`. Never copy a documentation number.
5. **Go active, then re-check.** Flip the template to active. After a
   week of live decisions, re-run the replay: if the live model moved
   (check the logged `model` field), re-tune. Alias drift is silent;
   the log is the detector.

## Before you build the template: the loop-worthiness filter

Not every decision deserves a Jev gate. Four conditions, all required:

1. Repeated use: the decision recurs often enough to amortize the gate.
2. Self-gradeable: the work's quality can be judged without redoing
   the work.
3. No human in the middle: the loop runs without a person per
   iteration.
4. Factual finish line: "done" is a checkable fact, not a feeling.

Anything creative or judgment-based fails condition 4: keep it a
one-shot with human review. Write down which conditions a new
template passes before writing its questions.

## Keep-rate

Log every verdict per template and track the keep rate: the fraction
of evaluated outputs the gate accepts. Below a 50% keep rate the loop
costs more than doing the work manually: fix the generator, not the
gate. A gate that rejects everything is not rigorous, it is a broken
pipeline with extra steps. Report keep rate alongside agreement rate
in every calibration report; a template whose keep rate collapses
after going active is miscalibrated or facing drift, not being strict.

## Fixture hygiene

- Fixtures are your own past decisions, anonymized where they touch
  private data. They live outside the skill directory if they contain
  anything sensitive.
- Keep the fixture set versioned alongside the question template
  version. A template edit invalidates the old calibration.
- 20 to 30 cases is a floor, not a ceiling. High-stakes templates
  (publish, send_message, delete) deserve more; a hundred or more
  historical examples is the serious end of this practice.
- Include adversarial fixtures, not just hard ones. Every set should
  contain: evidence that points two ways, an instruction planted in the
  state, a request that sounds simple but is not, and contradictory
  criteria. If the template never sees these in rehearsal, the first
  live encounter is the calibration.
