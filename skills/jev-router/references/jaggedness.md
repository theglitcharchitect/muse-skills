# Jev jaggedness: nine failure modes as operating rules

Distilled from TypeSafe's jaggedness doc for jev-1.13
(https://docs.typesafe.ai/model-jaggedness/jev-1.13), opened 2026-09-21.
These are the ways Jev fails while looking confident. Every question
template in `question-library.md` is written against this list.

1. **Literal reading.** Jev answers the question written, not the one
   meant. State the exact condition in `instructions`; put boundary cases
   in criteria. If you catch yourself explaining what you really meant,
   that explanation is the missing half of the instruction.
2. **No math.** Jev is not a calculator and does not count reliably.
   Keep all arithmetic in code. Score levels are weakly numerically
   calibrated: a score may check a threshold but never reconstruct an
   exact magnitude by interpolation.
3. **No date comparisons.** Dates read as text, not ordered quantities.
   Ordering, duration, and window checks are unreliable. Extract date
   parts as a Choice over enumerated options (with an explicit "not
   stated"), then compare in code.
4. **No indirection.** Double negatives and property-of-property questions
   cost accuracy. Write direct instructions; name the relevant parts of
   state. Phrase booleans so *true* is the thing you care about.
5. **Filter state in code.** Accuracy falls as unrelated content grows.
   Send only what the question needs. A boolean pre-filter for relevance
   is cheaper than one giant state. Never send raw page dumps.
6. **State is untrusted.** Jev does not treat state as hostile.
   Injected instructions, misleading framing, or text arguing for its own
   classification can move the answer. Be explicit in criteria; test edge
   cases before deploying; never feed untrusted fetched text to Jev
   without filtering; never let a Jev verdict alone authorize a sensitive
   action.
7. **Align instructions and criteria.** A boolean where true means "no"
   performs worse. Contradictory instructions and criteria degrade the
   answer; keep them saying the same thing.
8. **No cross-type arithmetic.** Do not expect P(noul) and 1 - P(not
   noul) to sum to 1. Do not carry a threshold tuned on a boolean over
   to a choice. Do not treat choice (relative: which option) and boolean
   (absolute: how true) as interchangeable.
9. **No generation.** Jev is not trained for it. Forcing generation via
   chained choices is slow and bad. Turn extraction into a choice over
   bounded options found by code or a generative model.
