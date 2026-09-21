---
name: "tweet-forge"
description: "Draft X/Twitter posts from a finding plus its numbers in a configured analyst voice: number in, structure out, every draft verified at 280 characters or under."
---

# Tweet Forge

## Purpose
Turn a finding plus its numbers into 2-3 post-ready tweet drafts in the voice you configure. Trigger on any tweet drafting request: "draft a tweet", "tweet this", "X post about", a regular posting habit, or similar.

## Setup (do once)
Fill in the two config files under `config/`:
- `config/account.md`: your handle, timezone, posting cadence.
- `config/voice.md`: your voice profile. Patterns, anti-patterns, register. Paste 3-5 of your own past posts as calibration samples, or write the rules directly.

Without a filled-in voice profile the skill drafts in a neutral analyst register. That is the documented fallback, not a failure.

## Workflow
1. **Extract the inputs.** You need a finding and at least one hard number. If the user gives a topic without figures, ask for the numbers. Never invent figures. If a figure must come from a source, verify it with a web search before drafting.
2. **Load the voice.** Read `config/voice.md` (voice patterns, anti-patterns) and any style guide it points to. Write in that voice from the first word; do not draft generic and humanize after.
3. **Forge 2-3 drafts.** Each draft uses a different labeled pattern (e.g. number-first hook, falsification dare, contrast pair, arithmetic demolition, named-mechanism closer). Vary the angle, not just the wording.
4. **Verify length.** Check every draft with `printf '%s' "$draft" | wc -m`. Every draft must be 280 or under. If one runs long, compress it: cut adjectives first, then clauses, never the number.
5. **Present.** Show each draft verbatim with its character count and pattern label, so the reader can see which move each one uses.

## Output Contract
- 2-3 drafts, each on its own, copy-paste ready.
- Each labeled: pattern name + character count.
- No commentary between drafts beyond the labels.
- End with one line: which draft you would pick and why, in one sentence.

## Operating Rules
1. Numbers are load-bearing. An assertion without a figure breaks character; do not produce one.
2. Approval of draft wording is not approval to publish. Nothing posts without the user's explicit yes.
3. Do not repeat a topic used within the last seven days. Check the posting log named in `config/account.md` and recent memory before drafting.
4. If the finding touches an active research thread, keep the figures consistent with the published numbers.
5. The defaults below come from the original author's voice profile; replace them with your own in `config/voice.md`:
   - banned patterns: "it's not X, it's Y" antithesis, em dashes, semicolons, hashtags, engagement bait ("thoughts?"), questions left hanging.
   - third person, institutional voice. Direct address only inside a falsification dare.
