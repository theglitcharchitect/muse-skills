---
name: "stealth_browser"
description: "Browser bot-detection literacy and legitimate automation hardening: how detectors fingerprint automation (TLS, canvas/WebGL, navigator tells, behavior, IP reputation, challenge systems) and how to make our own browser work behave like a real user without tripping them. Use when a browser task hits blocks, challenges, or CAPTCHAs, or when hardening automation before a run."
---

# Stealth Browser

## Purpose
Understand what bot detectors look for so our own browser automation behaves like a real user. Legitimate use only: QA on our own services, monitoring, accessibility checks, research. Not a tool for bypassing protections to reach data we are not permitted to access.

## Workflow
1. **Diagnose the block.** Read the failure: instant TLS/reset or 403 before content = network layer; "checking your browser" interstitial or widget = JS challenge; CAPTCHA after some success = behavioral/IP scoring. Match it against `references/detection-layers.md`.
2. **Fix one layer at a time.** Apply the matching countermeasures from `references/hardening-checklist.md`, then retest. Never stack everything at once; you will not learn which layer was actually blocking.
3. **Verify with public suites.** Run the fingerprint through the test suites in `references/test-suites.md`. A green score on one suite says nothing about the others; test the layer you changed.
4. **Escalate on a ladder, then stop.** Start with the lightest workable setup and escalate: plain browser → stealth browser → stealth + residential proxy. If the same configuration fails twice, change something or stop. Do not burn retries.

## Operating Rules
1. Consistency beats perfection. One mismatched signal (TLS says Chrome, canvas says server GPU, timezone disagrees with IP) is a louder tell than any single weak layer. See `references/detection-layers.md` on cross-layer correlation.
2. Respect the target: obey `robots.txt`, rate limits, and terms of service. Keep request rates human; randomize intervals; never hammer a failing path.
3. CAPTCHAs are a hard stop for automation. Options are a human handoff or a pre-authenticated session the user set up themselves. No CAPTCHA-solving services, no retry loops.
4. Session hygiene: persist cookies and storage across runs, keep one IP per session, land on real entry points with referrers, act in sequential purposeful steps.
5. Never use these techniques against protections guarding data you are not authorized to access, and never bundle this knowledge into tooling for credential abuse, exploit kits, or malware.
