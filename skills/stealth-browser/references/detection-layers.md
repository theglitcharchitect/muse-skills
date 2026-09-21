# Detection Layers

What modern bot detectors check, roughly in the order a request encounters them. Sources: practitioner writeups and community research, 2025-2026.

## 1. Network layer (before the page loads)

- **TLS fingerprinting (JA3/JA4).** The ClientHello cipher-suite list, extension order, and elliptic-curve order produce a hash. Automation libraries (Python requests, curl, undetected HTTP stacks) produce hashes no real browser does. The server often knows before the page renders.
- **HTTP/2 fingerprinting.** SETTINGS frame values and their order, header order, and pseudo-header sequences are fingerprinted and cross-referenced against the TLS hash and the stated User-Agent. Any discrepancy = block.
- **TCP/IP fingerprint.** OS-level TCP window sizes and options should agree with the OS claimed in the User-Agent.
- **IP reputation.** Datacenter ASNs are cheap to flag; residential IPs cost more to judge; mobile IPs mostly force behavioral analysis. Proxy headers (`Via`, `X-Forwarded-For`) on transparent/anonymous proxies are trivial tells.

## 2. JavaScript property checks

- **`navigator.webdriver`.** The single most-checked flag. Real browsers: `undefined`. Automation: `true` (or `false` but explicitly set, which Chrome 88+ detectors also catch via property-descriptor inspection). Public countermeasure: `--disable-blink-features=AutomationControlled` plus prototype deletion.
- **Headless tells.** UA containing `HeadlessChrome`; `navigator.plugins` empty; `navigator.languages` missing; `hardwareConcurrency` stuck at the default 4; `window.chrome` / `chrome.runtime` incomplete or missing; `navigator.permissions` behaving non-standardly.
- **CDP side effects.** DevTools-protocol instrumentation leaves serialization artifacts (e.g., the known `Error` stack-getter probe) that pages can detect.

## 3. Execution-layer fingerprinting

- **Canvas hashing.** The page forces a hidden complex render (text, fonts, shapes), reads the pixels via `toDataURL`/`getImageData`, and hashes them. Font hinting, anti-aliasing, and the graphics stack make the hash hardware/software-specific. Headless Linux servers (Mesa/SwiftShader, missing consumer fonts) produce anomalous hashes.
- **WebGL disclosure.** `WEBGL_debug_renderer_info` reveals the real GPU string. Consumer laptops report `Intel Iris Xe` / `Apple M2`; servers report `SwiftShader` or `Mesa OffScreen` — an instant flag.
- **Font enumeration and audio fingerprinting.** Missing font sets and off-spec AudioContext output add corroborating signals.

## 4. Behavioral signals

- **Mouse and input.** Instant clicks, perfectly straight paths, zero scroll jitter, uniform keystroke timing. Human input follows Bezier-like curves with Gaussian-distributed pauses. Precision is the tell: humans are sloppy.
- **Timing.** Requests at constant intervals (e.g., every 500ms) are trivially detectable. Randomized, human-plausible pacing is the baseline fix.
- **Navigation patterns.** Deep-linking straight to a results URL with no referrer, or scraping hundreds of rows as fast as possible, reads as a bot. Real sessions start at entry points and move sequentially.

## 5. Session and cookie analysis

Real users carry cookies and maintain session continuity. Automation that ignores sessions, rotates IPs mid-session, or replays stateless requests looks like a different visitor on every hit — inconsistent identity is itself a signal. Cloudflare issues `cf_clearance` cookies after its JS checks pass; losing them means re-challenging.

## 6. Challenge and ML systems

- **Cloudflare (as of early 2026).** Layered: JA3/JA4 + HTTP/2 matching, lightweight JS detections, the "checking your browser" JS challenge (canvas/WebGL/navigator/timing), Turnstile's behavioral widget, behavioral analysis, and an ML bot score (1-99) folding in all signals plus IP reputation. Since March 2025, **AI Labyrinth** serves honeypot networks of AI-generated pages with invisible links to waste crawler compute and map bot patterns.
- **DataDome, PerimeterX (HUMAN), Akamai Bot Manager.** Commercial device-fingerprinting + behavioral ML stacks; similar signal sets, different model weights.
- **reCAPTCHA v3.** Score-based (no checkbox); low scores gate or block silently.
- **Anubis.** Proof-of-work challenge; usually passes with a real browser engine and a few seconds of compute.

## The meta-signal: cross-layer correlation

Detectors do not just score each layer; they check that layers agree with each other. TLS says Chrome on Windows, but the TCP fingerprint says Linux, the timezone says Dhaka, and the IP geolocates to Frankfurt: that disagreement is a stronger block signal than any single weak fingerprint. **Evasion is about agreement across layers, not perfection in one.** This is why IP-behavior clustering also works: 100 IPs with identical timing, headers, and fingerprints are one bot network no matter how clean each IP is.

## What none of this defeats

With enough resources any proxy or fingerprint can be detected; top residential setups still only reach roughly 70-90% success against Cloudflare Enterprise / DataDome / Akamai-class systems. The practical question is always whether detecting you is worth the target's cost.
