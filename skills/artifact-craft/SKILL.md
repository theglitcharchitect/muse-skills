---
name: "artifact_craft"
description: "Practitioner quality bar for interactive web artifacts and dashboards: information hierarchy, chart selection, low-friction interactivity, mobile/touch behavior, accessibility, performance, and a pre-ship checklist. Use when reviewing, hardening, or refining an artifact that is already planned or built."
---

# Artifact Craft

## Purpose
Turn a working artifact into a good one. This is the review and hardening pass, drawn from current practitioner guidance (2026 dashboard audits, Core Web Vitals practice, WCAG): what separates artifacts people keep using from ones they abandon. Complements `artifacts_builder`, which owns the build routes, design tokens, and build workflow.

## Workflow
1. **Audit first.** Run `references/pre_ship_checklist.md` against the artifact. Fix fails before adding polish.
2. **One screen, one decision.** Cut to 5-9 key metrics on the main view. Every remaining number must inform a decision; kill vanity metrics and the metric graveyard.
3. **Hierarchy.** Primary KPI top-left and large, secondary supporting, tertiary in tables. Sections get headings and breathing room. No same-weight-everywhere layouts, no important content in the bottom corner.
4. **Right chart for the data.** Use `references/chart_selection.md`. Let the data pick the chart, not preference.
5. **Context for every number.** Compare against a previous period or a target. Annotate spikes and dips. Show last-updated or data freshness. A lone number tells nothing.
6. **Frictionless interactivity.** Sensible filter defaults so the page answers the core question immediately on load, no five-click setup. Every control must do something; a decorative control is a bug.
7. **Mobile pass.** Three breakpoints: ≥1024 desktop layout unchanged, 768-1023 two-column cards, <768 single column. Filters collapse behind a toggle with an active-count badge. Tables become cards. 44px minimum touch targets. Modals go full-screen. KPI strip in a 2-column grid. 16px body text.
8. **Accessibility pass.** WCAG AA text contrast (4.5:1 minimum). Never encode meaning by color alone: add labels or patterns, then grayscale-test. All controls keyboard-operable. Honor `prefers-reduced-motion`.
9. **Performance pass.** Good band at p75: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1. Keep initial JS under ~200KB gz. Lazy-load below the fold. Explicit width/height on all media. Defer or facade third-party scripts. `font-display: swap` on custom fonts.
10. **Re-run the checklist, then ship.**

## Output Contract
- The hardened artifact, or a precise list of checklist fails with fixes.
- All copy real, all numbers sourced or labeled as the user's own data.
- Stale data flagged with its age; never silent.

## Operating Rules
1. Audit before adding: a failing bar is never fixed by more widgets.
2. Cut before adding: a metric that cannot change a decision leaves.
3. Mobile is not a shrunken desktop; reflow content, don't scale it.
4. Performance is a design constraint, not a final step; re-audit after every major change.
5. Never present generated or sample data as fact.
6. One artifact, one slug, one job; changes go through the artifact's edit route, never a second create.
