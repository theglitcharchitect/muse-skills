# Sanitization notes

Every skill in this repo was audited for personal identifiers before
inclusion: real names, handles, domains, credential references, private
paths, keys, and tokens. What follows is the complete record of what was
changed, excluded, and why.

## Excluded

### `newsroom-admin`
Excluded outright. Its `SKILL.md` hardcodes a single production domain and
restricts authenticated requests to it; its tooling imports Hatch-runtime
credential helpers (`dynamic_credentials.py`) and a stored credential
(`custom.newsroom-admin`) that only exists on the author's machine. A
generic version would have been a different skill, not a sanitized one.
If you need this pattern (admin API for your own site), the architecture
docs describe the shape; write your own against your own domain and
credential.

### `.superhumanizer-tov/` voice profiles
Not copied. These were the author's personal tone-of-voice profiles,
calibrated on his own writing. The `superhumanizer` skill itself is
generic and is included; bring your own profiles.

## Sanitized

### `tweet-forge`
Rewritten for a generic owner:
- The author's handle and name were removed from the frontmatter
  description and the trigger list.
- "Load the voice" no longer points at the author's private voice profile
  and style guide; it points at new `config/voice.md` and
  `config/account.md` templates the user fills in once.
- The seven-day topic check no longer references the author's posting log
  path; it references the log named in `config/account.md`.
- The research-thread consistency rule was kept but decoupled from the
  author's specific threads.
- The original voice rules (banned patterns, institutional third person)
  survive as documented defaults in the skill, clearly marked as the
  original author's, for the user to replace.

### `skills/jev-router` (from `jev-router-share`)
Copied from the already-sanitized share version, not the private
`jev-router/` directory. Dropped `__pycache__/` and `logs/`. One line of
provenance kept intentionally: the README byline naming the author's
musebook identity, which is public by design.

## Verified clean, copied as-is

`satori` (copied without its `.git` directory), `delta-watch`,
`self-audit`, `stealth-browser`, `crowdcast`, `artifact-craft`,
`artifacts-builder`, `bullshit-detector`, `canvas-design`, `cloudflare`,
`docx`, `frontend-design`, `invoice-organizer`, `kinetic-typography`,
`map-ranking-systems`, `pdf`, `pptx`, `scroll-driven-storytelling`,
`superhumanizer`, `theme-factory`, `xlsx`.

A repo-wide grep for handles, domains, folder IDs, key material, and
credential patterns found no remaining personal identifiers and no
hardcoded secrets. No placeholder keys were invented anywhere in this
repo; where a credential is needed, the docs say how to create one.

## Copyright holder

`LICENSE` names `D4RW1N`, the author's publishing alias, as copyright
holder. Deliberate: this repo ships under the name he publishes under.
