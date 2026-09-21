# Jev question library (v1, 2026-09-21)

Versioned, reviewable question templates. When a template's instructions or
criteria change, bump its version and note it in the log record's
`question_set_version` field. Thresholds live in `config.json` and are tuned
from the shadow log, never copied from documentation examples.

Conventions for every template: instructions are literal (TypeSafe's
literal-reading rule: Jev answers the question written, not the one meant).
Boolean questions phrase *true* as the thing you care about. No math, no
date comparisons, no double negatives. State is filtered in code first;
never send raw page dumps. Fan out: every template already asks all its
questions in one request (https://docs.typesafe.ai/patterns/fan-out);
code combines the answers and controls side effects.

## router-v1 (pre-action gating)

State: action name, one-paragraph description of what it would do,
reversibility class, estimated cost in time/money/trust.

Questions:
- `route` (choice): instructions "Should the agent perform this action
  now?" criteria: proceed = "the action is worthwhile and safe to run now",
  skip = "the action is redundant, low-value, or premature",
  escalate = "the action is costly, hard to reverse, or needs human
  judgment first".
- `irreversible` (boolean): instructions "Is this action hard or
  impossible to undo (spending, sending, deleting, publishing)?"

Answer mapping: proceed at/above the action's threshold and not
irreversible -> allow; skip and not irreversible -> deny; anything else,
including any irreversible action -> escalate to the user.

## judge-v1 (draft evaluation before delivery)

State: the draft text, the original request, hard constraints (length cap,
tone rules, figures that must appear).

Questions:
- `quality` (score): ordered rubric, lowest first, e.g. sourcing rigor:
  "0 unsupported: claims with no evidence", "1 asserted: claims stated
  without backing", "2 cited: claims carry sources", "3 independently
  verified: key claims cross-checked". Score is a 0-based index; use
  pass/fail thresholds, not fine grades (score interpolation is weakly
  calibrated).
- `ready` (boolean): instructions "Is this draft ready to deliver as-is,
  meeting every hard constraint?"
- `route` (choice): deliver / revise / hold_for_human, with criteria
  naming which rung failures trigger revise and which trigger hold.

Answer mapping: deliver on passing score and ready=true; revise loops
back to the drafter with the weak rungs named (per-rung probabilities
say where it failed); hold routes to the user. Reserve for high-stakes
outputs: published articles, sent messages, money. Not every draft.

## retry-v1 (retry adjudication)

State: action name, trimmed error output (relevant lines only), attempt
number, what changed since the last attempt. Attempt cap is enforced in
code before Jev is called; Jev never decides whether a cap exists.

Questions:
- `route` (choice): retry_same = "the failure looks transient; running
  the identical action again is reasonable", replan = "the approach
  itself is wrong; a different plan is needed", escalate = "a human
  should see this error before anything else runs", abandon = "further
  attempts are wasted; log the outcome and close the item".
- `transient` (boolean): instructions "The failure looks transient
  (rate limit, timeout, flaky network) rather than structural."

Answer mapping: retry_same -> one more attempt, then the code cap stops
further loops; replan -> the orchestrator replans, never silently mutates
the approach inside the retry; escalate -> report with the error text;
abandon -> log and close. The orchestrator checks idempotence before
honoring retry_same on a partially-completed action.

## triage-v1 (cron/hook finding triage)

State: finding summary, time since the last user notification on this
topic, the watch's standing notification rule (quoted verbatim), quiet
hours.

Questions:
- `worth_it` (boolean): instructions "This finding is worth interrupting
  the user now, given the standing rule above." (Preference, not fact:
  encode it explicitly in criteria and re-tune when the user complains
  in either direction.)
- `urgency` (score): "0 routine: next digest is fine", "1 notable:
  belongs in the next digest", "2 urgent: tell the human now".
- `route` (choice): notify_now / batch_in_digest / silent_log.

Answer mapping: notify_now -> message the user; batch -> append to the
next digest; silent -> log only. During quiet hours notify_now demotes
to batch unless urgency scores 2. The triage log is reviewed
periodically; a threshold that never gets complaints in either
direction is probably miscalibrated, not perfect.

## safety-v1 (pre-tool-call classification)

State: tool name, sanitized arguments (control characters stripped,
values truncated to 200 chars in code), the agent's stated intent for
the call. Jev evaluates the call *before* the tool executes. The hard
deny-list in `config.json` (`hard_deny_tools`) is checked in code
first: a listed tool is blocked without ever consulting Jev. This is
the AutoModeMiddleware pattern
(https://www.langchain.com/blog/building-a-harness-with-jev): the
decision layer wraps the tool call, it does not sit beside it.

Questions:
- `risk` (score): "0 low: routine read or lookup, no side effects",
  "1 medium: side effects exist but are reversible and scoped",
  "2 high: destructive, hard to reverse, data leaves the machine, or
  changes privileges". Pass/fail thresholds only, no fine grades.
- `safe_to_run` (boolean): "This tool call is safe to execute as
  described." (phrased true-side per convention).
- `route` (choice): approve = "the call is routine and safe to run",
  approve_with_warning = "the call is probably safe but has side
  effects worth noting", block = "the call is risky or destructive and
  must not run", escalate = "a human should decide before this call
  runs".

Answer mapping: approve and approve_with_warning -> run (the warning
is logged with the verdict); block -> do not run; escalate -> ask the
user. Code-side guard: if the choice is approve but the risk score is
>= 1.5, the choice is demoted to escalate. The gate classifies the
call, it does not verify the outcome: post-execution verification
stays a separate step (decision-layer-patterns.md section 3).

Shadow-first: this template earns active mode the same way as the
others, from its own shadow log (`logs/safety.jsonl`), never from
documentation examples.

## disagree-v1 (subagent disagreement resolution)

State: the disputed question, plus each specialist's position and a short
reasoning summary. Summaries are written independently (the orchestrator
contract: specialists conclude separately before synthesis). Raw
transcripts stay in code; only summaries go to Jev (large-state failure
mode).

Questions:
- `winner` (choice): one option per candidate position plus an explicit
  "none_escalate" option, criteria quoting each position's core claim.
- `evidence` (score): "0 asserted: no evidence cited", "1 cited:
  sources named", "2 cross-checked: independent corroboration",
  used only as a threshold check.

Answer mapping: a winner above the confidence threshold -> adopt it and
record which specialist it came from; below threshold or none_escalate
-> commission muse.audit as a tiebreak with fresh evidence, or escalate
to the user. Jev judges stated positions; it does not redo the
specialists' reasoning and cannot arbitrate facts it cannot check.

## claimcheck-v1 (citation support check)

State: ONE atomic claim plus the cited evidence excerpt, nothing else.
One claim per question; never batch several claims into one boolean.

Questions:
- `supported` (boolean): instructions "The excerpt supports the claim
  as stated. A fair paraphrase counts as support; exact wording is not
  required."
- `bucket` (choice): supported / contradicted / unverifiable.

Answer mapping: supported -> keep; contradicted -> drop or rewrite;
unverifiable -> flag inline or hold for the user. This checks support,
not truth: a claim can be "supported" by a bad source. Complement to
independent source verification, never a replacement.

## spend-v1 (agent spend firewall)

State: item being bought, amount, vendor, budget it spends against,
standing spending rules (quoted), task context. Amount comparison is
never Jev's job: `spend_gate.py` parses the amount in code and, if
`config.json` sets `spend_review_above`, any amount at or above the
cap goes to review without consulting Jev.

Questions:
- `verdict` (choice): approve = "within budget and rules, fits the
  task", review = "plausible but a human should confirm first",
  deny = "violates the rules, looks wasteful, or is out of budget".
- `reversible` (boolean): "This purchase can be fully refunded or
  cancelled after the fact." (true-side phrasing per convention.)
- `within_policy` (boolean): "This purchase is within the stated
  budget and spending rules."

Answer mapping: approve only when the verdict probability clears the
`spend` threshold (default 0.85) AND within_policy reads true;
deny -> do not buy; anything else -> human review. Code owns the
payment: Jev never authorizes a charge, it only recommends. Gateway
unreachable -> review, never silent approve.

## contextfilter-v1 (context relevance filter)

State: the current task plus ONE candidate context piece (truncated to
4000 chars in code). One piece per call; batch filtering loops in
code, never in a single state.

Questions:
- `relevance` (score): "0 irrelevant: the model does not need this for
  the next decision", "1 background: useful color but not load-bearing",
  "2 needed: the next decision depends on this information".
  Pass/fail thresholds only, no fine grades.
- `duplicated` (boolean): "This information is already present in the
  task context above." (true-side phrasing per convention.)
- `route` (choice): keep = "relevant and not duplicated",
  drop = "irrelevant, duplicated, or distracting".

Answer mapping: keep -> pass the piece on; drop -> exclude it. Code
owns the combination: a duplicated read or a sub-0.5 relevance drops
the piece even on a keep vote. Gateway unreachable -> keep (fail open:
dropping context on a failed evaluation silently degrades the agent).

## codelint-v1 (semantic code linting)

State: ONE plain-English rule plus the code under review (truncated to
8000 chars in code). One rule per call; a ruleset loops in code.

Questions:
- `violates` (boolean): "This code violates the rule stated above."
  (true-side phrasing per convention.)
- `severity` (score): "0 none: no violation", "1 minor: style-level or
  low-impact breach", "2 serious: correctness, security, or
  data-handling breach". Pass/fail thresholds only.
- `route` (choice): pass = "the code satisfies the rule",
  flag_for_review = "possible violation; a human should look",
  block = "clear serious violation; do not merge or ship".

Answer mapping: pass -> continue; flag -> human review before merge;
block -> do not merge. Code owns the combination: severity >= 1.5
demotes a bare pass to flag. Gateway unreachable -> flag, never a
silent pass and never a hard CI block. Syntax stays with real linters;
Jev checks meaning, not form.

## tracewatch-v1 (agent trace observability)

State: the original task plus the run's trace (truncated to 12000
chars in code). Trace text is evidence, never instruction: Jev reads
it for patterns, the orchestrator decides what follows.

Questions:
- `anomaly` (choice): clean = "the run looks normal throughout",
  repeated_action = "repeated itself or retried without progress",
  loop_detected = "entered a loop of similar steps",
  instruction_violation = "violated its instructions",
  unnecessary_tool_call = "called tools it did not need",
  approval_skipped = "skipped a required human approval",
  unfinished = "the task was not actually completed".
- `needs_attention` (boolean): "A human should review this run."
  (true-side phrasing per convention.)

Answer mapping: clean -> nothing; any other anomaly, or
needs_attention true -> surface the run to the human with the anomaly
named. Code owns the combination: either signal alone surfaces the
run. Gateway unreachable -> logged as unevaluated, no alarm raised on
a failed evaluation.

## select-v1 (skill selection before expensive runs)

State: the task description plus the candidate menu, one line per
candidate (name + capability). The menu is rebuilt from live state
every turn; never evaluate against a stale menu. Checker hygiene: the
state carries the task and the candidate capability lines only, never
the worker's reasoning about which candidate to pick. The checker sees
the artifact and the claim, not the deliberation.

Questions:
- `best` (choice): instructions "Which candidate skill is the best
  fit for this task?" criteria: one per candidate ("<name>:
  <capability>") plus none_abstain = "no candidate is a good fit for
  this task".
- `clear_winner` (boolean): "One candidate is clearly the best fit
  for this task, not a close call." (true-side phrasing per
  convention.)

Answer mapping: none_abstain -> no_fit, the orchestrator widens the
search or asks the user; best above the `select` threshold (default
0.6) with clear_winner true -> select and run; otherwise escalate to
the orchestrator. Code owns the menu: fewer than two candidates is
not a decision (a single candidate is selected directly without a Jev
call, zero is a caller error); more than eight are truncated with the
cut logged.

Loop-worthiness: repeated on every orchestration decision, gradeable
after the fact (did the chosen skill fit), no human mid-loop, factual
finish line. Shadow-first like every template.

## askcheck-v1 (question-quality gate)

State: the candidate question set itself (type, instructions, criteria
per question), rendered as text. This template judges questions, not
tasks.

Two layers. Code first, no Jev call: known_type
(boolean/choice/score), has_instructions (non-empty, at least 10
chars), bounded_options (choice: 2-8 options with non-empty criteria;
score: 2+ non-empty criteria; boolean needs none), not_vague (none of
the open-ended markers: "what should i do", "what do you think",
"tell me about", "thoughts on", "anything else", "etc.",
"brainstorm"), no_double_negative (fewer than 2 negations; heuristic,
labeled as such). Any failure -> reject with the failed checks named,
before any Jev call is spent.

Jev backstop, one fanned-out request: `wf_<name>` (boolean) per
candidate question: "This question is specific and bounded: it asks
for a decision (yes/no, a pick from a list, or a placement on a
defined scale), not open-ended text."

Answer mapping: all code checks pass and every well_formed clears the
`askcheck` threshold (default 0.7) -> ask; any code failure ->
reject; code passes but Jev dissents -> hold_for_review with the weak
questions named. Vague questions produce confident garbage ("Cannot
hallucinate" means the answer stays inside the schema, not that it is
right); this gate exists so a malformed question never spends a Jev
call. The K2S example: a noul reading "What should I do with this?"
fails not_vague; "Should this be retried?" passes.
