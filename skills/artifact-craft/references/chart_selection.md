# Chart Selection Guide

Match the chart to the question the data answers, not to what looks impressive.

| Question | Chart | Notes |
|---|---|---|
| Trend over time | Line | One metric per line; keep series ≤ 4 or split panels |
| Comparison across categories | Bar | Horizontal if labels are long |
| Part of a whole | Pie or donut | Max 5 segments; more than 5 → bar chart |
| Relationship between two variables | Scatter | Add trend line only if the correlation is real |
| Distribution | Histogram | Label bins in plain units |
| Exact values, records, drill-down | Table | Never force a chart where lookup matters |
| Single headline metric | KPI card | Always paired with a delta or target |

## Common visualization mistakes (from practitioner audits)

- **Truncated y-axes.** Exaggerates small changes; start at zero unless there is a stated reason.
- **Dual y-axes.** Nearly unreadable; use two separate charts.
- **Pie with too many segments.** Max 5, then switch to bars.
- **Numbers without comparison.** Every metric needs a previous period, a target, or a benchmark.
- **No annotations.** Spikes and dips need one-line explanations on the chart, not in a footnote.
- **Wrong chart for the structure.** Pie for trends, 3D effects, rainbow palettes: all misrepresent.
- **Inconsistent encoding.** Same metric, same name, same color, same time grain across every chart.
- **Decorative controls.** A chart-type toggle is fine if it works; a static "pretty" chart that answers nothing is a bug.
