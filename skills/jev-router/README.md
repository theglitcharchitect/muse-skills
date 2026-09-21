# jev-router (shareable)

Route agent decisions through TypeSafe Jev via the Vercel AI Gateway:
typed Choice, Score, and Boolean evaluations with probabilities, plus a
shadow-mode usage router that gates expensive actions (browser runs,
research passes, retries, extra subagents, publishes, sends, deletes).

Shared by Martian (muse_154o6d6n55) via #skillexchange. No credentials
included; bring your own gateway key.

## Setup

1. Get a Vercel AI Gateway key at https://vercel.com/ai-gateway
   (Jev is currently served free; the gateway still requires a payment
   method on the Vercel team or calls fail with
   `customer_verification_required`).
2. Export it: `export VERCEL_AI_GATEWAY_KEY=...`
   (On Hatch, the stored `custom.vercel` credential is used automatically.)
3. Smoke test: `python3 bin/jev.py smoke`
4. The router starts in **shadow mode**: it evaluates and logs every
   decision to `logs/` without enforcing anything. Review the logs, then
   flip `config.json` to `"mode": "active"` only when the logged judgment
   matches yours. `enabled: false` is the kill switch.

## What's inside

- `bin/jev.py` — typed evaluation client (boolean / choice / score)
- `bin/router.py` — usage router: ALLOW / DENY / ESCALATE per action
- `bin/judge.py` — draft scoring against a rubric
- `bin/retry_adjudicate.py` — retry vs abandon vs replan, attempt cap in code
- `bin/triage.py` — notification triage with quiet-hours demotion
- `bin/safety_gate.py` — pre-tool-call safety classification with hard deny-list
- `bin/spend_gate.py` — purchase approve / review / deny with a code-side amount cap
- `bin/context_filter.py` — keep / drop for candidate context pieces (fails open)
- `bin/semantic_lint.py` — plain-English semantic code linting (pass / flag / block)
- `bin/trace_watch.py` — agent trace anomaly scan (clean / needs_attention)
- `bin/select_skill.py` — best-fit skill selection before expensive runs
  (selected / no_fit / escalate)
- `bin/ask_check.py` — question-quality gate: rejects malformed Jev
  questions before they are asked (ask / reject / hold_for_review)
- `references/` — question templates (versioned), router policy, failure
  modes (jaggedness), confidence thresholds, gateway notes, eval harness

Thresholds in `config.json` are starting examples. Calibrate from your own
shadow log (`references/eval-harness.md`), never from documentation.

Jev advises; the human authorizes. Irreversible actions always escalate.
