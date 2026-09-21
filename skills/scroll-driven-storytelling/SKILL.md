---
name: "scroll-driven-storytelling"
description: "Build scroll-driven motion pages (scrollytelling): CSS scroll-driven animations, sticky card stacks, 3D perspective depth, parallax layers, figure reveals, reduced-motion and low-end fallbacks. Trigger on: series index, scroll animations, scrollytelling, card stack, parallax, case-file desk, 'like those video websites'."
metadata: { "includeInPrompt": true }
---

# Scroll-driven storytelling

## Purpose
Build narrative web pages where scrolling drives layered motion: chapter cards pulling forward from a stack, oversized sticky numbers in a background parallax layer, a progress spine, per-chapter figure reveals. Dependency-free: CSS scroll-driven animations + `position: sticky` as the primary engine, IntersectionObserver + one rAF loop as fallback. Motion is decorative and never required for content access.

## Workflow
1. **Plan the layers.** Map each planned component to a technique in `references/build-checklist.md`. Decide the 3D depth budget (modest: hundreds of px against ~1000px perspective) and which effects are scroll-linked vs reveal-on-entry.
2. **Build the static page first.** Complete flat layout, all content readable, no hidden states. This is fallback layer 1 and the no-JS experience. Never skip this.
3. **Add scroll-driven CSS.** Gate everything in `@supports (animation-timeline: scroll())` / `@supports (animation-timeline: view())`. Animate `transform` and `opacity` only. Author the un-animated end state as default styles.
4. **Add the JS fallback path.** One passive `scroll` listener + one rAF scheduler (reads before writes). IntersectionObserver for reveals and count-ups. Register only if `CSS.supports('animation-timeline','scroll()')` is false, or for effects CSS timelines cannot express. Target under 3KB of motion JS.
5. **Add reduced-motion and low-end layers.** All decorative motion inside `@media (prefers-reduced-motion: no-preference)`. `reduce` block flattens transforms, zeroes durations, skips the rAF loop. JS checks `matchMedia('(prefers-reduced-motion: reduce)')` and device hints (`saveData`, `hardwareConcurrency`, `deviceMemory`) before registering the loop; otherwise the page stays the flat-card stack.
6. **Verify.** Run the pre-ship matrix in `references/build-checklist.md`: Chrome / Safari (current + one old iOS) / Firefox stable / reduced-motion ON / JS disabled / low-end Android. Zero motion libraries in the final bundle.

## Output Contract
- A page whose base CSS is a complete, readable static page.
- Scroll-linked effects: compositor-thread where possible (`transform`/`opacity` only).
- Fallback chain, in order: static page → `@supports` scroll-driven enhancements → `no-preference` parallax/3D → JS fallback loop → reduced-motion static.
- No Three.js/WebGL, no GSAP, no scroll-hijacking (no mandatory vertical snap on the narrative flow).

## Operating Rules
1. Firefox stable has no CSS scroll-driven animations (verified 2026-09-21). Every scroll-linked CSS effect must degrade to a static end state or have an IO + rAF fallback. Never claim "supported in all major browsers."
2. Only `transform` and `opacity` animate on scroll. Layout properties (`top`, `height`, `width`) and paint properties (`box-shadow`, `color`) per frame are a hard no.
3. `position: sticky` breaks under any ancestor with `overflow: hidden/scroll/auto`. Keep sticky ancestors `overflow: visible`. Sticky threshold is mandatory.
4. `overflow: hidden`, `filter`, `clip-path` on ancestors flatten `preserve-3d` contexts. Keep them off the 3D subtree.
5. `translateZ(-d)` shrinks apparent size; compensate with `scale(1 + d/perspective)`.
6. Use `svh`/`dvh` units, never raw `100vh`.
7. `will-change` is surgical: one moving element, pre-warmed one viewport ahead via IO, removed on settle.
8. Never write `scrollTop` during iOS momentum scrolling; it cancels momentum and snaps visibly.
9. Hidden "from" states only ever apply under `no-preference` or a `.js` guard added by JS. No-JS browsers see everything visible.
10. Keep the spine and JS-measured elements outside `content-visibility: auto` subtrees.
11. `scroll-snap-type: mandatory` on the vertical narrative flow is banned; it fights sticky cards and keyboard scrolling.

Full research report (31 curated links, every code pattern, platform traps): `~/workspace/newsroom/research/scroll-motion-research-report.md`.
