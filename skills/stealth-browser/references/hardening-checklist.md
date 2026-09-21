# Hardening Checklist

Pre-flight checklist for our own browser automation. Work top to bottom; each layer only matters if the layers above it are consistent. Community consensus tools, 2025-2026.

## Tooling (public, open or documented)

- **Camoufox** — community consensus best open-source anti-detect browser. Stealth Firefox fork with fingerprint rotation and `--humanize` mode. Starting point for protected sites.
- **Nodriver** — faster than Camoufox, slightly less stealthy; no WebDriver artifacts.
- **Pydoll** — CDP-native Python driver, good anti-detection, still maturing.
- **SeleniumBase (UC mode)** — undetected-chromedriver lineage, auto-CAPTCHA helpers for legitimate test flows.
- **curl_cffi / rnet** — HTTP-only work with real TLS impersonation; handles basic protection without a browser.

## Environment

1. **Hide automation flags.** `--disable-blink-features=AutomationControlled`; delete `navigator.webdriver` from the prototype. Verify it reads `undefined`, not `false`.
2. **Use a real browser profile.** Headed or headful-capable engine with real fonts installed. Never run detection-sensitive work on a bare headless server with SwiftShader rendering.
3. **Pin a common viewport.** Avoid odd resolutions; 1280x720 or 1920x1080 class sizes, with slight natural jitter.
4. **Complete the browser surface.** Plugins, languages, `window.chrome`, permissions API, and WebGL renderer strings should look like a consumer machine, not a container.

## Network

5. **Residential IP when stealth matters.** Datacenter IPs fail reputation checks first. Keep one IP per session; rotate between sessions, never mid-session.
6. **Geo-consistency.** Timezone, locale, and Accept-Language must match the egress IP's location. A proxy without geo-alignment leaks.
7. **Leak checks.** Test WebRTC, DNS, and timezone before running at scale.
8. **TLS/HTTP2 agreement.** The TLS profile, HTTP/2 frame ordering, header order, and User-Agent must describe the same browser and OS.

## Behavior

9. **Humanize input.** Bezier mouse paths, Gaussian-distributed delays between actions, variable typing speed, random scroll patterns. Camoufox `--humanize` covers the baseline; Turnstile-class behavioral checks need it on.
10. **Plausible pacing.** No constant intervals. Randomize delays; act in sequential, purposeful steps.
11. **Real entry points.** Land on the homepage or a search page with a referrer; navigate inward like a user. Never deep-link cold to the target URL.
12. **Handle the chrome of the web.** Dismiss cookie banners and consent dialogs before acting; overlays block clicks and skipping them looks non-human.

## Session

13. **Persist state.** Reuse browser profiles, cookies, and storage across runs. Keep `cf_clearance`-class cookies alive.
14. **One identity per session.** Same IP, same fingerprint, same cookies for the whole session. Rotating any of them mid-session is a flag.

## Escalation ladder

```
plain browser
  -> stealth browser (Camoufox / Nodriver / Pydoll)
    -> stealth + residential proxy + geo-alignment
      -> STOP: report the block
```

- Start at the lightest tier that could work; escalate only after a confirmed block.
- Same configuration failing twice = change something or stop. Never retry unchanged.
- A block surviving stealth + proxy means escalation is exhausted. Report it plainly; do not burn compute or risk the IP.

## CAPTCHA policy

CAPTCHAs are a hard stop. Either hand the session to the user or use a pre-authenticated profile the user set up. No solving services, no automated retries against the challenge.
