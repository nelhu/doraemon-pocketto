# SVG Diagrams

Use SVG for architecture, sequence, hierarchy, topology, causal, and spatial diagrams that need deterministic geometry.

## Pass the professional-diagram gate

SVG is only a rendering container. A set of rounded rectangles, headings, and group boundaries without visible relationships is a card gallery, not a professional technical diagram.

- Choose the diagram grammar before drawing: sequence, architecture, flowchart, state, call chain, dependency, topology, hierarchy, or causal graph.
- Encode the relationship with visible, directed, labeled connectors. Spatial proximity, shared color, and containment do not replace an edge.
- Use the grammar's standard semantics: participants, lifelines, and ordered messages for sequence; components, boundaries, and labeled flows for architecture; start, process, decision, end, and conditional edges for flowcharts; states and event-labeled transitions for state diagrams.
- Keep the main topology connected and remove orphan nodes. Do not add cards merely to fill space.
- A diagram with four or more node-like rectangles and zero relationship edges is a blocking failure even if its SVG, typography, and accessibility are otherwise valid.
- When another skill defines a typed diagram contract, preserve its node, edge, order, and boundary metadata in the final SVG.

## Establish the coordinate system

- Use one SVG with a stable `viewBox`. For a full-width Codex visual, a useful starting point is `0 0 680 H` with a 40-unit safe margin.
- Compute `H` from the lowest content edge plus the bottom safe margin. Do not guess height and patch clipping later.
- Define the grid before placing elements: columns, rows, node dimensions, gutters, group padding, and label widths.
- Keep geometry in SVG user units. Do not mix percentage coordinates with user-unit routing.
- Use `width: 100%; height: auto;` so the SVG scales within the host.

## Size labels before boxes

Estimate text width before assigning node width. As a starting approximation:

- Latin body text: `characters × font-size × 0.56`
- CJK body text: `characters × font-size × 1.0`
- Add at least 24–32 units of horizontal padding to the larger estimate.

Use explicit `<tspan>` lines when wrapping is required. Do not rely on unpredictable SVG text wrapping. Keep sibling nodes aligned and give long labels more width rather than smaller type.

## Route connectors deliberately

- Route connectors after nodes and group boundaries are final.
- Prefer orthogonal paths for architecture and process diagrams; use curves only when they communicate flow more clearly.
- Connect to the nearest sensible edge anchor, not the center of every box.
- Maintain a clear gap between line ends, arrowheads, and labels.
- Never route through text, controls, or node interiors.
- Use lanes or shared trunks for repeated directions, and keep siblings spaced consistently.
- Distinguish edge types with direct labels, restrained dash patterns, or marker shapes—not arbitrary colors alone.
- Put connectors behind nodes and labels. Define markers once in `<defs>` and reuse them.

## Structure groups

- Use a subtle boundary, title, and padding to show a real subsystem, trust boundary, ownership boundary, or lifecycle phase.
- Do not draw a box around every node. Group only when containment matters.
- Keep group titles aligned to the same grid and leave extra top padding for them.
- When two regions exchange data, label the crossing edge at the boundary.

## Accessibility

- Give the SVG a short `<title>` and a useful `<desc>` that states the reading order and main conclusion.
- Use direct text labels rather than hover-only tooltips.
- If the diagram is complex, include a concise semantic list or summary outside the SVG but inside the fragment.
- Ensure arrow meaning and state remain understandable without color.

## QA

At both wide and narrow widths, confirm that:

- No label or arrowhead is clipped.
- Connectors do not touch unrelated nodes or cross labels.
- Group boundaries do not look like nodes.
- Text remains readable after scaling.
- The main reading direction is apparent before the legend is consulted.
- The diagram still explains one relationship rather than becoming a miniature slide deck.

Complex technical diagrams with connectors always use the full-QA path. A generic fragment-validator pass is not sufficient: render at approximately 736 px and 320 px, inspect labels, node overlaps, connector crossings, arrow clipping, and reading direction, and fix every blocking issue before delivery.
