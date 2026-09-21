# Curated links (research 2026-09-21; URLs verbatim from the coordinator's findings)

## Tier 1 — pure CSS reference implementations
1. Bramus canonical stacking-cards demo — https://scroll-driven-animations.style/demos/stacking-cards/css/ — pure CSS, the reference implementation most demos descend from.
2. EaseMotion ease-stacked-scroll-deck — https://github.com/likhitha827/easemotion-css/blob/HEAD/submissions/examples/ease-stacked-scroll-deck/README.md — zero-JS deck pinning cards via `animation-timeline: view()` + `animation-range: exit-crossing`; documents a reduced-motion kill-switch.
3. EaseMotion ease-scroll-stack 3D deck — https://github.com/devmaster1987/easemotion-css/blob/HEAD/submissions/examples/ease-scroll-stack/README.md — real `perspective` + `translateZ` depth with reduced-motion stripping 3D.
4. animation-handbook Stacking Cards — https://github.com/matinmonshizadeh/animation-handbook/blob/HEAD/animations/01-scroll-based/stacking-cards/README.md — named view-timeline with per-card exit slices, hand-written rAF fallback, production notes (peek-tab offsets, sticky run-out trap); model flat/static fallback.
5. dontdevpanic scroll-driven-animations-showcase — https://github.com/dontdevpanic/scroll-driven-animations-showcase — eight-section gallery (reveals, multi-layer parallax, `@property` counters with no JS, stacking cards); `@supports` fallback + reduced-motion baseline; pure CSS, zero JS.
6. Codrops practical intro to `scroll()` and `view()` — https://tympanus.net/codrops/2024/01/17/a-practical-introduction-to-scroll-driven-animations-with-css-scroll-and-view/ — single-file CodePen demos; `timeline-scope` pattern shows one element's timeline driving a distant element (the spine-fill mechanism); gate-nesting reference.
7. Keith Clark pure-CSS parallax — http://keithclark.co.uk/articles/pure-css-parallax-websites/ — the `perspective` + `translateZ(-Npx)` + compensating `scale()` recipe; exact math for the numeral background layer.

## Tier 2 — vanilla JS (dependency-light)
8. Scrollama — https://github.com/russellsamora/scrollama/blob/HEAD/README.md — newsroom-standard (~2KB, IO-based, no scroll listeners); step enter/exit/progress driving a sticky graphic; used by ProPublica, WaPo, Pudding; step progress can fill the spine.
9. Scrollama demo pen — https://codepen.io/aw207/pen/BXwVPa — single-file sticky-graphic skeleton; drop each chapter's key figure into the graphic slot.

## Tier 3 — GSAP-dependent (comparison only, not for this build)
10. Codrops sticky-section animation ideas — https://tympanus.net/codrops/2024/01/31/on-scroll-animation-ideas-for-sticky-sections/ — GSAP demos as choreography reference for chapter exits.
11. Codrops 3DStackMotion — https://github.com/codrops/3DStackMotion/ — 3D card-stack with rotations; the aspirational end of pull-forward, flattenable to pure CSS.
12. PixelPerfectLabs card-stacking-gsap — https://github.com/YT-PixelPerfectLabs/card-stacking-gsap — the "compare against" baseline showing what CSS saves (~60KB+ runtime, main-thread scroll handlers).

## Tier 4 — articles, guides, hard-won lessons
13. web.dev high-performance CSS animations — https://web.dev/articles/animations-guide — "Avoid any property that triggers layout or paint unless it's absolutely necessary."
14. MDN scroll-driven animations guide — https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations — canonical definitions with `@supports` fallback example.
15. CSS-Tricks bringing back parallax — https://css-tricks.com/bringing-back-parallax-with-scroll-driven-css-animations/ — `scroll()` for page-driven motion, `view()` for element-driven.
16. CSS-Tricks practical scroll-linked use cases — https://css-tricks.com/practical-use-cases-for-scroll-linked-animations-in-css-with-scroll-timelines/?ref=csslayout.news — playbook for the layered chapter treatment (parallax, reveals, progress, scrollspy).
17. CSS-Tricks viewport units on mobile — https://css-tricks.com/the-trick-to-viewport-units-on-mobile/ — use `dvh`, never raw `100vh`.
18. Codrops sticky-grid scroll (March 2026) — https://tympanus.net/codrops/2026/03/02/sticky-grid-scroll-building-a-scroll-driven-animated-grid/ — current sticky-plus-scroll-driven construction for stacks and reveals.
19. Kevin Powell CSS-only scroll-based animations — https://www.youtube.com/watch?v=UmzFk68Bwdk — `scroll()`, `view()`, `animation-range` with an explicit reduced-motion section.
20. Kevin Powell short version — https://www.youtube.com/watch?v=bBh8fpb3h5c — linking keyframes to scroll position.
21. CSS-only stacking cards with view-timeline and perspective — https://www.youtube.com/watch?v=Pb0vBPXvM-I — exactly the planned card-stack technique, zero JS.
22. Bramus on codeTV — https://codetv.dev/series/learn-with-jason/s6/css-only-scroll-driven-animation-and-other-impossible-things — "They are not essential to how the website should work... you still get to see the style thing, but it won't animate on scroll."
23. Chrome modern-web-guidance scrollytelling — https://github.com/googlechrome/modern-web-guidance/blob/HEAD/skills/modern-web-guidance/guides/ui-behaviors/scrollytelling.md — native CSS where supported, IO/scroll-listener fallback; motion is decoration.
24. NativeCSS stacked-card fallback commit — https://github.com/skerbis/nativecss/commit/38cf100d9beb71d71b99e5fb730dcc07dcc1a380 — flat baseline, JS self-disables with `CSS.supports()` and respects reduced motion.
25. Addy Osmani adaptive loading — https://dev.to/addyosmani/adaptive-loading-improving-web-performance-on-low-end-devices-1m69 — `saveData`, `hardwareConcurrency`, `deviceMemory` are hints, never reliable classifications.
26. TanStack iOS scroll write-up — https://github.com/tanstack/tanstack.com/blob/HEAD/src/blog/tanstack-virtual-perf-and-ios.md — writing `scrollTop` during iOS momentum cancels it and causes a visible snap.
27. Practitioner commit on fixed backdrop-filter bars — https://github.com/sarastrist-crypto/tristian-walker-web/commit/139bca1fd1331432815668178209abcdb691b75d — fixed `backdrop-filter` is a severe iOS scroll cost; swap to near-opaque solid on mobile.
28. dev.to sticky-not-working — https://dev.to/robmarshall/how-to-fix-issues-with-css-position-sticky-not-working-4a18 — keep `overflow: visible` on every sticky ancestor.
29. W3C CSSWG scroll-animations explainer — https://github.com/w3c/csswg-drafts/blob/HEAD/scroll-animations-1/EXPLAINER.md — main-thread scroll handlers can never stay perfectly synchronized; why compositor timelines exist.
30. Firefox performance docs on scroll-linked effects — https://github.com/browserworks/waterfox/blob/HEAD/docs/performance/scroll-linked_effects.md — async scrolling makes JS-driven effects laggy/janky/jittery.
31. jh3y CodePen pens (fetch failed during research; treat as unverified leads) — https://codepen.io/jh3y/pen/MWzQvKK and https://codepen.io/jh3y/pen/xxQdPae — Apple-style scroll text reveals, horizontal scroll-transform choreography.

## Coverage gaps (honest)
- No pen found that is literally an oversized-sticky-number background parallax layer or a vertical spine with progress fill; both are two-piece builds (Keith Clark depth recipe + `view()` ranges; Scrollama step progress + `timeline-scope`).
- No canonical Stack Overflow/r/webdev thread surfaced; dev.to items 24/25/28 are the closest equivalents.
- Support statements conflict across dated articles: Safari 26 (Sept 2025) shipped scroll-driven animations; older pieces say otherwise. Always version support claims with a date; older iOS Safari gets the flat fallback.
