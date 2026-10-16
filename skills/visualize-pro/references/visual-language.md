# Visual Language

## Start from the relationship

Name the relationship before choosing a form:

| Relationship | Strong default | Avoid by default |
| --- | --- | --- |
| Sequence or lifecycle | Horizontal/vertical flow, timeline, state path | Dashboard grid |
| Hierarchy or ownership | Tree, nested groups, indented structure | Unordered cards |
| Dependency or topology | Node-link diagram with explicit edge meaning | Decorative network hairball |
| Comparison | Aligned bars, dot plot, small multiples, comparison table | Unaligned cards with oversized totals |
| Distribution | Histogram, strip/dot plot, box plot | Pie chart |
| Part-to-whole | Stacked bar or one restrained donut for few categories | Many slices or 3D pie |
| Spatial mechanism | Annotated SVG or, only when essential, 3D | Generic isometric decoration |
| Adjustable cause and effect | A useful default state plus focused controls | Controls hiding an empty canvas |

If the content has no important visual relationship, answer with prose or a table.

## Content first, chrome recedes

- Give the visual one focal idea and one clear reading order.
- Establish hierarchy with alignment, grouping, spacing, weight, and scale before using color or containers.
- Leave breathing room around the focal content. Do not fill width merely because it is available.
- Use transparent or unframed composition for an inline explainer. Use a bounded surface only when it clarifies grouping or supports interaction.
- Use headings at sensible reading sizes; do not compensate for weak structure with oversized type.
- Prefer regular and medium weights. Reserve bold for one decisive label or value.

## Color and materials

- Keep architecture chrome, axes, connectors, inactive states, and supporting copy neutral.
- Use one accent family for focus and a small semantic set for success, warning, danger, or distinct data series.
- Keep the same meaning mapped to the same color across the entire visual.
- Use host semantic tokens and chart-series tokens with fallbacks. Do not build parallel light and dark palettes.
- Avoid neon glows, blue-purple AI gradients, glassmorphism, heavy shadows, rainbow series, and decorative color with no semantic role.
- Check contrast in both themes and never encode state with color alone.

## Showpiece versus inline explainer

A showpiece may use the full host width and carry most of the answer. It still needs one focal idea, disciplined labels, and responsive geometry.

An inline explainer should feel like part of the prose: compact, transparent, and low-chrome. It should clarify one relationship and leave supporting detail outside the visual.

## Responsive composition

- Design at the 736 px host width, then deliberately reflow at 320 px.
- Prefer wrapping or stacking secondary material below the primary visual instead of shrinking labels until unreadable.
- Keep touch targets around 40 px or larger where controls are expected.
- Avoid horizontal scrolling. If a dense comparison cannot reflow honestly, simplify or split it.

## Interaction and motion

- Make the primary state immediately legible.
- Use interaction to compare, inspect, or adjust—not to reveal basic content one click at a time.
- Keep controls close to the region they affect and label their consequence.
- Animate state transitions only when the transition teaches something. Keep motion short and respect reduced-motion settings.
- Provide an obvious selected state without excessive glow, elevation, or movement.

## Integrity checklist

- Trace every displayed fact to user input, a cited source, or a clearly labeled assumption.
- Preserve units, ordering, baselines, uncertainty, and missing values.
- Do not invent KPI cards, system statuses, exact boundaries, or UI screens.
- Remove any ornament that could be mistaken for data.
- If the visual simplifies a complex system, label the abstraction rather than presenting it as exhaustive.
