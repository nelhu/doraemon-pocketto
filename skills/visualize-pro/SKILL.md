---
name: visualize-pro
description: Create and render polished, low-latency in-conversation visualizations, diagrams, charts, simulations, maps, interactive explainers, and UI mockups with the Visualize Pro MCP widget renderer. Use when the user asks to visualize, show, explore, compare, simulate, chart, map, or explain architecture, sequence, hierarchy, causality, quantitative trends, scenarios, spatial mechanisms, or adjustable inputs and a visual materially improves understanding. Do not use for standalone websites, app pages, components, or project UI changes.
---

# Visualize Pro

Turn an explanation or dataset into the smallest visual that makes its main relationship obvious. Keep the content truthful, the geometry intentional, and the surrounding chrome quiet.

## Optimize for first-render latency

Treat response time as a product requirement. For an ordinary chart, comparison, or repeated visual, target one file write, one blocking validation, and one renderer call. A simple or repeated visual should normally reach the renderer within 60 seconds.

Use this fast path by default:

1. Reuse the current task's existing fragment when the user asks to regenerate, revise, retry, or restyle the same visual. Patch its data or smallest necessary section; do not rebuild its layout.
2. For a new standard chart, write the smallest useful fragment, preferably below 12 KB and 300 lines. Do not add controls, summary cards, details tables, or decorative panels unless requested or essential to the comparison.
3. For a simulated front-end page-load waterfall, run `scripts/build_performance_waterfall.py <output.html>` instead of authoring the chart from scratch.
4. Run `scripts/validate_fragment.py` once, fix blocking errors if any, then call the renderer immediately.
5. Skip browser automation, screenshots, `view_image`, dark-mode sweeps, and multi-width interaction QA on the fast path. Use them only when the full-QA triggers below apply.
6. Do not search for the renderer when `visualizeProRenderer.render_widget_html` is already callable. If it is unavailable, discover it once, then call it.

Use full QA only for maps, 3D, Canvas, complex SVG connectors, multi-step interaction, external geometry, a validator warning that affects correctness, or an explicit QA request. Full QA may inspect 320 px and 736 px widths and the primary interaction.

## Decide the surface

When explicitly invoked, produce a visual unless the requested source data is unavailable. When invoked implicitly, use a visual only when it is materially clearer than concise prose or a small table.

Choose one surface:

- Use Mermaid for a simple static flow, sequence, tree, state graph, or dependency graph whose labeled nodes and edges are the whole story.
- Use Visualize Pro widget HTML for custom geometry, rich annotation, quantitative graphics, responsive composition, controls, simulation, or direct manipulation.
- Modify the user's project instead when the request is for a standalone website, product page, production component, or durable application UI.
- Use prose or a Markdown table when no important relationship becomes easier to understand visually.

Do not call or depend on the bundled `visualize` skill, its `::codex-inline-vis` directive, or its renderer assets. Build the result directly from this skill and render it with the `visualizeProRenderer` MCP server contributed by the Visualize Pro plugin.

## Load guidance progressively

The fast path is self-contained in this `SKILL.md`; do not read references for an ordinary chart or a repeated visual. Read only the reference needed for a complex or unfamiliar form:

- Complex architecture, flow, hierarchy, topology, timeline, or causal diagram: [references/svg-diagrams.md](references/svg-diagrams.md)
- Unfamiliar quantitative encoding or dense statistical chart: [references/charts.md](references/charts.md)
- Multi-step controls, simulation, scenario exploration, UI mockup, or 3D mechanism: [references/interactive-and-mockups.md](references/interactive-and-mockups.md)
- Geographic data: [references/maps.md](references/maps.md)
- Renderer debugging or contract changes: [references/renderer-contract.md](references/renderer-contract.md)
- Visual-system changes: [references/visual-language.md](references/visual-language.md)

Read [references/provenance.md](references/provenance.md) only when modifying this skill or auditing its origin and licensing boundary.

## Compose the visual

1. State the one relationship the visual must reveal: sequence, hierarchy, dependency, comparison, distribution, spatial mechanism, or adjustable cause and effect.
2. Choose the smallest composition that reveals it. Do not turn every fact into a panel.
3. Decide whether the result is a showpiece or an inline explainer:
   - A showpiece carries most of the answer and may use the full host width.
   - An inline explainer supports nearby prose and should be compact, transparent, and lightly framed.
4. Establish layout and geometry before decoration. Make labels, values, connectors, and states readable before adding stylistic detail.
5. Use color only to encode meaning, selection, or state. Keep neutral structure neutral.
6. Put only essential labels, values, legends, controls, and accessible descriptions inside the visual. Do not repeat the surrounding answer verbatim.
7. Preserve source meaning and uncertainty. Never invent metrics, statuses, boundaries, screens, or controls to make the visual look complete.

## Build widget HTML

Follow these requirements exactly:

- Write one ASCII kebab-case `.html` source file in a writable task-scoped directory so it can be validated and inspected.
- Write an HTML fragment only. Do not include `<!doctype>`, `<html>`, `<head>`, or `<body>`.
- Give the fragment one unique root `id` and scope every style and selector under it.
- Keep the fragment self-contained. Inline source data and final geometry; do not fetch remote data at runtime.
- Use Visualize Pro semantic variables with readable fallbacks. Do not copy Phoenix token names or hard-code a separate light/dark palette.
- Avoid `position: fixed`, viewport-sized roots, global CSS resets, iframes, and navigation that escapes the conversation.
- Let the fragment root follow its natural content height. Do not put a fixed height, clipping `max-height`, or `overflow-y: auto|scroll` on an inline widget root; nested scrolling makes the user choose between the conversation scrollbar and the widget scrollbar.
- Keep inline visuals compact enough to fit the host's reported `window.openai.maxHeight`. Shorten, responsively recompose, progressively disclose, or offer fullscreen for content that cannot remain readable within that bound.
- Do not add fragment-level host resize code. The Visualize Pro renderer owns a `ResizeObserver` and reports every initial or dynamic content-height change through `window.openai.notifyIntrinsicHeight(height)`.
- Make the first render useful without interaction. Controls should clarify the model, not conceal the answer.
- Keep the file below 2 MB. Use native HTML, CSS, SVG, Canvas, and JavaScript. Do not use CDNs or external runtime assets.
- Do not import code or assets from the bundled Visualize plugin.

## Validate before responding

On the fast path, rely on the validator for structural checks and inspect only the changed data/selector bindings. Do not perform visual QA unless a full-QA trigger applies.

Run the bundled read-only validator for every widget fragment:

```bash
python3 /absolute/path/to/visualize-pro/scripts/validate_fragment.py /absolute/path/to/visual.html
```

Treat validator errors as blocking. Resolve correctness warnings. Do not turn a successful validation into an automatic screenshot workflow.

## Respond

For Mermaid, return the fenced Mermaid block at the point where it best supports the answer.

For widget HTML, read the validated file and call the Visualize Pro renderer tool with:

- `title`: a concise reader-facing title
- `html`: the exact validated fragment

The tool call is the visual handoff. Do not emit `::codex-inline-vis`, `app_block`, raw HTML, or the default Visualize directive afterward. If the MCP widget is blocked by the Codex web sandbox, use the `localPreviewUrl` returned by the same tool call as the fallback and state that it opens the identical self-contained fragment through `127.0.0.1`.

## Dependencies

- Installed `visualize-pro` local plugin and its `visualizeProRenderer` MCP server
- Codex MCP App support for in-conversation rendering
- Node.js for the bundled MCP server
- Python 3 only for the skill-relative `scripts/validate_fragment.py`
- No CDN, remote font, copied bundled-Visualize asset, or Phoenix runtime
