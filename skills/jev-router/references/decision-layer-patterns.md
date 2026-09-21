# Decision-layer patterns

Distilled from @0xMovez's "Jev Engineering: how to build the fastest AI
Agent Brain in 10 Steps" (X article, Sep 18, 2026). Quantitative claims
below are the article's, reported here as reported, not independently
verified. Local calibration rules in confidence-policy.md still govern
every threshold.

## 1. The three-way split

Every agent job decomposes into three kinds of work, each with its own
executor:

- **Creates text** (research summaries, drafts, explanations) -> stays
  with the generative LLM.
- **Picks from a list, scores a value, or answers yes/no** -> goes to
  Jev. These decisions never needed generation; they were always
  paying generation prices.
- **Is an exact rule** (stop after ten actions, cap retries at three) ->
  belongs in code, not in any model. Our retry adjudicator already does
  this: the attempt cap is enforced before Jev is ever called.

When a new decision surfaces, classify it into one of the three before
deciding how to evaluate it.

## 2. Dynamic menus

Choice options must be rebuilt from live state on every turn. A
browser's available actions change after every click; a worker pool
changes as workers finish. Evaluating against yesterday's option list
produces confidently wrong answers.

For our CLIs: when the state passed to `router.py` or `judge.py`
describes a world that changed since the last call, regenerate the
question criteria from the fresh state first. Never cache a question
definition across state changes.

## 3. Pre-tool-call safety classification

Now wired into this skill as `bin/safety_gate.py` with the `safety-v1`
question template. Jev acts as a gate that runs *before* a tool
executes, approving safe calls and blocking or escalating risky ones.
This is the AutoModeMiddleware pattern
(https://www.langchain.com/blog/building-a-harness-with-jev): the
decision layer wraps the tool call rather than sitting beside it.

Two code-first layers run before Jev is consulted: a hard deny-list
(`hard_deny_tools` in config.json) blocks listed tools deterministically,
and argument values are sanitized (control characters stripped, values
truncated) before they enter the state. The gate classifies the call;
it does not verify the outcome. A confident decision cannot prove a
file was saved or a message was sent, so post-execution verification
stays a separate step. Both layers have a place; they answer different
questions.

## 4. Cost per completed task, not per decision

A cheap decision that sends a worker down the wrong branch costs more
than the decision itself. Track the bill per completed task. The
router log carries token usage and cost per decision; roll it up per
task when reviewing. If a low-confidence ALLOW correlates with
expensive rework downstream, the threshold for that action type is too
loose regardless of what the per-decision numbers say.

## 5. Evidence quality in state

"The researcher finished" tells Jev less than the sources, the
findings, and the remaining gaps. Keep those fields separate from the
original request in the state object. Summaries compress away exactly
the distinctions a decision model needs. This is the same discipline
as the state-filtering rule: strip boilerplate, keep evidence.

## 6. Reported benchmarks (unverified)

- Browser Use: Jev selecting actions and page elements; flight-search
  demo reported at ~7 seconds and $0.0039 (article's numbers).
- Paper classification: 1,018 AI papers at $0.08 total, 256ms median
  end-to-end latency per paper (reported by a third party in the
  article's replies).
- Inbox triage: 500 emails classified for 3.5 cents (demo by Riley
  Brown, reported in article).
- Context compaction: one reported test compacted a ~1M-token Claude
  session to 86K in about a second, as a relevance filter rather than
  a summarization pass.

Treat all of these as existence proofs of the pattern, not as
performance guarantees for our deployment. Our numbers come from our
own logs.

## 7. Harness over model

The article's closing argument: on the same model, loop engineering
decides performance more than weights do. The router, the question
templates, the thresholds, and the verification steps are the
product. The model alias underneath can drift (it has: versioned IDs
already 404 on the gateway) and the harness should keep working.
