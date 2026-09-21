# Test Suites

Public suites for self-testing a browser fingerprint before a run. Each answers a different question; none is a superset of the others.

- **bot.sannysoft.com** — smoke test for headless Chrome tells. Passing proves you are not running an *unmodified* headless browser; serious tooling clears it on day one. Also runs three canvas tests inside an iframe and compares them: a consistency check, not just a fingerprint check.
- **CreepJS** — asks whether you are *lying*, not what you report. Takes clean copies of built-ins from a fresh iframe, walks descriptors and prototypes, inspects stack traces, and names each blocked probe as a lie. A high score means nothing here contradicts anything else here: the consistency test.
- **BotD (FingerprintJS bot detection)** — returns a verdict rather than a fingerprint. Most of its detectors really ask *which engine you are* by testing behaviors that differ between engines.
- **BrowserLeaks** — per-surface readings (WebRTC, canvas, WebGL, fonts) rather than a verdict. Reach for it when you want to read a specific value instead of a score.
- **FingerprintJS (open source)** — returns a visitor ID, a hash of many components. Answers "can I be recognized again," which is a different question from "do I look automated." The commercial version adds signals the open library lacks.

**How to use them:** test the layer you changed, not the whole stack. A green result on one suite says nothing about the rest. Run after each hardening change, and re-run periodically: detectors and these suites both drift.
