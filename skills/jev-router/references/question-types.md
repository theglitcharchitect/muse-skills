# Jev question types (via Vercel AI Gateway `/v1/evaluate`)

## boolean
Returns a probability between 0 and 1. Supply `criteria` to define the true/false cases.

```json
{"approved": {"type": "boolean", "instructions": "Was the request approved?",
  "criteria": {"true": "explicit yes from the user", "false": "anything else"}}}
```
Answer: `{"type": "boolean", "probability": 0.97}`

## choice
Picks one option from a named set. `criteria` maps option names to descriptions.
Answer carries the selected `choice` plus per-option `probabilities`.

```json
{"route": {"type": "choice", "instructions": "Route this support ticket.",
  "criteria": {"billing": "payment or charge problems", "shipping": "delivery problems"}}}
```
Answer: `{"type": "choice", "choice": "billing",
  "probabilities": {"billing": 0.99, "shipping": 0.01}}`

## score
Rates the state along an ordered scale. `criteria` is an array of at least two
labels, ordered lowest to highest. Answer is an interpolated `score` plus the
probability of each rung.

```json
{"quality": {"type": "score", "instructions": "Rate this pull request.",
  "criteria": ["poor: no tests or docs", "good: tests and docs", "excellent: tests, docs, clear rationale"]}}
```
Answer: `{"type": "score", "score": 2.97,
  "probabilities": {"0": 0, "1": 0.02, "2": 0.98}}`

## Notes
- Multiple questions of different types can share one `state` in a single request.
- `state` accepts a string, an object, or an array.
- Do not ask Jev to do arithmetic or date math; use plain code for that.
- Keep state clean: strip tracking headers, HTML boilerplate, unrelated metadata.
