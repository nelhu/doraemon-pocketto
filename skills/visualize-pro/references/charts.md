# Charts

## Choose the encoding from the question

- Trend over time: line chart; use an area only when magnitude-to-zero matters.
- Compare categories: aligned horizontal or vertical bars, or a dot plot when differences are small.
- Distribution: histogram, strip/dot plot, or box plot.
- Correlation: scatter plot with clearly labeled axes; add a trend only if justified.
- Part-to-whole: stacked bar or one restrained donut for a few categories.
- Exact lookup: table, optionally paired with a small chart.

Do not select a chart because a library makes it easy. Select the encoding that makes the requested comparison easiest.

## Build the chart

- Use inline SVG for simple charts. Use a pinned allowlisted library only for complex scales, projections, interaction, or many marks.
- Start quantitative axes at zero when length encodes magnitude, unless a non-zero domain is necessary and clearly indicated.
- Show units in an axis title, subtitle, direct label, or value—not only in surrounding prose.
- Prefer direct series labels over distant legends when space allows.
- Keep series-to-color mapping stable across states and small multiples.
- Use grid lines sparingly and keep them visually behind the data.
- Preserve missing values and uncertainty rather than connecting or smoothing them away.
- Do not use 3D perspective, pictorial area, or animation that distorts magnitude.

## Use host colors safely

For SVG, use CSS variables in `fill` and `stroke` with fallbacks. For Canvas, read computed styles from the root and resolve each series token before drawing. Never pass an unresolved `var(...)` string to a Canvas API.

Ensure adjacent series differ by more than hue when overlap is likely: use direct labels, line patterns, marker shapes, or value annotations.

## Interaction

- Make the default state answer the main question.
- Use hover or focus details for secondary precision, not for the only visible value.
- When a control changes the dataset or domain, update marks, axes, labels, summaries, and accessible descriptions together.
- Keep tooltips within the fragment bounds and make the same information keyboard-accessible.

## Accessibility and integrity

- Give the chart a concise title and a text summary of the main pattern.
- Make data points or series reachable by keyboard when the interaction is essential.
- Provide an accessible table when exact values are central or numerous.
- Label sampled, estimated, normalized, cumulative, or incomplete data explicitly.
- Do not imply precision beyond the input data or silently aggregate categories.
