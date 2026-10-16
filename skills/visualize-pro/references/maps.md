# Maps

Use a map only when location or geographic shape is part of the question. For regional rankings without spatial meaning, use a sorted chart.

## Geometry and projection

- Use a published, attributable boundary dataset whose license permits the requested use.
- Never hand-draw or approximate political and administrative boundaries.
- Choose a projection appropriate to the displayed extent and use a projection library for nontrivial geography.
- Show enough surrounding context to orient the reader; do not crop a region so tightly that islands, neighbors, or disputed context disappear.
- Preserve the source dataset's boundary semantics and state its date or version when relevant.
- After projection, keep the final display geometry inline so the fragment does not fetch data at runtime.

## Encoding

- Use proportional symbols for counts at locations and choropleths for rates or normalized measures, not raw counts across unequal areas.
- Use a visible legend with units, domain, missing-data treatment, and source date.
- Keep boundary strokes neutral and subordinate to the data.
- Use a sequential scale for ordered magnitude and a diverging scale only around a meaningful midpoint.
- Mark missing or unavailable data distinctly from zero.

## Interaction and accessibility

- Make the default map understandable without hover.
- Keep hover/focus details inside the fragment and keyboard-accessible.
- Provide a ranked list or table alternative for exact values.
- Give the map a text summary of its main spatial pattern and any important coverage limitations.

## QA

- Verify the map imports and renders before responding; a blank projection is a blocking failure.
- Check full-region context, labels, legend, small islands or enclaves relevant to the question, and light/dark contrast.
- Do not claim disputed boundaries as authoritative; follow the user's source and identify it.
