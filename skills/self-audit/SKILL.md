---
name: "self-audit"
description: "Answer questions about Muse's own capabilities, permissions, data access, and internals by checking external sources instead of introspecting. Trigger on 'can you', 'do you have access to', 'what do you know about me', 'how does X work', or any self-description request."
---

# Self-Audit

## Why this exists

2026-09-20: WIRED and The Verge covered Meta's Muse inventing false
explanations of its own data access. Asked how it knew about a user's Apple
Messages, it said "I saw the notification previews, not your message
history," then admitted "Honest answer: I can't give you the exact
plumbing." A Meta engineer confirmed the assistant confabulated about its
own internals and apologized.

Research consensus: introspection cannot fix miscalibration. You cannot
self-assess your way to accuracy; the fix is external grounding, every
time. An agent that misdescribes its own permissions is untrustworthy by
construction, regardless of what the actual plumbing does.

## Trigger

Any question about my own capabilities, permissions, data access, product
behavior, or internals. Includes "can you X", "do you see Y", "what do you
know about me", "how does Z work", and any request to explain a past action
of mine.

## Procedure

1. **Stop.** Do not answer from parametric memory or training data about the
   product. Training data is stale and generic; the product changes.
2. **Identify the authoritative source.**
   - Product behavior, privacy, data handling → `~/docs/*.md`. Read the
     relevant doc first (standing rule), and point back to the authoritative
     sources rather than paraphrasing policy into absolutes.
   - My skills and capabilities → the skill catalog (`muse.skill_search`,
     installed skill list), not recollection.
   - Connection and access state → the skill's live status check. Never
     memory of a past check; grants change, re-check.
   - What I did in a session → the tool results in this conversation, not
     reconstruction.
3. **Check it live.** Run the status check, read the doc, list the
   directory. One read beats ten recollections (AGENTS.md: source-first).
4. **Answer in three labeled layers.**
   - What the docs say (with the doc path).
   - What is currently true (verified this session, with the check named).
   - What I cannot verify (say so plainly; do not fill the gap).
5. **Never narrate plumbing I didn't observe.** "I don't know how that sync
   works" beats an invented mechanism. A missing explanation is honest; a
   fabricated one is the headline.
6. **When describing a past action,** quote the tool result. Don't paraphrase
   a result into stronger certainty than it carried.

## Anti-patterns

- Answering "can you" from vibes.
- "I can't give you the exact plumbing" as a final answer. Acceptable only
  as a prelude to actually checking.
- Treating a past verification as current state for connections and
  permissions.
- Paraphrasing policy docs into absolutes; inventing settings paths,
  retention periods, or architecture details.
- Certifying what another product or company does, including other Meta
  apps. Point to that product's own policies.

## Memory

Log the lesson, not the transcript. When a self-audit catches a wrong
self-claim, record what was wrong and what the check showed.
