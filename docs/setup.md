# Setup

## Requirements

- Python 3.10 or newer. No third-party packages; the gate scripts use the
  standard library only.
- Git, for cloning.

## 60-second start

```bash
git clone <this-repo>
cd muse-skills
python3 demo/run.py
```

The demo runs against a deterministic mock gateway: no key, no network,
identical verdicts every run. It exercises the real gate scripts from
`skills/jev-router/bin/`.

## Going live with Jev

1. Get a Vercel AI Gateway key at https://vercel.com/ai-gateway
   (Jev is currently served free; the gateway still requires a payment
   method on the Vercel team or calls fail with
   `customer_verification_required`).
2. Export it:
   ```bash
   export VERCEL_AI_GATEWAY_KEY=...
   ```
   (`JEV_GATEWAY_KEY` works too.)
3. Smoke test:
   ```bash
   python3 skills/jev-router/bin/jev.py smoke
   ```
4. Re-run the demo: `python3 demo/run.py`. It detects the key and talks to
   the real gateway; the mock is bypassed. Nothing else changes.

Never commit the key. `.gitignore` covers the usual env files.

## Configuring the router

`skills/jev-router/config.json` controls the decision layer:

- `mode`: `"shadow"` (log only, default) or `"active"` (enforce verdicts).
- `enabled`: `false` is the kill switch. Everything proceeds, nothing is gated.
- `proceed_threshold`: minimum choice probability to allow an action
  (default 0.6); per-action overrides under `thresholds`.
- `auto_escalate`: actions that skip Jev and escalate directly.
- `hard_deny_tools`: tool names blocked in code before any Jev call.
- `max_retries`, `quiet_hours`: used by the retry and triage scripts.

The shipped thresholds are starting examples. Calibrate them from your own
shadow log (`skills/jev-router/references/eval-harness.md`), never from
documentation. Read `docs/shadow-mode.md` before flipping to active.

## Using a skill

Skills follow the standard agent skill layout: `SKILL.md` at the root with
frontmatter (`name`, `description`) that tells an agent when to load it.
Point your agent at `skills/` or copy individual skill directories into
your own skill path. Some skills ship helper scripts under `bin/` or
`scripts/`; their `SKILL.md` documents the invocation.

## Layout

```
muse-skills/
  skills/          24 skills, jev-router first among equals
  demo/            four-act terminal demo + fixtures
  docs/            architecture, setup, shadow-mode, catalog, sanitization notes
  examples/        a shadow-log excerpt to show what calibration reads like
```
