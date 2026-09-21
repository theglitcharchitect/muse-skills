# Brief template (DELTA WATCH v2.0 output format)

Two parts, plain prose and tables, no JSON ever, scannable in 2-3 minutes. The cell production architecture is internal and never appears as a header. One voice, one brief.

## PART 1 - THE BRIEF

- **HEADER** - `DELTA WATCH - [EDITION] - [date, Asia/Dhaka time] - lookback [window] - stale-by [horizon]`
- **BLUF** - 3-5 bullets, most decision-relevant developments, each tagged `[FACT]/[INFERENCE]/[SPECULATION]` plus source grade plus analytic confidence.
- **DOMESTIC** - by domain, only what changed since the last edition; source grade in brackets.
- **EXTERNAL/GEOPOLITICS** - bilateral and regional movements, same format.
- **STRATEGIC VECTORS** - vector map (`references/vectors-elite.md` section 1) for the top 2-3 stories.
- **CONNECTING THE DOTS - ELITE READ** - the elite-cognition block (`references/vectors-elite.md` section 2) for the top story, plus comparative capitals; link analysis (section 3) if three or more actors are load-bearing.
- **ON THE ARC** - where today's items sit on the standing arcs (`references/watch-architecture.md`), plus any live deep-layer mechanism, advancing/stalling/reversing; explicit "no arc" note for anything genuinely orthogonal.
- **ANOMALIES** - the standing needle-hunt output; "none this cycle" is a valid and expected entry most days.
- **WHAT'S BEING SPUN** - 1-3 narratives, who benefits, your read; name any myth explicitly refused per the disinformation firewall.
- **RED TEAM** (Net Assessment + Needle only) - strongest counter-read plus confidence adjustment.
- **WATCHLIST** - prioritized tripwires: signal to watch, why it matters, likelihood on the ladder.
- **GAPS** - unverified items, `INSUFFICIENT DATA` entries, coverage gaps. Never papered over.

## PART 2 - STANDING DATA APPENDIX (plain Markdown tables, carried run to run)

Every forecast, indicator, watchlist item, actor, and anomaly in Part 1 appears here with a stable ID (`FC-YYYY-####`, `WL-###`, `ACT-##`, `AN-YYYY-####`). IDs persist across runs. Use `n/a` for unknowns, never a guessed number.

**A. Indicator Board** - refresh each run; carry forward with a staleness note if no new print. Flag anything moving faster than its own 3-month baseline.

| Indicator | Latest | As-of | Prior | Next release | Trend/velocity | Grade |
|---|---|---|---|---|---|---|
| FX reserves (gross / BPM6 net) | | | | | | |
| Taka: official vs kerb + premium | | | | | | |
| CPI (headline / food) | | | | | | |
| Monthly remittance | | | | | | |
| Monthly RMG export (+ US share) | | | | | | |
| Private-sector credit growth | | | | | | |
| Call money rate | | | | | | |
| IMF review status/date | | | | | | |

**B. Forecast Ledger** - every forecast/tripwire issued; resolve due items each Net Assessment.

| ID | Issued | Claim | Likelihood (ladder) | Stale-by | Status | Resolved by |
|---|---|---|---|---|---|---|

**C. Watchlist Tracker** - lifecycle for each tripwire.

| ID | Signal | Why it matters | Likelihood | Status | Review by |
|---|---|---|---|---|---|

**D. Actor Registry** - power is a trajectory, not a snapshot.

| ID | Actor/faction | Role | Access trend | Note |
|---|---|---|---|---|

**E. Events Calendar** - forward-dated known events driving the AGENDA edition: IMF review windows, national budget, ICT/tribunal hearing dates, election-roadmap milestones, court verdicts, GSP+/LDC-graduation deadlines, monthly data releases, summits and visits.

| Date | Event | Arc | Why it matters |
|---|---|---|---|

**F. Anomaly Log** - every AN-tier item, tracked to resolution.

| ID | Surfaced | Type (numeric/temporal/absence/structural/narrative) | Description | Confidence | Status | Resolved by |
|---|---|---|---|---|---|---|

**G. Calibration Note** (Needle, or when enough forecasts resolve) - of the calls rated "likely" or higher, how many actually happened; state whether the system runs over- or under-confident and correct forward.

**H. State Carry** - open forecast IDs, open watchlist IDs, open anomaly IDs, standing-story IDs. If state could not be loaded this run, say so here and list what was reconstructed versus genuinely lost.
