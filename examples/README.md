# This file explains the sample data next to it.

`shadow-log-excerpt.jsonl` holds four illustrative entries in the exact
format the router writes to `skills/jev-router/logs/router.jsonl`.
They are samples, not a real log: read them to see what a calibration
pass looks like before you have your own week of data.

What to notice:
- Every entry carries the full probability distribution and the margin
  between the top two options, not just the winner.
- The `publish` entry escalates at 0.93: irreversible actions route to a
  human in both modes.
- The `retry` entry denies at 0.66: a fourth retry of the same failed
  fetch is low-value, and Jev says skip.
- `mode` is `shadow` throughout: these decisions were logged, not
  enforced. Your thresholds come from scoring entries like these against
  your own judgment. See `docs/shadow-mode.md`.
