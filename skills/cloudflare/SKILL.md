---
name: "cloudflare"
description: "Use Cloudflare when the user asks for Cloudflare or this provider's API."
---

# Cloudflare

## Purpose
Use Cloudflare with the user-connected `custom.cloudflare` credential.

## Tooling
Deploys go through wrangler, driven by `bin/cf-pages-deploy`:

    bin/cf-pages-deploy --project <name> --dir <site-dir> [--branch main]

The wrapper exchanges the stored credential for an authd surrogate, exports it
as `CLOUDFLARE_API_TOKEN` (the surrogate, never the real token) plus
`CLOUDFLARE_ACCOUNT_ID` (from `~/workspace/newsroom/deploy/.cf-account-id`),
and runs `npx wrangler pages deploy`. The egress layer swaps the surrogate for
the real credential on the approved `api.cloudflare.com` calls. A hand-rolled
direct-upload REST client was tried and abandoned: the asset-upload JWT flow
rejected every auth variant, while wrangler's implementation works first try.

Python CLIs under `bin/` that call the API directly must import
`/opt/hatch/skills/skill-creator/bin/dynamic_credentials.py` and call
`add_surrogate_to_request(...)` before authenticated requests, matching where
the provider reads the key. If they use `urllib`, read JSON responses with
`read_json_response(resp)` from the same helper instead of calling
`resp.read()` directly. They must send only `hsurr:*` values, and only to the
hosts below.

## Auth
The credential is already stored; nothing here collects one. Never ask the user to paste a raw key in chat, set a secret environment variable, pass a secret flag, or write an auth file.

A 401 or 403 is a question about the request before it is a question about the key. Check that the credential was attached at all: a request built without the helpers named under Tooling carries nothing, and that looks exactly like a wrong or under-scoped token. Only once a request that did carry the credential is still rejected, call `credentials.request_api_access` with `reconnect` to replace it. The connector is stored as `custom.cloudflare`.

## Operating Rules
1. Use this skill when the user asks for Cloudflare or this provider's API.
2. Restrict authenticated requests to: api.cloudflare.com.
3. Do not print, log, or persist raw credentials.
4. If auth is missing or rejected, follow the Auth section rather than asking for a key.
