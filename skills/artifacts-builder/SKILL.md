---
name: "artifacts_builder"
description: "Design and build interactive frontend web artifacts, HTML dashboards, and UI components. Use when the user asks to build, design, or prototype a web app, dashboard, widget, or interactive UI component."
---

# Artifacts Builder

## Purpose
Ship self-contained, interactive frontend web artifacts: dashboards, single-page apps, widgets, UI prototypes.

## Route first
This runtime builds hosted web artifacts through the `artifact` namespace, not by hand-writing pages:
- Hosted page or app anyone can open from a link, no saved state → `artifact.create_web_static`.
- Hosted app that must save what the user enters → `artifact.create_web_fullstack`.
- Local single-file HTML dashboard or file deliverable (the Table 6 monitoring dashboard pattern) → build it yourself with the workflow below, then deliver it as a file artifact (`artifact.create_file`, kind `other`, html) or attach it directly.

This skill governs the design and quality bar for all three routes. When delegating to an `artifact` builder, translate the workflow below into `verbatim_request`: what it is, what it does, the data it carries, the interactions, the design tokens.

## Workflow
1. **Clarify the job.** What question does it answer, or what action does it enable? Get the data or its source before building. Never ship invented demo data presented as real. If he hasn't supplied data, ask once, briefly.
2. **Plan component architecture.** State requirements, interactive elements (filters, tabs, modals, charts), layout structure. One screen, one job.
3. **Design tokens.** Default to his brutalist/neon brutalist register: hard borders, sharp corners, high-contrast neon accents on dark ground, monospace data type, dense information layout. Soften only when the artifact's audience demands it.
4. **Single-file distribution.** Self-contained HTML: Tailwind via CDN or hand-rolled CSS, charts via a pinned stable CDN (or inline SVG for simple series), icons inlined. No build step, no broken links, no placeholder methods.
5. **Interactivity.** Real state handling: filters recompute, tabs switch, inputs validate. Every control must do something; a decorative control is a bug.
6. **Copy.** Dense, evidence-first labels. No lorem ipsum, no "Welcome to your dashboard" filler.

## Output contract
- A complete, runnable file, or a precise builder brief for the `artifact` namespace.
- Responsive and mobile-usable.
- All copy real; all numbers sourced or labeled as his own data.
- Verification: render or open it (or confirm the builder's result) before handing it over.

## Operating rules
1. Never promise sample or demo data; ask for the real data or build the input UI first.
2. No external asset that can 404: pin stable CDN versions, inline what is small.
3. Default to his brutalist/neon register unless he says otherwise.
4. One artifact, one slug, one job; extend with `artifact.edit`, never a second create.
5. Hand it over attached or as a card in the same message, never "it's ready, go find it."
