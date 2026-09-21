# Vercel AI Gateway notes: Jev evaluation

Operational record. Last verified 2026-09-21 (model page, TypeSafe docs,
live smoke test: cost "0", boolean 0.01 correct).
Gateway docs: https://vercel.com/docs/ai-gateway/modalities/evaluation.
Further reading: speculative fan-out
https://docs.typesafe.ai/patterns/fan-out, confidence
https://docs.typesafe.ai/confidence, jaggedness
https://docs.typesafe.ai/model-jaggedness/jev-1.13, models
https://docs.typesafe.ai/models.
Everything under "live-tested" was verified on 2026-09-21.

## Endpoint

`POST https://ai-gateway.vercel.sh/v1/evaluate`
Body: `{"model": "typesafe-ai/jev", "state": <string|object|array>, "questions": {...}}`.
Question types on the gateway: `boolean` (TypeSafe's native "noul",
identical semantics), `choice`, `score`. Multiple types share one state
in a single request, answered in one round trip. Not available through
the OpenAI/Anthropic/Cohere-compatible endpoints.

Response: `model`, `answers`, token `usage`, and
`providerMetadata.gateway` with `cost`, `marketCost`, `surchargeCost`,
`gatewayCost`, routing info (`originalModelId`, `resolvedProvider`,
`canonicalSlug`, `finalProvider`), and a `generationId`.

## Provider options

`providerOptions.gateway` accepts `zeroDataRetention: true` (per-request
zero data retention) and `only: ["typesafe-ai"]` (provider restriction).
Evaluation works with BYOK: a team provider key is used automatically.

## Auth gotchas (live-tested)

- The gateway returns HTTP 403 `customer_verification_required` until a
  valid credit card is on file, even for free models.
- The card must sit on the same Vercel team that owns the API key. A
  card on the wrong team still yields 403. Check the dashboard team
  selector and the AI Gateway billing page when this error persists.
- A 401 or 403 is a question about the request before it is a question
  about the key: verify the surrogate credential was actually attached
  (a request built without the helper carries nothing and looks exactly
  like a wrong key) before reconnecting.

## Pricing (live-tested, treat as changeable)

On 2026-09-21 the gateway listed `typesafe-ai/jev` (32K context) as Free
input / Free output, and live evaluations returned cost `"0"`. Vercel's
own docs example shows a non-zero cost field, and community writeups
describe $0.042/M input on the gateway. Treat the free tier as
observed-but-changeable. Recheck the models page before assuming free
forever. Direct API pricing (for reference): $0.042/M input tokens,
free output.

## Context and versions

- Gateway context: 32K. Direct API: 64K per request (32K budget for
  state plus the single longest question). Text only.
- Versioned model IDs do NOT work on the gateway (live-tested:
  `typesafe-ai/jev-1.13.0` returns 404 `model_not_found`). The response's
  `model` field reports the alias that answered. Alias drift is therefore
  a real risk here: log the reported model with every decision so a
  silent model move is detectable in the log.
- Direct API alternative: `POST https://api.typesafe.ai/v1/systemone`
  with a Bearer key, versioned IDs like `jev-1.13.0`, and the alias
  `jev-latest`. TypeSafe recommends pinning the versioned ID once
  thresholds are tuned.

## Dead ends (live-tested)

- `typesafe/jev` does not exist on Cloudflare Workers AI (65-model
  catalog checked, no Jev). A community FAQ claiming otherwise is wrong.
- A working community path is Cloudflare AI Gateway -> OpenRouter
  Decisions with `typesafe/jev-1.13`.
