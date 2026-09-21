# Terminology glossary (support verified 2026-09-21 vs MDN compat data + caniuse)

## CSS Scroll-driven Animations — the primary engine
`@keyframes` driven by scroll progress instead of time. `scroll()` = a scroll container's top-to-bottom progress; `view()` = a subject element's own passage through the scrollport. `animation-range` trims the timeline slice (`entry`, `exit`, `cover`, `contain`, percentages). Named-timeline plumbing (`scroll-timeline-name`, `timeline-scope`) shares one timeline across elements. Drives spine fill (`scroll(root)` → `scaleY`), numeral drift (`view()` with `exit` range), card press-down, figure reveals. Zero JS, compositor-thread. Support: Chrome/Edge 115+, Safari 26+ (Sept 2025), Firefox behind a flag only (~84% global). **Firefox stable has none of this** — `animation-range-start`/`animation-range-end` and `timeline-scope` are unimplemented even in Nightly (bug 1676779); Interop 2026 focus area, no ship date. Every scroll-linked CSS effect needs an IO + rAF fallback or a static end state.

```css
.spine-fill { transform: scaleY(0); transform-origin: top; }
@supports (animation-timeline: scroll()) {
  .spine-fill { animation: fill linear both; animation-timeline: scroll(root block); }
  @keyframes fill { to { transform: scaleY(1); } }
}
.card { opacity: 1; translate: none; }
@supports (animation-timeline: view()) {
  .card { animation: rise linear both; animation-timeline: view();
    animation-range: entry 10% cover 35%; }
  @keyframes rise { from { opacity: 0; translate: 0 32px; } }
}
```

## position: sticky — the layout backbone
Hybrid of `relative` and `fixed`: scrolls normally until it hits the threshold, then sticks within its nearest scrolling ancestor's box. Chapter cards sticking at `top: 0` so each new card slides over the last; numerals stuck mid-viewport; the spine pinned alongside chapters. Replaces GSAP ScrollTrigger pinning with zero JS. Support: Chrome 56+, Firefox 32+, Safari 6.1+ (Widely). Breaks if any ancestor has `overflow: hidden/scroll/auto`; threshold mandatory; `-webkit-sticky` for Safari < 13.

## perspective + transform-style: preserve-3d + translateZ — the depth
`perspective` on a parent sets viewer distance from z=0 (smaller = more dramatic depth); children at different `translateZ()` depths; `preserve-3d` keeps one shared 3D space. Numeral layer back (`translateZ(-300px)`), cards at z=0, pull-forward cards toward viewer (`translateZ(60px)`). Deeper layers move slower: parallax with no JS. Support: Chrome 36+, Firefox 16+, Safari 6.1+ (Widely). Gotchas: `overflow: hidden`, `filter`, `clip-path` on ancestors flatten the context; Safari quirks with `preserve-3d` + `position: fixed` descendants; keep depth modest (hundreds of px against ~1000px perspective).

## translateZ scale-compensation math (Keith Clark recipe)
`translateZ(-d)` shrinks apparent size; compensate with `scale = 1 + (d / perspective)`. Example: `perspective: 1000px` + `translateZ(-400px)` needs `scale(1.4)`: `transform: translateZ(-400px) scale(1.4);`. Pure math on top of `perspective`, universally supported.

## IntersectionObserver — the universal fallback
Async visibility-threshold reporting, off the critical path; one observer serves many elements, `rootMargin` shifts the trigger line. Adds `.is-in` classes in Firefox, drives figure reveals and count-ups, lazy-starts rAF effects, scrollspy for the spine. Cannot do continuous scrub motion (crossings, not positions); pair with rAF. Support: Chrome 51+/Edge 15+, Firefox 55+, Safari 12.1+ (Widely). Pattern: guard hidden states behind a `.js` class added by JS; `threshold: 0.15, rootMargin: '0px 0px -10% 0px'`; `io.unobserve(e.target)` to fire once.

## JS scroll progress — the Firefox fallback for fills
`progress = scrollY / (documentHeight - viewportHeight)` clamped 0..1; pinned-scene variant `-sectionRect.top / (sectionHeight - viewportHeight)`. Writes on `transform` only: `el.style.transform = \`scaleY(${p})\``.

## Card-stack / pull-forward
Full-viewport cards each `position: sticky; top: 0`; each incoming card slides over the pinned one beneath. Pull-forward refinement: scale the covered card down slightly proportionally to how far the next card has arrived. Per-card `top` offsets (`calc(var(--i) * 24px)`) leave slivers of buried cards visible as the stack's edge (case-file pile metaphor). Static fallback is just the sticky stack without scaling.
```css
.stack-card { position: sticky; top: calc(var(--i, 0) * 24px); min-height: 100svh; }
```

## Scroll snapping
Declarative snap points. Defensible use: `scroll-snap-type: x proximity` on a horizontal figure strip inside a chapter. Mandatory vertical snapping on the chapter flow is banned: it fights sticky cards, parallax, and keyboard scrolling, and is a motion-sickness trigger. Snap events (`scrollsnapchange`) are Chromium 129+ only; never depend on them.

## Compositor-only properties (transform, opacity) — the performance law
Pipeline: style → layout → paint → composite. `transform`/`opacity` skip layout and paint; the compositor reuses the painted layer on the GPU thread: 60fps during scroll. Animating `width`/`top`/`margin` forces full layout recalc per frame; `color`/`box-shadow` force repaint; both jank, worst on mid-range mobile. Spine grows with `scaleY`, not `height`.

## content-visibility — a loading tool, not a motion tool
`content-visibility: auto` skips rendering offscreen subtrees until near the viewport; `contain-intrinsic-size: auto 1400px` reserves placeholder size so the scrollbar does not jump. Wrap each chapter; keep the sticky spine and JS-measured elements outside `auto` subtrees. Support: Chrome 85+ (`auto` from 108), Firefox 125+, Safari 18+. Unsupported browsers ignore it.

## will-change discipline
Hint promoting an element to its own compositor layer ahead of time, avoiding first-frame hitch. Surgical only: `will-change: transform` on the one moving card, pre-warmed one viewport ahead via IntersectionObserver (`rootMargin: '100px'`), removed on settle. Dozens of promoted layers exhaust mobile GPUs and make things worse.

## requestAnimationFrame scroll handling — the lightweight JS engine
The `scroll` listener is `{ passive: true }` and only schedules one rAF callback; the callback does all reads first, then all writes, once per frame. One global loop drives spine progress (Firefox), card-stack scaling, numeral parallax offsets where CSS timelines are unavailable, count-ups. Never read `getBoundingClientRect`/`offsetTop`/`scrollHeight` inside the handler; cache, invalidate on resize.

## prefers-reduced-motion — first-class static fallback
Parallax, scroll jacking, large-area motion trigger vestibular disorders; fades are generally fine, spatial displacement/parallax/scaling/rotation are the triggers. Under `reduce`: flatten translateZ depth, kill parallax drift and card scaling, show final states, skip the rAF loop; the spine becomes a static indicator. All decorative motion nested inside `@media (prefers-reduced-motion: no-preference)`; JS gate `matchMedia('(prefers-reduced-motion: reduce)').matches` before registering the loop.

## CSS vs GSAP ScrollTrigger — verdict: stay dependency-free
CSS gives zero JS bytes, compositor-thread motion, declarative syntax, automatic reduced-motion gating; covers every effect in this brief. Weaknesses: no Firefox stable support, no pinning model (use `sticky`), no JS callbacks (IO covers that), no scrub smoothing. ScrollTrigger buys pinned-and-scrubbed multi-element choreography identical in Firefox; costs ~25KB gzipped plus main-thread motion that janks on low-end devices. Revisit ScrollTrigger only if a page demands true pinned-and-scrubbed multi-element choreography pixel-identical in Firefox, as the fallback path, not the primary engine.
