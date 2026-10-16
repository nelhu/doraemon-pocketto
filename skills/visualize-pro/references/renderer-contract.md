# Visualize Pro Renderer Contract

Use this contract whenever the output surface is Visualize Pro widget HTML.

## Architecture boundary

The authoring skill and renderer plugin are separate:

```text
SKILL.md -> validated HTML fragment -> render_widget_html
         -> MCP App resource ui://visualize-pro/widget-v1.html
         -> inline widget
         -> 127.0.0.1 fallback URL
```

The renderer does not call the bundled `visualize` skill, emit
`::codex-inline-vis`, read bundled renderer assets, or load its `unpkg` shell.

## Fragment boundary

- Output a fragment, not a document: omit doctype, `html`, `head`, and `body`.
- Use one unique root `id`, for example `viz-request-lifecycle-7f3a`.
- Scope CSS under that root. Do not use broad selectors such as `*`, `body`,
  `svg`, `.card`, or `button` without the root prefix.
- Keep scripts inside the fragment and bind them to the unique root. Avoid
  globals; wrap code in an IIFE or module-like closure.
- Do not use iframes, embedded documents, `position: fixed`, `100vh`, or
  `100vw`.

## Theme and layout

Use these semantic variables with readable fallbacks:

```css
var(--background, transparent)
var(--foreground, #18181b)
var(--card, #ffffff)
var(--card-foreground, #18181b)
var(--muted, #f4f4f5)
var(--muted-foreground, #71717a)
var(--border, #e4e4e7)
var(--primary, #2563eb)
var(--primary-foreground, #ffffff)
var(--destructive, #dc2626)
var(--viz-series-1, #2563eb)
var(--viz-series-2, #16a34a)
var(--viz-series-3, #d97706)
var(--viz-series-4, #9333ea)
var(--viz-series-5, #0891b2)
var(--viz-series-6, #e11d48)
```

Treat the host width as fluid from roughly 320 px to 736 px. Use
`max-width: 100%`, responsive grids, wrapping controls, and SVG `viewBox`
instead of a fixed viewport canvas. Keep the root background transparent unless
a filled surface carries meaning.

## Intrinsic height and scrolling

The plugin-owned widget shell observes the mounted fragment and status region
with `ResizeObserver`. After the first render and every later size change, it
calls `window.openai.notifyIntrinsicHeight(height)` so the host can resize the
inline MCP App instead of adding an inner scrollbar.

- Let the fragment root use natural document flow. Do not set a fixed root
  height, a clipping `max-height`, or `overflow-y: auto|scroll`.
- Do not call `notifyIntrinsicHeight` from the fragment. Centralizing height
  reporting in the renderer avoids duplicate observers and competing values.
- The host may cap the requested height at `window.openai.maxHeight`.
  Responsively compact, progressively disclose, or offer fullscreen when a
  readable visual would exceed that bound; intrinsic-height reporting cannot
  override the host limit.
- The renderer hides iframe overflow only when `notifyIntrinsicHeight` is
  available. Unsupported hosts keep ordinary document overflow as a safe
  fallback instead of clipping content.

## Offline runtime

- Inline all data, styles, scripts, icons, and geometry.
- Do not use remote or relative runtime assets.
- Do not use `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`,
  `sendBeacon`, dynamic import, external scripts, external stylesheets, remote
  fonts, analytics, trackers, or ads.
- Data URLs and Blob URLs are allowed for generated images or downloads.
- Keep the fragment below 2 MB.

The MCP resource declares no external `connect`, `resource`, or `frame`
domains. The loopback fallback applies a matching offline CSP.

## Accessibility and behavior

- Give the root a concise accessible name or reference a visible heading with
  `aria-labelledby`.
- Use semantic buttons, inputs, labels, tables, and lists where they fit.
- Make controls keyboard operable and preserve visible focus.
- Provide SVG `title`/`desc`, chart summaries, units, and direct labels where
  applicable.
- Respect `prefers-reduced-motion`; do not require animation to understand the
  result.
- Make the initial state a complete explanation, not an empty loading shell.

## Renderer call

After validation, call the MCP tool with the exact fragment:

```json
{
  "title": "Request lifecycle",
  "html": "<section id=\"viz-request-lifecycle-7f3a\">...</section>"
}
```

The result contains:

- `structuredContent.html`: the fragment consumed by the plugin-owned widget
- `structuredContent.localPreviewUrl`: the loopback fallback
- `structuredContent.renderer`: `visualize-pro`

Do not emit a rendering directive after the tool call. If the inline widget
host reports an initialization error, present the returned loopback URL instead
of retrying through the bundled Visualize renderer.
