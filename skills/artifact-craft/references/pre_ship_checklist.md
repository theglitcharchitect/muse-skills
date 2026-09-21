# Pre-Ship Checklist

Run this against every artifact before handover. A fail blocks shipping.

## Content
- [ ] 5-9 key metrics max on the main view; nothing here is decorative
- [ ] Every number informs a decision; vanity metrics removed
- [ ] One clear audience; no exec-summary-next-to-analyst-deep-dive mixing
- [ ] All copy real; no lorem ipsum, no filler headers
- [ ] No invented demo data; sample data labeled as sample, never as fact
- [ ] Data freshness shown (last-updated timestamp); stale data flagged

## Layout
- [ ] Primary KPI top-left and largest; visual weight matches importance
- [ ] Sections separated with headings and breathing room
- [ ] Charts at the same level share heights
- [ ] F-pattern scanning path; nothing critical in the bottom corner

## Visualization
- [ ] Chart type matches the data structure (see chart_selection.md)
- [ ] Every number has a comparison: previous period, target, or benchmark
- [ ] Spikes and dips annotated on the chart
- [ ] Consistent names, colors, and time grains for the same metric
- [ ] No truncated y-axes, no dual y-axes, no >5-segment pies

## Interactivity
- [ ] Page answers the core question on load with sensible defaults
- [ ] Every control works; none is decorative
- [ ] Filters apply consistently across all charts

## Mobile
- [ ] <768px: single column, no horizontal scroll
- [ ] Filters collapse behind a toggle with active-count badge
- [ ] Tables render as cards on mobile
- [ ] 44px minimum touch targets
- [ ] 2-column KPI grid, 16px body text on mobile

## Accessibility
- [ ] WCAG AA text contrast (4.5:1)
- [ ] Meaning never encoded by color alone; grayscale test passes
- [ ] All controls keyboard-operable
- [ ] `prefers-reduced-motion` honored

## Performance
- [ ] p75 LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1
- [ ] Initial JS under ~200KB gz; below-fold content lazy
- [ ] Explicit width/height on all media
- [ ] Third-party scripts deferred or facaded, never unaudited
- [ ] `font-display: swap`; minimal font weights
